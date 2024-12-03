import grpc
from concurrent import futures
import time
import t_pb2
import t_pb2_grpc

class GreeterServicer(t_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        for i in range(5):
            response = t_pb2.HelloResponse(message=f"Hello, {request.name}! Message {i+1}")
            # Gửi một stream response
            context.write(response)
            time.sleep(1)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    t_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Server running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
