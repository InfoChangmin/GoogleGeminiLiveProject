## pip install google-genai==0.3.0
# 파이썬 서버측 코드

import asyncio
import json
import os
import websockets
from google import genai
import base64

# Load API key from environment
os.environ['GOOGLE_API_KEY'] = 'YOUR API KEY' # 자신의 키로 교체하세요!
MODEL = "gemini-2.0-flash-exp"  # use your model ID

client = genai.Client(
    http_options={
        'api_version': 'v1alpha',
    }
)


# 조명값을 조절하는 함수
def set_light_values(brightness, color_temp):
    return {
        "brightness": brightness,
        "colorTemperature": color_temp,
    }

# 팬 속도를 조절하는 함수
def set_fan_values(speed):
    return {
        "speed": speed,
    }

# 도구로 활용(구성 함수 호출)
# https://ai.google.dev/gemini-api/docs/function-calling?hl=ko
tool_set_light_values = {
    "function_declarations": [
        {
            "name": "set_light_values",
            "description": "Set the brightness and color temperature of a room light.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "brightness": {
                        "type": "NUMBER",
                        "description": "Light level from 0 to 100. Zero is off and 100 is full brightness"
                    },
                    "color_temp": {
                        "type": "STRING",
                        "description": "Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`."
                    }
                },
                "required": ["brightness", "color_temp"]
            }
        }
    ]
}

tool_set_fan_values = {
    "function_declarations": [
        {
            "name": "set_fan_values",
            "description": "방 안의 선풍기 세기를 조정하세요!.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "speed": {
                        "type": "NUMBER",
                        "description": "0~100까지의 빠르기 값을 설정할 수 있어. 0을 선택하면 끄는거고 100을 하면 최고 속력이야."
                    }
                },
                "required": ["speed"]
            }
        }
    ]
}

# 웹 소켓 핸들러
async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
    """Handles the interaction with Gemini API within a websocket session.

    Args:
        client_websocket: The websocket connection to the client.
    """
    try:
        config_message = await client_websocket.recv()
        config_data = json.loads(config_message)
        config = config_data.get("setup", {})

        config["tools"] = [tool_set_light_values, tool_set_fan_values] # 제미나이한테 할수 있는 도구 추가

        # 세션 연결
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            print("Connected to Gemini API")

            # 클라이언트로부터 사진, 음성을 받아서 gemini로 전달
            async def send_to_gemini():
                """Sends messages from the client websocket to the Gemini API."""
                try:
                    async for message in client_websocket:
                        try:
                            data = json.loads(message)
                            if "realtime_input" in data:
                                for chunk in data["realtime_input"]["media_chunks"]:
                                    if chunk["mime_type"] == "audio/pcm":
                                        await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})

                                    elif chunk["mime_type"] == "image/jpeg":
                                        await session.send({"mime_type": "image/jpeg", "data": chunk["data"]})

                        except Exception as e:
                            print(f"Error sending to Gemini: {e}")
                    print("Client connection closed (send)")
                except Exception as e:
                    print(f"Error sending to Gemini: {e}")
                finally:
                    print("send_to_gemini closed")

            async def receive_from_gemini():
                """Receives responses from the Gemini API and forwards them to the client, looping until turn is complete."""
                try:
                    while True:
                        try:
                            print("receiving from gemini")
                            async for response in session.receive():
                                # first_response = True
                                # print(f"response: {response}")
                                if response.server_content is None:
                                    if response.tool_call is not None:
                                        # handle the tool call
                                        print(f"Tool call received: {response.tool_call}")

                                        function_calls = response.tool_call.function_calls
                                        function_responses = []

                                        for function_call in function_calls:
                                            name = function_call.name
                                            args = function_call.args
                                            # Extract the numeric part from Gemini's function call ID
                                            call_id = function_call.id

                                            # set light values가 들어올 경우 밝기와 컬러맵 인자를 전달
                                            if name == "set_light_values":
                                                try:
                                                    result = set_light_values(int(args["brightness"]),
                                                                              args["color_temp"])
                                                    function_responses.append(
                                                        {
                                                            "name": name,
                                                            # "response": {"result": "The light is broken."},
                                                            "response": {"result": result},
                                                            "id": call_id
                                                        }
                                                    )
                                                    await client_websocket.send(
                                                        json.dumps({"text": json.dumps(function_responses)}))
                                                    print("Function executed")
                                                except Exception as e:
                                                    print(f"Error executing function: {e}")
                                                    continue

                                            elif name == "set_fan_values":
                                                try:
                                                    result = set_fan_values(int(args["speed"]))
                                                    function_responses.append(
                                                        {
                                                            "name": name,
                                                            # "response": {"result": "The light is broken."},
                                                            "response": {"result": result},
                                                            "id": call_id
                                                        }
                                                    )
                                                    await client_websocket.send(
                                                        json.dumps({"text": json.dumps(function_responses)}))
                                                    print("Function executed")
                                                except Exception as e:
                                                    print(f"Error executing function: {e}")
                                                    continue

                                        # Send function response back to Gemini
                                        print(f"function_responses: {function_responses}")
                                        await session.send(function_responses)
                                        continue

                                    # print(f'Unhandled server message! - {response}')
                                    # continue

                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        # print(f"part: {part}")
                                        if hasattr(part, 'text') and part.text is not None:
                                            # print(f"text: {part.text}")
                                            await client_websocket.send(json.dumps({"text": part.text}))
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                            # if first_response:
                                            # print("audio mime_type:", part.inline_data.mime_type)
                                            # first_response = False
                                            base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                            await client_websocket.send(json.dumps({
                                                "audio": base64_audio,
                                            }))
                                            print("audio received")

                                if response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                        except websockets.exceptions.ConnectionClosedOK:
                            print("Client connection closed normally (receive)")
                            break  # Exit the loop if the connection is closed
                        except Exception as e:
                            print(f"Error receiving from Gemini: {e}")
                            break  # exit the lo

                except Exception as e:
                    print(f"Error receiving from Gemini: {e}")
                finally:
                    print("Gemini connection closed (receive)")

            # Start send loop
            send_task = asyncio.create_task(send_to_gemini())
            # Launch receive loop as a background task
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)


    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        print("Gemini session closed.")


async def main() -> None:
    async with websockets.serve(gemini_session_handler, "localhost", 9082):
        print("Running websocket server localhost:9082...")
        await asyncio.Future()  # Keep the server running indefinitely


if __name__ == "__main__":
    asyncio.run(main())