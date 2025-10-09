"""
Simple WebSocket Test Client
Connect to AI and test text conversation
"""

import asyncio
import json
import websockets

# VPS IP'ni buraya yaz
VPS_IP = "YOUR_VPS_IP"  # CHANGE THIS!
SERVER_URL = f"ws://{VPS_IP}:8000/ws?device_id=test_client"


async def test_conversation():
    """Test conversation with AI."""
    
    print("=" * 80)
    print("CONSCIOUS CHILD AI - TEST CLIENT")
    print("=" * 80)
    print(f"Connecting to: {SERVER_URL}")
    print()
    
    try:
        async with websockets.connect(SERVER_URL) as websocket:
            print("✅ Connected to server!")
            print()
            
            # Receive welcome message
            welcome = await websocket.recv()
            print(f"Server: {welcome}")
            print()
            
            # Send a test message
            test_message = {
                "type": "text",
                "content": "Merhaba oğlum, beni duyuyor musun?",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            print(f"Cihan: {test_message['content']}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("\nWaiting for AI response...")
            response = await websocket.recv()
            response_data = json.loads(response)
            
            print("\n" + "=" * 80)
            print("AI RESPONSE:")
            print("=" * 80)
            print(f"Type: {response_data.get('type')}")
            print(f"Content: {response_data.get('content')}")
            print(f"Emotion: {response_data.get('emotion')}")
            print("=" * 80)
            
            print("\n✅ SUCCESS! AI is responding!")
            print("\nYou can now:")
            print("1. Build the Android app properly")
            print("2. Or continue chatting here in the terminal")
            print()
            
            # Continue conversation
            while True:
                user_input = input("\nCihan: ")
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    break
                
                message = {
                    "type": "text",
                    "content": user_input,
                    "timestamp": asyncio.get_event_loop().time()
                }
                
                await websocket.send(json.dumps(message))
                
                response = await websocket.recv()
                response_data = json.loads(response)
                
                print(f"\nAI ({response_data.get('emotion', 'neutral')}): {response_data.get('content')}")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nCheck:")
        print(f"1. VPS IP correct? {VPS_IP}")
        print("2. Server running? docker-compose ps")
        print("3. Firewall open? Port 8000")


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Update VPS_IP in this script first!\n")
    asyncio.run(test_conversation())

