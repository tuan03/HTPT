import asyncio
import grpc
import time
from concurrent import futures
import stream_pb2
import stream_pb2_grpc

myVar = None
class StreamService(stream_pb2_grpc.StreamServiceServicer):
    async def StreamData(self, request, context):
        global myVar
        try:
            
            myVar = context
            i = 0
            while True:
                i = i+1
                message = f"Message {i}"
                response = stream_pb2.DataResponse(message=message)
                await context.write(response)  # Gửi dữ liệu qua stream
                await asyncio.sleep(3)  # Giả lập độ trễ
        finally:
            myVar = None
            print("done")


async def main():
    while True:
        global myVar
        message = f"Đây là tin nhắn ngoài lề"
        response = stream_pb2.DataResponse(message=message)
        if myVar is not None:
            await myVar.write(response)
        await asyncio.sleep(5)
async def serve():
    server = grpc.aio.server()
    stream_pb2_grpc.add_StreamServiceServicer_to_server(StreamService(), server)
    listen_address = "[::]:50051"
    server.add_insecure_port(listen_address)
    print(f"Server is running on {listen_address}...")
    
    await server.start()
    await main()
    await server.wait_for_termination()
    


if __name__ == "__main__":
    # Chạy server asyncio
    asyncio.run(serve())
    

    