import asyncio
import grpc
from chat_pb2 import ChatUpdate, ChatMessage, ConnectRequest, GroupRequest, AddToGroupRequest, SeenRequest
import chat_pb2_grpc

class ChatClient:
    def __init__(self, username):
        self.username = username
        self.stub = None
        self.channel = None

    async def connect(self):
        # Tạo kết nối gRPC đến server
        self.channel = grpc.aio.insecure_channel('localhost:50051')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)

        # Kết nối và nhận cập nhật online users và messages
        async for update in self.stub.Connect(ConnectRequest(username=self.username)):
            self.handle_update(update)

    def handle_update(self, update: ChatUpdate):
        print(f"Online Users: {update.online_users}")
        print(f"Latest Messages: {update.messages}")

    async def send_message(self, message, group_id):
        # Gửi tin nhắn đến server
        chat_message = ChatMessage(
            username=self.username,
            message=message,
            group_id=group_id
        )
        await self.stub.SendMessage(chat_message)

    async def create_group(self, group_name):
        # Tạo nhóm mới
        group_request = GroupRequest(group_name=group_name, creator=self.username)
        response = await self.stub.CreateGroup(group_request)
        print(f"Group created with ID: {response.group_id}")
        return response.group_id

    async def add_to_group(self, group_id):
        # Thêm người dùng vào nhóm
        add_request = AddToGroupRequest(group_id=group_id, username=self.username)
        response = await self.stub.AddToGroup(add_request)
        print(f"Added to group: {response.group_name}")

    async def mark_as_seen(self, message_id):
        # Đánh dấu tin nhắn là đã xem
        seen_request = SeenRequest(message_id=message_id, username=self.username)
        await self.stub.MarkAsSeen(seen_request)

    async def run(self):
        # Chạy các thao tác của client
        await self.connect()
        group_id = await self.create_group("Test Group")
        await self.send_message("Hello, this is a test message!", group_id)
        await self.add_to_group(group_id)
        await self.send_message("Another message after adding to group.", group_id)

        # Giả sử bạn có một message_id để đánh dấu là đã xem
        # await self.mark_as_seen("some_message_id")

        # Dừng client sau khi làm xong
        await self.channel.close()

if __name__ == "__main__":
    username = input("Nhập tên")
    client = ChatClient(username)
    asyncio.run(client.run())
