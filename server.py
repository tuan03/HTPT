import asyncio
from concurrent import futures
import grpc
import uuid
from datetime import datetime, timedelta
from chat_pb2 import (
    ChatUpdate
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

import logging

# Cấu hình logging
logging.basicConfig(
    filename='LOG.txt',   # Đường dẫn tới file log
    level=logging.INFO,    # Mức độ log (INFO sẽ ghi mọi thông tin quan trọng)
    format='%(asctime)s - %(message)s'  # Định dạng log bao gồm thời gian
)
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
        self.tick_time_userOfftine = {}
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
                    {'message_id': 1, 'sender_id': 1, 'message': 'Chào mọi người!', 'time': '2024-12-01 10:00:00.626571'},
                    {'message_id': 2, 'sender_id': 2, 'message': 'Chào bạn, có gì mới không?', 'time': '2024-12-01 10:05:00.626571'},
                    {'message_id': 3, 'sender_id': 3, 'message': 'Cần giúp đỡ gì không?', 'time': '2024-12-01 10:10:00.626571'}
                ]
            },
            {
                "group_id": 2,
                "title": "Nhóm du lịch",
                "members": [2, 3, 5, 6],
                "messages": [
                    {'message_id': 4, 'sender_id': 2, 'message': 'Ai muốn đi du lịch cuối tuần không?', 'time': '2024-12-01 11:00:00.626571'},
                    {'message_id': 5, 'sender_id': 5, 'message': 'Mình đi nhé! Đến đâu?', 'time': '2024-12-01 11:05:00.626571'},
                    {'message_id': 6, 'sender_id': 6, 'message': 'Đi đâu cũng được, mình theo các bạn!', 'time': '2024-12-01 11:10:00.626571'}
                ]
            },
            {
                "group_id": 3,
                "title": "Nhóm công việc",
                "members": [1, 4, 7, 8],
                "messages": [
                    {'message_id': 7, 'sender_id': 1, 'message': 'Họp vào ngày mai nhé!', 'time': '2024-12-02 09:00:00.626571'},
                    {'message_id': 8, 'sender_id': 4, 'message': 'Chắc được rồi, giờ nào?', 'time': '2024-12-02 09:05:00.626571'},
                    {'message_id': 9, 'sender_id': 7, 'message': 'Họp vào sáng mai, ổn không?', 'time': '2024-12-02 09:10:00.626571'}
                ]
            }
        ]

        self.messages_by_user = [
                    {'message_id': 17, 'sender_id': 1, 'receiver_id': 2, 'message': 'Message 20', 'time': '2024-12-04 07:10:57.626571'}
        ]
        self.Room = {}
    def GetGroupMembers(self, request, context):
        group_id = request.group_id
        # Tìm nhóm theo group_id
        group = next((g for g in self.groups if g['group_id'] == int(group_id)), None)
        if group is None:
            return chat_pb2.GetGroupMembersResponse(members=member_usernames)
        # Trả về danh sách tên người dùng của các thành viên
        members = [
            chat_pb2.Member(user_id = user['id'], username=user['username'], fullname=user['fullname'])
            for user in self.users if user['id'] in group['members']
        ]
        return chat_pb2.GetGroupMembersResponse(members=members)
    def NewUser(self, request, context):
        username = request.username
        password = request.password
        fullname = request.fullname
        user = next((user for user in self.users if user['username'] == username), None)
        if user:
            return chat_pb2.LoginResponse(
                success=False,
                message="Username đã được tạo",
                token=""
            )
        else :
            new_id = len(self.users) + 1
            # Thêm user mới vào danh sách
            new_user = {
                'id': new_id,
                'username': username,
                'password': password,
                'fullname': fullname
            }
            self.users.append(new_user)

            payload = {
                "uid": new_id
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return chat_pb2.LoginResponse(
                success=True,
                message="Đăng nhập thành công",
                token=token,
                uid = new_id,
                fullname = fullname
            )

    def Login(self, request, context):
        username = request.username
        password = request.password
        user = next((user for user in self.users if user['username'] == username), None)
        if not user:
            return chat_pb2.LoginResponse(
                success=False,
                message="not_been_created",
                token=""
            )
        if user['password'] != password:
            return chat_pb2.LoginResponse(
                success=False,
                message="Nhập sai mật khẩu",
                token=""
            )

        payload = {
            "uid": user['id']
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return chat_pb2.LoginResponse(
            success=True,
            message="Đăng nhập thành công",
            token=token,
            uid = user['id'],
            fullname = user['fullname']
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
    def get_user_groups(self,user_id, groups):#[{'group_id': 1, 'title': 'Nhóm học tập', 'last_message': {'message_id': 3, 'sender_id': 3, 'message': 'Cần giúp đỡ gì không?', 'time': '2025-12-01T10:10:00'}}]
        # Danh sách các nhóm mà người dùng tham gia
        user_groups = []

        for group in groups:
            if user_id in group["members"]:
                if group['messages']:
                    latest_message = max(group['messages'], key=lambda msg: datetime.fromisoformat(msg['time']))
                else:
                    latest_message = {"message_id": None, "sender_id": None, "message": "Chưa có tin nhắn", "time": str(datetime.now())}
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
                self.tick_time_userOfftine[uid] = str(datetime.now())
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
            if idHash not in self.Room:
                self.Room[idHash] = {}
            if idUser not in self.room_users:
                self.room_users[idUser] = idHash
            else:
                if idUser in self.Room[self.room_users[idUser]]:
                    del self.Room[self.room_users[idUser]][idUser]
                self.room_users[idUser] = idHash
            self.Room[idHash][idUser] = context
            data_room = {
                "id": int(idRoom[1:]),
                "typeM": typeM,
                "messList": messList,
                "isInit": True
            }

            if 'p' in idRoom:
                user_id = int(idRoom[1:])
                data_room["isActive"] = bool(user_id in self.online_users)
                if user_id in self.tick_time_userOfftine and user_id not in self.online_users:
                    data_room["lastTimeOnline"] = self.tick_time_userOfftine[user_id]
                user = next((u for u in self.users if u['id'] == user_id), None)
                data_room["title"] = user['fullname'] if user else None
            elif 'g' in idRoom:
                group_id = int(idRoom[1:])
                group = next((g for g in self.groups if g['group_id'] == group_id), None)
                data_room["title"] =  group['title'] if group else None
            
            


            yield chat_pb2.DataRoom(**data_room)

            while True:
                    await asyncio.sleep(1)
                    data_room = {
                        "id": int(idRoom[1:]),
                        "typeM": typeM
                    }

                    if 'p' in idRoom:
                        user_id = int(idRoom[1:])
                        data_room["isActive"] = bool(user_id in self.online_users)
                        if user_id in self.tick_time_userOfftine and user_id not in self.online_users:
                            data_room["lastTimeOnline"] = self.tick_time_userOfftine[user_id]
                        user = next((u for u in self.users if u['id'] == user_id), None)
                        data_room["title"] = user['fullname'] if user else None
                    elif 'g' in idRoom:
                        group_id = int(idRoom[1:])
                        group = next((g for g in self.groups if g['group_id'] == group_id), None)
                        data_room["title"] =  group['title'] if group else None
                    yield chat_pb2.DataRoom(**data_room)
            return
        except Exception as e:
            print(e)
        finally:
            if idUser in self.Room[idHash]:
                del self.Room[idHash][idUser]
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
            'time': current_time
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
                'time': current_time
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

    async def OutGroup(self,request,context):
        uid = await self.authen(context)
        group = next((group for group in self.groups if group['group_id'] == int(request.group_id)),None)
        if group is None:
            return chat_pb2.StatusResponse(status=False, message=f"Nhóm không tồn tại.")
        if uid not in group['members']:
            return chat_pb2.StatusResponse(status=False, message=f"Bạn không thuộc nhóm này.")
        group['members'].remove(uid)
        return chat_pb2.StatusResponse(status=True, message=f"Rời nhóm thành công.")
    async def NewGroup(self,request,context):
        uid = await self.authen(context)
        print(list([gr['group_id'] for gr in self.groups]))
        group_id = max(list([gr['group_id'] for gr in self.groups])) + 1
        new_group = {
            "group_id": group_id,
            "title": request.title,
            "members": [uid],
            "messages": [{'message_id': 1, 'sender_id': uid, 'message': 'Nhóm được khởi tạo !!!', 'time': str(datetime.now())}
               ]
        }
        self.groups.append(new_group)
        return chat_pb2.StatusResponse(status=True, message=f"Tạo nhóm thành công.")

    async def AddUserToGroup(self,request,context):
        uid = await self.authen(context)
        group_id = request.group_id
        user = next((user for user in self.users if user['username'] == request.username),None)
        if user is None:
            return chat_pb2.StatusResponse(status=False, message=f"Người dùng không tồn tại.")
        user_id = user['id']
        print(group_id,user_id,request.username)
        group = next((group for group in self.groups if group['group_id'] == int(group_id)),None)
        if group is None:
            return chat_pb2.StatusResponse(status=False, message=f"Nhóm không tồn tại.")
        if uid not in group['members']:
            return chat_pb2.StatusResponse(status=False, message=f"Bạn không thuộc nhóm này.")
        if user_id in group['members']:
            return chat_pb2.StatusResponse(status=False, message=f"Người dùng đã tham gia nhóm này.")
        group['members'].append(user_id)
        return chat_pb2.StatusResponse(status=True, message=f"Thêm thành viên thành công.")

    async def print_abc(self):
        while True:
            log_message = "\n\n\n" + "="*38 + "\n"
            log_message += "======ROOM======\n" + str(self.Room) + "\n"
            log_message += "======ROOM USER======\n" + str(self.room_users) + "\n"
            log_message += "======OFFLINE USER======\n" + str(self.tick_time_userOfftine) + "\n"
            
            log_message += "="*38 + "\n"
            
            # Ghi thông tin vào file log
            logging.info(log_message)
            
            # Chờ 2 giây
            await asyncio.sleep(2)

async def serve():
    server = grpc.aio.server()
    chats = ChatService()
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chats, server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await chats.print_abc()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
