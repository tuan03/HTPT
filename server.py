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
        self.room_users = {}
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
                    {'message_id': 17, 'sender_id': 1, 'receiver_id': 2, 'message': 'Message 20', 'time': '2024-12-04 07:10:57.626571', 'isRead': True}
        ]
        self.Room = {}
    def Login(self, request, context):
        username = request.username
        password = request.password
        user = next((user for user in self.users if user['username'] == username and user['password'] == password), None)
        if user:
            payload = {
                "uid": user['id']
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return chat_pb2.LoginResponse(
                success=True,
                message="Đăng nhập thành công",
                token=token,
                uid = user['id']
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
    def get_recent_user_inbox(self,user_id):
        messages = self.messages_by_user
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
        try :
            self.online_users[uid] = context
            print("kkk",self.get_user_groups(uid,self.groups))
            while True:
                    await asyncio.sleep(1)
                    update = ChatUpdate(
                        online_users=list([user for user in self.users if user['id'] in self.online_users and user['id'] != uid]),
                        recent_user_inbox=self.get_recent_user_inbox(uid),
                        groupmess = self.get_user_groups(uid,self.groups)
                    )
                    yield update
        except Exception as e:
            print(e)
        finally:
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
        for group in self.groups:
            if group['group_id'] == group_id:
                result = []
                for message in group['messages']:
                    pmess = copy.deepcopy(message)
                    cob = next(user for user in self.users if user['id'] == pmess['sender_id'])
                    pmess['sender'] = cob if cob else {}
                    sender_id = pmess.pop('sender_id', None)
                    result.append(pmess)
                return result
        return []
    async def JoinRoomChat(self, request, context):
        idRoom = request.idRoom
        idUser = await self.authen(context)
        idHash = None
        typeM = idRoom[0]
        messList = None
        try:
            if 'p' in idRoom:
                idHash = self.create_room_id(int(idUser),int(idRoom[1:]))
                messList  = list(self.get_messages(idUser,int(idRoom[1:]),self.messages_by_user))
            else:
                idHash = self.create_room_id(int(-1),int(idRoom[1:]))
                messList = self.get_group_messages(int(idRoom[1:]))
                print(messList)
            if idHash not in self.Room:
                self.Room[idHash] = {}
            if idUser not in self.room_users:
                self.room_users[idUser] = idHash
            else:
                if idUser in self.Room[self.room_users[idUser]]:
                    del self.Room[self.room_users[idUser]][idUser]
                self.room_users[idUser] = idHash
            self.Room[idHash][idUser] = context
 
            print("tick1",self.Room[idHash])
            yield chat_pb2.DataRoom(
                        id = int(idRoom[1:]),
                        typeM = typeM,
                        messList=messList
                    )

            while True:
                    await asyncio.sleep(1)
                    yield chat_pb2.DataRoom(
                        id = int(idRoom[1:]),
                        typeM = typeM,
                        messList=None,
                        newMess=None
                    )
            return
        except Exception as e:
            print(e)
        finally:
            if idUser in self.Room[idHash]:
                del self.Room[idHash][idUser]
                print("Đã đóng connect trước")
                print("tick2",self.Room[idHash])
    def add_message(self, mess, sender, receiver):
        # Tạo một ID mới cho tin nhắn
        new_message_id = max([msg['message_id'] for msg in self.messages_by_user]) + 1
        
        # Lấy thời gian hiện tại
        current_time = str(datetime.now())
        # Tạo tin nhắn mới
        new_message = {
            'message_id': new_message_id,
            'sender_id': sender,
            'receiver_id': receiver,
            'message': mess,
            'time': current_time,
            'isRead': False,  # Mặc định là chưa đọc
        }    
        # Thêm tin nhắn mới vào danh sách
        self.messages_by_user.append(new_message)
        pmess = copy.deepcopy(new_message)
        cob = next(user for user in self.users if user['id'] == sender)
        pmess['sender'] = cob if cob else {}
        sender_id = pmess.pop('sender_id', None)
        receiver = pmess.pop('receiver_id', None)
        return pmess
    def add_message_to_group(self,group_id, sender_id, message):
        # Tìm nhóm theo group_id
        group = next((g for g in self.groups if g['group_id'] == group_id), None)
        
        if group:
            # Tạo message_id mới (số ID tin nhắn tiếp theo trong nhóm)
            new_message_id = max([msg['message_id'] for msg in group['messages']], default=0) + 1
            
            # Lấy thời gian hiện tại
            from datetime import datetime
            current_time = str(datetime.now())
            
            # Thêm tin nhắn vào nhóm
            new_message = {
                'message_id': new_message_id,
                'sender_id': sender_id,
                'message': message,
                'time': current_time,
                'isRead': False  # Tin nhắn mới mặc định là chưa đọc
            }
            
            group['messages'].append(new_message)
            pmess = copy.deepcopy(new_message)
            cob = next((user for user in self.users if user['id'] == sender_id), {})
            pmess['sender'] = cob if cob else {}
            sender_id = pmess.pop('sender_id', None)
            return pmess
        else:
            return None
    async def SendMessage(self, request, context):
        uid = await self.authen(context)
        try:
            # print("tick:",request.message)
            if request.HasField("receiver_id"):
                receiver_id = request.receiver_id
                roomHash = self.create_room_id(uid,receiver_id)
                newMess = self.add_message(request.message,uid,receiver_id)
                for i in self.Room[roomHash]:
                    await self.Room[roomHash][i].write(chat_pb2.DataRoom(
                        id = int(receiver_id),
                        typeM = 'p',
                        newMess=newMess
                    ))
            elif request.HasField("group_id"):
                group_id = request.group_id
                roomHash = self.create_room_id(int(-1),int(group_id))
                newMess = self.add_message_to_group(group_id,uid,request.message)
                for i in self.Room[roomHash]:
                    await self.Room[roomHash][i].write(chat_pb2.DataRoom(
                        id = int(group_id),
                        typeM = 'g',
                        newMess=newMess
                    ))
            else:
                print("No receiver or group ID specified")

            return Empty()
        except Exception as e:
            print(e)

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
