import asyncio
from concurrent import futures
import grpc
import uuid
from datetime import datetime, timedelta
from chat_pb2 import (
    ChatUpdate, GroupResponse, SeenRequest
)
import chat_pb2
from google.protobuf.empty_pb2 import Empty
import chat_pb2_grpc
import jwt
from typing import Optional
from collections import defaultdict
import copy
import hashlib
import queue
# Secret key dùng để mã hóa và giải mã JWT
SECRET_KEY = "your_secret_key"
# Hàm xác thực JWT
def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["uid"]  # Trả về thông tin người dùng từ JWT
    except jwt.InvalidTokenError:
        return "Invalid token"

# context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Sai thông tin đăng nhập")
# context.abort(grpc.StatusCode.UNAUTHENTICATED, "Chưa đăng nhập người dùng")
# context.abort(grpc.StatusCode.PERMISSION_DENIED, "Không có quyền truy cập")

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.online_users = {}
        self.users = [
                        {'id': 1, 'username': 'u1', 'password': 'p1', 'fullname': 'Nguyễn Anh Tuấn'},
                        {'id': 2, 'username': 'u2', 'password': 'p2', 'fullname': 'Hoàng Minh Tâm'},
                        {'id': 3, 'username': 'lanhuong9', 'password': 'mypassword', 'fullname': 'Lân Hương Nguyễn'},
                        {'id': 4, 'username': 'thanhson1', 'password': 'thanhson2024', 'fullname': 'Thành Sơn Lê'},
                        {'id': 5, 'username': 'tuananh88', 'password': 'tuananhpass', 'fullname': 'Tuấn Anh Lê'},
                        {'id': 6, 'username': 'quanghieu4', 'password': 'quanghieu789', 'fullname': 'Quang Hiếu Đoàn'},
                        {'id': 7, 'username': 'xuantruong5', 'password': 'xuantruong01', 'fullname': 'Xuân Trường Phan'},
                        {'id': 8, 'username': 'nguyentuan6', 'password': 'nguyentuan123', 'fullname': 'Nguyễn Tuấn Anh'},
                        {'id': 9, 'username': 'hoangkim2', 'password': 'hoangkim123', 'fullname': 'Hoàng Kim Cương'},
                        {'id': 10, 'username': 'phuongly10', 'password': 'phuongly987', 'fullname': 'Phương Ly Trần'}
                    ]

        self.groups = [
            {
                "group_id": 1,
                "title": "Nhóm học tập",
                "members": [1, 2, 3, 4],
                "messages": [
                    {'message_id': 1, 'sender_id': 1, 'message': 'Chào mọi người!', 'time': '2024-12-01T10:00:00', 'isRead': True},
                    {'message_id': 2, 'sender_id': 2, 'message': 'Chào bạn, có gì mới không?', 'time': '2024-12-01T10:05:00', 'isRead': False},
                    {'message_id': 3, 'sender_id': 3, 'message': 'Cần giúp đỡ gì không?', 'time': '2024-12-01T10:10:00', 'isRead': False}
                ]
            },
            {
                "group_id": 2,
                "title": "Nhóm du lịch",
                "members": [2, 3, 5, 6],
                "messages": [
                    {'message_id': 4, 'sender_id': 2, 'message': 'Ai muốn đi du lịch cuối tuần không?', 'time': '2024-12-01T11:00:00', 'isRead': True},
                    {'message_id': 5, 'sender_id': 5, 'message': 'Mình đi nhé! Đến đâu?', 'time': '2024-12-01T11:05:00', 'isRead': True},
                    {'message_id': 6, 'sender_id': 6, 'message': 'Đi đâu cũng được, mình theo các bạn!', 'time': '2024-12-01T11:10:00', 'isRead': False}
                ]
            },
            {
                "group_id": 3,
                "title": "Nhóm công việc",
                "members": [1, 4, 7, 8],
                "messages": [
                    {'message_id': 7, 'sender_id': 1, 'message': 'Họp vào ngày mai nhé!', 'time': '2024-12-02T09:00:00', 'isRead': True},
                    {'message_id': 8, 'sender_id': 4, 'message': 'Chắc được rồi, giờ nào?', 'time': '2024-12-02T09:05:00', 'isRead': True},
                    {'message_id': 9, 'sender_id': 7, 'message': 'Họp vào sáng mai, ổn không?', 'time': '2024-12-02T09:10:00', 'isRead': False}
                ]
            }
        ]

        self.messages_by_user = [
                    {'message_id': 20, 'sender_id': 1, 'receiver_id': 2, 'message': 'Message 20', 'time': '2024-12-02', 'isRead': True},
                    {'message_id': 21, 'sender_id': 2, 'receiver_id': 1, 'message': 'Message 21', 'time': '2024-12-03', 'isRead': True},
                    {'message_id': 22, 'sender_id': 1, 'receiver_id': 2, 'message': 'Message 23', 'time': '2024-12-02', 'isRead': True},
                ]
        self.MainQueue = {}
    def Login(self, request, context):
        username = request.username
        password = request.password
        user = next((user for user in self.users if user['username'] == username and user['password'] == password), None)
        print(user)
        if user:
            payload = {
                "uid": user['id']
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return chat_pb2.LoginResponse(
                success=True,
                message="Đăng nhập thành công",
                token=token
            )
        else:
            return chat_pb2.LoginResponse(
                success=False,
                message="Sai tài khoản hoặc mật khẩu",
                token=""
            )

    async def authen(self, context):
        metadata = dict(context.invocation_metadata())
        token = metadata.get('authorization', None)
        
        # Extract the token if available
        if token:
            return verify_jwt(token)
        else:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Chưa đăng nhập người dùng")
    def get_recent_user_inbox(self,user_id, messages):
        latest_messages = defaultdict(lambda: None)
        for message in messages:
            if message['sender_id'] == user_id or message['receiver_id'] == user_id:
                key = tuple(sorted([message['sender_id'], message['receiver_id']]))
                if latest_messages[key] is None or latest_messages[key]['time'] < message['time']:
                    latest_messages[key] = message
        result = []
        latest_messages = copy.deepcopy(latest_messages)
        for message in latest_messages.values():
            if message['sender_id'] == user_id:
                message['isMe'] = True  # Nếu người gửi là người dùng
            else:
                message['isMe'] = False  # Nếu người nhận là người dùng
            if message['sender_id'] == user_id:
                cob = next(user for user in self.users if user['id'] == message['receiver_id'])
                message['col'] = cob if cob else {}
            else:
                cob = next(user for user in self.users if user['id'] == message['sender_id'])
                message['col'] = cob if cob else {}
            sender_id = message.pop('sender_id', None)
            receiver_id = message.pop('receiver_id', None)
            result.append(message)
        return result
    def get_user_groups(self,user_id, groups):#[{'group_id': 1, 'title': 'Nhóm học tập', 'last_message': {'message_id': 3, 'sender_id': 3, 'message': 'Cần giúp đỡ gì không?', 'time': '2025-12-01T10:10:00', 'isRead': False}}]
        # Danh sách các nhóm mà người dùng tham gia
        user_groups = []

        for group in groups:
            if user_id in group["members"]:
                # Lấy tin nhắn mới nhất trong nhóm
                latest_message = max(group['messages'], key=lambda msg: datetime.fromisoformat(msg['time']))
                user_groups.append({
                    "group_id": group["group_id"],
                    "title": group["title"],
                    "last_message": latest_message
                })

        # Sắp xếp nhóm theo thời gian của tin nhắn mới nhất
        user_groups.sort(key=lambda group: datetime.fromisoformat(group["last_message"]['time']), reverse=True)

        return user_groups
    def get_messages(self,user_id, they_id, messages):
        result = []
        messages = copy.deepcopy(messages)
        messages = [mess for mess in messages if (mess['sender_id'] == user_id and mess['receiver_id'] == they_id) or (mess['sender_id'] == they_id and mess['receiver_id'] == user_id)]
        for message in messages:
            if message['sender_id'] == user_id:
                message['isMe'] = True
            else:
                message['isMe'] = False 

            cob = next(user for user in self.users if user['id'] == message['sender_id'])
            message['sender'] = cob if cob else {}
            sender_id = message.pop('sender_id', None)
            receiver_id = message.pop('receiver_id', None)
            result.append(message)
        return result
    async def Connect(self, request, context):
        uid = await self.authen(context)
        self.online_users[uid] = queue.Queue()
        while True:
                await asyncio.sleep(1)
                update = ChatUpdate(
                    online_users=list([user for user in self.users if user['id'] in self.online_users and user['id'] != uid]),
                    recent_user_inbox=self.get_recent_user_inbox(uid,self.messages_by_user),
                    groupmess = self.get_user_groups(uid,self.groups)
                )
                yield update
        if uid in self.online_users :
            del self.online_users[uid]
        return
    def create_room_id(self,user_id1, user_id2):
        try:
            if user_id1 > user_id2:
                user_id1, user_id2 = user_id2, user_id1
            # Ghép hai ID lại và tạo băm
            combined_id = f"{user_id1}_{user_id2}"
            print(combined_id)
            return hashlib.sha256(combined_id.encode()).hexdigest()
        except Exception as e:
            print(e)
    def get_group_messages(self,group_id):
        # Tìm nhóm có group_id = 1
        for group in self.groups:
            if group['group_id'] == group_id:
                for message in group['messages']:
                    cob = next(user for user in self.users if user['id'] == message['sender_id'])
                    message['sender'] = cob if cob else {}
                    sender_id = message.pop('sender_id', None)
                return group['messages']
        return []
    async def JoinRoomChat(self, request, context):
        try:
            idRoom = request.idRoom
            idUser = await self.authen(context)
            idHash = None
            typeM = idRoom[0]
            messList = None
            if 'p' in idRoom:
                idHash = self.create_room_id(int(idUser),int(idRoom[1:]))
                messList  = list(self.get_messages(idUser,int(idRoom[1:]),self.messages_by_user))
            else:
                idHash = self.create_room_id(int(-1),int(idRoom[1:]))
                messList = self.get_group_messages(int(idRoom[1:]))
            print(messList)
            if idHash not in self.MainQueue:
                self.MainQueue[idHash] = queue.Queue()
            self.MainQueue[idHash].put(self.online_users[idUser])

            
            yield chat_pb2.DataRoom(
                        id = int(idRoom[1:]),
                        typeM = typeM,
                        messList=messList,
                    )

            while True:
                    await asyncio.sleep(1)
                    yield chat_pb2.DataRoom(
                        id = int(idRoom[1:]),
                        typeM = typeM,
                        messList=None,
                    )
            return
        except Exception as e:
            print(e)

    async def SendMessage(self, request, context):
        if request.HasField("receiver_id"):
            receiver_id = request.receiver_id
            print(f"Receiver ID: {receiver_id}")
        elif request.HasField("group_id"):
            group_id = request.group_id
            print(f"Group ID: {group_id}")
        else:
            print("No receiver or group ID specified")

        return Empty()

    async def MarkAsSeen(self, request, context):
        for message in self.messages:
            if message.message_id == request.message_id:
                if request.username not in message.seen_by:
                    message.seen_by.append(request.username)
                break
        return Empty()

    async def CreateGroup(self, request, context):
        group_id = str(uuid.uuid4())
        self.groups[group_id] = {
            "name": request.group_name,
            "members": {request.creator}
        }
        return GroupResponse(group_id=group_id, group_name=request.group_name, members=list(self.groups[group_id]["members"]))

    async def AddToGroup(self, request, context):
        group = self.groups.get(request.group_id)
        if group:
            group["members"].add(request.username)
        return GroupResponse(group_id=request.group_id, group_name=group["name"], members=list(group["members"]))

async def serve():
    server = grpc.aio.server()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
