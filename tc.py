import grpc
import chat_pb2
import chat_pb2_grpc

class MyClient:
    async def connect(self):
        # Create a gRPC channel and stub
        self.channel = grpc.aio.insecure_channel('localhost:50051')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)

        try:
            # Streaming RPC, so we need to handle each message in a loop
            async for response in self.stub.Connect(
                chat_pb2.ConnectRequest(username='nat'),
                metadata=[('authorization', 'Bearer my_secret_token')]
            ):
                print(f"Received update: {response.message}")

        except grpc.RpcError as e:
            # Handle the error
            status_code = e.code()
            print(f"Error occurred: {status_code} - {e.details()}")
        finally:
            # Close the channel when done
            await self.channel.close()

# Run the client
import asyncio
client = MyClient()
asyncio.run(client.connect())
