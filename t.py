import asyncio
from concurrent import futures
import grpc
import uuid
from datetime import datetime,timedelta
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
def authenticate_user(username, password,users):
    # Kiểm tra thông tin đăng nhập
    user = next((user for user in users if user['username'] == username and user['password'] == password), None)
    return user

# Hàm tạo JWT
def create_jwt(user_id):
    payload = {
        "uid": user_id
    }

    # Tạo JWT bằng cách mã hóa payload với SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Hàm xác thực JWT
def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded["uid"]  # Trả về thông tin người dùng từ JWT
    except jwt.ExpiredSignatureError:
        return "Token expired"
    except jwt.InvalidTokenError:
        return "Invalid token"

def login(username, password):
    # user = authenticate_user(username, password)
    if user:
        # Tạo JWT nếu đăng nhập thành công
        token = create_jwt(user)
        print(f"JWT token: {token}")
        return token
    else:
        print("Thông tin đăng nhập không hợp lệ.")
        return None

users = [
            {'id': 1, 'username': 'matrinh3', 'password': '123456', 'fullname': 'Nguyễn Anh Tuấn'},
        ]

print(authenticate_user('matrinh3','123456',users))
a = create_jwt(3)
print(a)
print(verify_jwt(a))