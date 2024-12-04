import grpc
import stream_pb2
import stream_pb2_grpc


def run():
    # Kết nối tới server
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = stream_pb2_grpc.StreamServiceStub(channel)

        # Gọi StreamData và nhận dữ liệu stream từ server
        responses = stub.StreamData(stream_pb2.Empty())
        try:
            for response in responses:
                print(f"Received: {response.message}")
        except grpc.RpcError as e:
            print(f"Stream error: {e}")


if __name__ == "__main__":
    run()
