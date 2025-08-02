import asyncio
import base64
import json
import websockets
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

from pizza_functions import FUNCTION_MAP

# Conversation state tracking
conversation_state = {
    "order_placed": False,
    "call_should_end": False,
    "grace_period_start": None
}

def sts_connect():
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        raise Exception("DEEPGRAM_API_KEY not found")
    
    sts_ws = websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        subprotocols=["token", api_key]
    )

    return sts_ws


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def end_twilio_call(call_sid):
    """End a Twilio call using the REST API."""
    try:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("Warning: Twilio credentials not found. Cannot end call programmatically.")
            return False
            
        client = Client(account_sid, auth_token)
        call = client.calls(call_sid).update(status='completed')
        print(f"Call {call_sid} ended successfully")
        return True
    except Exception as e:
        print(f"Error ending call {call_sid}: {e}")
        return False
    

async def handle_barge_in(decoded, twilio_ws, streamsid):
    if decoded["type"] == "UserStartedSpeaking":
        clear_message = {
            "event": "clear",
            "streamSid": streamsid
        }
        await twilio_ws.send(json.dumps(clear_message))


def execute_function_call(func_name, arguments):
    global conversation_state
    
    if func_name in FUNCTION_MAP:
        result = FUNCTION_MAP[func_name](**arguments)
        print(f"Function call result: {result}")
        
        # Check if an order was successfully placed
        if func_name == "place_pizza_order" and "order_id" in result:
            conversation_state["order_placed"] = True
            conversation_state["grace_period_start"] = asyncio.get_event_loop().time()
            print("Order placed successfully - starting grace period for call termination")
        
        return result
    else:
        result = {"error": f"Unknown function: {func_name}"}
        print(result)
        return result
    

def create_function_call_response(func_id, func_name, result):
    return {
        "type": "FunctionCallResponse",
        "id": func_id,
        "name": func_name,
        "content": json.dumps(result)
    }


async def handle_function_call_request(decoded, sts_ws):
    try:
        for function_call in decoded["functions"]:
            func_name = function_call["name"]
            func_id = function_call["id"]
            arguments = json.loads(function_call["arguments"])

            print(f"Function call: {func_name} (ID: {func_id}), arguments: {arguments}")
    
            result = execute_function_call(func_name, arguments)

            function_result = create_function_call_response(func_id, func_name, result)
            await sts_ws.send(json.dumps(function_result))
            print(f"Sent function result: {function_result}")

    except Exception as e:
        print(f"Error calling function: {e}")
        error_result = create_function_call_response(
            func_id if "func_id" in locals() else "unknown",
            func_name if "func_name" in locals() else "unknown",
            {"error": f"Function call failed with: {str(e)}"}
        )
        await sts_ws.send(json.dumps(error_result))


async def handle_text_message(decoded, twilio_ws, sts_ws, streamsid):
    await handle_barge_in(decoded, twilio_ws, streamsid)

    if decoded["type"] == "FunctionCallRequest":
        await handle_function_call_request(decoded, sts_ws)

async def sts_sender(sts_ws, audio_queue):
    print("sts_sender started")
    while True:
        chunk = await audio_queue.get()
        await sts_ws.send(chunk)


async def call_monitor(call_info_queue, twilio_ws):
    """Monitor conversation state and handle call termination."""
    global conversation_state
    
    # Wait for call info
    call_info = await call_info_queue.get()
    call_sid = call_info["call_sid"]
    
    GRACE_PERIOD = 30  # 30 seconds after order completion
    
    while True:
        await asyncio.sleep(1)  # Check every second
        
        if conversation_state["order_placed"] and conversation_state["grace_period_start"]:
            current_time = asyncio.get_event_loop().time()
            elapsed = current_time - conversation_state["grace_period_start"]
            
            if elapsed >= GRACE_PERIOD and not conversation_state["call_should_end"]:
                print("Grace period expired. Ending call.")
                conversation_state["call_should_end"] = True
                
                # End the call
                if end_twilio_call(call_sid):
                    break
                else:
                    # Fallback: close WebSocket if REST API fails
                    await twilio_ws.close()
                    break


async def sts_receiver(sts_ws, twilio_ws, streamsid_queue):
    print("sts_receiver started")
    streamsid = await streamsid_queue.get()

    async for message in sts_ws:
        if type(message) is str:
            print(message)
            decoded = json.loads(message)
            await handle_text_message(decoded, twilio_ws, sts_ws, streamsid)
            continue

        raw_mulaw = message

        media_message = {
            "event": "media",
            "streamSid": streamsid,
            "media": {"payload": base64.b64encode(raw_mulaw).decode("ascii")}
        }

        await twilio_ws.send(json.dumps(media_message))


async def twilio_receiver(twilio_ws, audio_queue, streamsid_queue, call_info_queue):
    BUFFER_SIZE = 20 * 160
    inbuffer = bytearray(b"")

    async for message in twilio_ws:
        try:
            data = json.loads(message)
            event = data["event"]

            if event == "start":
                print("Get our streamsid")
                start = data["start"]
                streamsid = start["streamSid"]
                call_sid = start["callSid"]
                streamsid_queue.put_nowait(streamsid)
                call_info_queue.put_nowait({"call_sid": call_sid, "stream_sid": streamsid})
                print(f"Call SID: {call_sid}, Stream SID: {streamsid}")
            elif event == "connected":
                continue
            elif event == "media":
                media = data["media"]
                chunk = base64.b64decode(media["payload"])
                if media["track"] == "inbound":
                    inbuffer.extend(chunk)
            elif event == "stop":
                break

            while len(inbuffer) >= BUFFER_SIZE:
                chunk = inbuffer[:BUFFER_SIZE]
                audio_queue.put_nowait(chunk)
                inbuffer = inbuffer[BUFFER_SIZE:]
        except:
            break

async def twilio_handler(twilio_ws):
    global conversation_state
    
    # Reset conversation state for new call
    conversation_state = {
        "order_placed": False,
        "call_should_end": False,
        "grace_period_start": None
    }
    
    audio_queue = asyncio.Queue()
    streamsid_queue = asyncio.Queue()
    call_info_queue = asyncio.Queue()

    async with sts_connect() as sts_ws:
        config_message = load_config()
        await sts_ws.send(json.dumps(config_message))

        await asyncio.wait(
            [
                asyncio.ensure_future(sts_sender(sts_ws, audio_queue)),
                asyncio.ensure_future(sts_receiver(sts_ws, twilio_ws, streamsid_queue)),
                asyncio.ensure_future(twilio_receiver(twilio_ws, audio_queue, streamsid_queue, call_info_queue)),
                asyncio.ensure_future(call_monitor(call_info_queue, twilio_ws))
            ]
        )

        await twilio_ws.close()


async def main():
    await websockets.serve(twilio_handler, "localhost", 5000)
    print("Started server.")
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())