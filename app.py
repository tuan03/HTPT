import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import messagebox
import datetime
import sqlite3
import io
import numpy as np
from io import BytesIO
from PIL import Image, ImageTk
import grpc
import time
import chat_pb2
import chat_pb2_grpc
import asyncio
from async_tkinter_loop import async_handler, async_mainloop
import nest_asyncio
from google.protobuf.empty_pb2 import Empty
# 👇️ call apply()
nest_asyncio.apply()
###################################3
class ChatClient:
    def __init__(self):
        self.root = None
        self.rows = [{'name': "Nguyễn Anh Tuấn", "content": "Xin chào, bạn là ai vậy, tôi biết bạn ư??? Bạn làm ơn nói cho tôi biết tên của bạn đi", 'time':'11/12'}]*20
        self.__def__sub_canvas = None # chứa danh sách tin nhắn hoặc người dùng

        self.stub = None
        self.channel = None
        self.list_user_online = []
        self.recent_user_inbox = []
        self.usergroups = []
        self.newMessages = None
        self.typeList = 'm'
        self.body_bar = None
        self.__login_frame = None
        self.entry_username = None
        self.entry_password = None
        self.channel = grpc.aio.insecure_channel('localhost:50051')
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        self.metadata =  None
        self.uid = None
    def isLogin(self):
        if self.metadata:
            return True 
        else:
            return False
    def login(self):
        self.__login_frame = tk.Tk()
        self.__login_frame.title("Đăng nhập")
        screen_width = self.__login_frame.winfo_screenwidth()
        screen_height = self.__login_frame.winfo_screenheight()

        # Kích thước cửa sổ
        window_width = 300
        window_height = 150

        # Tính toán vị trí để cửa sổ nằm giữa màn hình
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        # Đặt kích thước và vị trí cho cửa sổ
        self.__login_frame.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.__login_frame.resizable(False, False)  # Không cho phép thay đổi kích thước cửa sổ
        # Khung nhập tài khoản
        frame = tk.Frame(self.__login_frame, padx=20, pady=20)
        frame.pack(pady=10)

        # Nhãn và ô nhập cho Tài khoản
        label_username = tk.Label(frame, text="Tài khoản:")
        label_username.grid(row=0, column=0, pady=5, sticky="w")
        self.entry_username = tk.Entry(frame, width=25)
        self.entry_username.grid(row=0, column=1, pady=5)

        # Nhãn và ô nhập cho Mật khẩu
        label_password = tk.Label(frame, text="Mật khẩu:")
        label_password.grid(row=1, column=0, pady=5, sticky="w")
        self.entry_password = tk.Entry(frame, show="*", width=25)
        self.entry_password.grid(row=1, column=1, pady=5)

        # Nút Đăng nhập
        btn_login = tk.Button(frame, text="Đăng nhập", command= self.handle_login, width=15)
        btn_login.grid(row=2, column=0, columnspan=2, pady=10)

        # Chạy ứng dụng
        self.__login_frame.mainloop()
    def confirm_name():
        root = tk.Tk()
        root.title("Nhập họ và tên")

        # Lấy kích thước màn hình
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Kích thước cửa sổ
        window_width = 400
        window_height = 200

        # Tính toán vị trí để cửa sổ nằm giữa màn hình
        position_x = (screen_width - window_width) // 2
        position_y = (screen_height - window_height) // 2

        # Đặt kích thước và vị trí cho cửa sổ
        root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        root.resizable(False, False)

        # Nhãn thông báo
        label_message = tk.Label(
            root,
            text="Tài khoản chưa được khởi tạo trên hệ thống.\nNhập họ và tên của bạn:",
            font=("Arial", 12),
            pady=10
        )
        label_message.pack()

        # Tạo ô nhập họ và tên
        entry_name = tk.Entry(root, width=40)
        entry_name.pack(pady=10)

        # Nút xác nhận
        btn_confirm = tk.Button(
            root,
            text="Xác nhận",
            command=lambda: handle_confirm(entry_name, root),
            width=15
        )
        btn_confirm.pack(pady=10)

        root.mainloop()
    def handle_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if username and password:  # Kiểm tra xem ô nhập không rỗng
            loop = asyncio.get_event_loop()
            data = loop.run_until_complete(self.stub.Login(
                        chat_pb2.LoginRequest(username=username, password=password)
                    ))  
            if data.success :
                self.metadata = [('authorization', data.token)]
                self.uid = data.uid
                self.__login_frame.destroy()
            else:
                messagebox.showwarning("Cảnh báo", data.message)    
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập Tài khoản và Mật khẩu!")
    async def connect(self):
        # Tạo kết nối gRPC đến server
        
        try:
            # Streaming RPC, so we need to handle each message in a loop
            async for response in self.stub.Connect(
                Empty(),
                metadata=self.metadata
            ):
                online_users_list = [
                        {'id': user.id, 'username': user.username, 'fullname': user.fullname}
                        for user in response.online_users
                    ]
                
                self.list_user_online = online_users_list
                self.recent_user_inbox = response.recent_user_inbox
                print(self.recent_user_inbox)
                self.usergroups = response.groupmess
                self.render_list_bar()
                
        except grpc.RpcError as e:
            # Handle the error
            print(e)
            
    async def joinRoomChat(self, room):
        try:
            add_chat_func = None
            async for response in self.stub.JoinRoomChat(
                chat_pb2.JoinRoomRequest(idRoom=room),
                metadata=self.metadata
            ):

                if response.messList:
                    add_chat_func = self.render_mess(response,"test")
                if response.HasField('newMess'):
                    add_chat_func(response.newMess)
        except grpc.RpcError as e:
            # Handle the error
            print(e)
        except Exception as e:
            print(e)
    # async def SendMessage(self, room):
    #     try:
    #         async for response in self.stub.JoinRoomChat(
    #             chat_pb2.JoinRoomRequest(idRoom=room),
    #             metadata=self.metadata
    #         ):
    #             if response.messList:
    #                 self.render_mess(response.messList,"test")
                
    #     except Exception as e:
    #         print(e)
    async def run(self):
        self.root = tk.Tk()
        self.root.title("CHATTING")
        self.width = 1200
        self.height = 650
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.resizable(False, False)
        asyncio.create_task(self.connect())
        self.init_ui()
        async_mainloop(self.root)
        
    def update_scrollbar_visibility(self,canvas, scrollbar, frame):
        # Kiểm tra vùng cuộn của canvas
        scroll_region = canvas.bbox("all")  # Trả về tọa độ (x1, y1, x2, y2) của vùng cuộn
        if scroll_region:
            canvas_width = scroll_region[2] - scroll_region[0]
            canvas_height = scroll_region[3] - scroll_region[1]
            
            # Nếu chiều cao của vùng cuộn lớn hơn chiều cao của canvas, hiển thị thanh cuộn
            if canvas_height > frame.winfo_height():
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            else:
                scrollbar.pack_forget()  # Ẩn thanh cuộn khi không cần thiết
    def update_scrollbar_visibility_x(canvas, scrollbar, frame):
        # Kiểm tra vùng cuộn của canvas
        scroll_region = canvas.bbox("all")  # Trả về tọa độ (x1, y1, x2, y2) của vùng cuộn
        
        if scroll_region:
            canvas_width = scroll_region[2] - scroll_region[0]
            canvas_height = scroll_region[3] - scroll_region[1]
            
            # Nếu chiều rộng của vùng cuộn lớn hơn chiều rộng của canvas, hiển thị thanh cuộn ngang
            if canvas_width > frame.winfo_width():
                scrollbar.pack(side=tk.BOTTOM, fill=tk.X)  # Hiển thị thanh cuộn ngang
            else:
                scrollbar.pack_forget()
        else:
            scrollbar.pack_forget() 
    def init_ui(self):
        left_bar = tk.Frame(self.root, width=300, height=self.height, bg="white", borderwidth=0, highlightthickness=0)
        left_bar.place(x=0,y=0)

        left_bar_header = tk.Canvas(left_bar, width=300, height=80, bg="white", borderwidth=0, highlightthickness=0)
        left_bar_header.place(x=0, y=0)
        self.left_bar = left_bar
        self.create_border(left_bar_header,btype="B")
        entry = tk.Entry(left_bar_header, font=("Arial", 13), width=25,bd=1, relief="solid")
        left_bar_header.create_window(10, 13, window=entry,anchor="nw")

        __temp = self.render_img(left_bar_header,"group-add.png",30,30,240,10,on_click=lambda e : print("cl"))
        text_id =  left_bar_header.create_text(10,  50,anchor='nw', text=f"Tin nhắn", fill="black",font=("Arial", 12)) 
        left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: self.render_list_bar(RType='m'))
        self.create_line(left_bar_header,10,70,70,70,width=2)
        text_id  = left_bar_header.create_text(10 + 90,  50,anchor='nw', text=f"Nhóm", fill="black",font=("Arial", 12))  
        left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: self.render_list_bar(RType='g'))
        self.create_line(left_bar_header,100,70,140,70,width=2)
        text_id  = left_bar_header.create_text(10 + 160,  50,anchor='nw', text=f"Đang hoạt động", fill="black",font=("Arial", 12))  
        left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: self.render_list_bar(RType='o'))
        self.create_line(left_bar_header,170,70,280,70,width=2)
        w,h = self.get_w_h(left_bar_header)
        w2,h2 = self.get_w_h(left_bar)
        __def__width = 300
        __def__height = h2-h
        __def__temp = tk.Frame(left_bar, width=__def__width, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
        __def__temp.place(x=0,y=h)


        __def__canvas_root = tk.Canvas(__def__temp, width=__def__width-15, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
        __def__canvas_root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        __def__scrollbar = tk.Scrollbar(__def__temp, orient=tk.VERTICAL, command=__def__canvas_root.yview,width=10)
        __def__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        __def__canvas_root.config(yscrollcommand=__def__scrollbar.set)
        _w_temp = __def__width-15
        __def__sub_canvas = tk.Canvas(__def__canvas_root, width=_w_temp, height=70*len(self.rows), bg="white",borderwidth=0, highlightthickness=0)
        self.__def__sub_canvas = __def__sub_canvas
        self._w_temp = _w_temp
        self.__def__canvas_root = __def__canvas_root
        self.__def__scrollbar = __def__scrollbar
        self.__def__temp = __def__temp

        x,y = self.get_w_h(left_bar)
        line = tk.Canvas(self.root, width=1, height=self.height, bg="black", highlightthickness=0)
        line.place(x=x,y=0)
        body_bar = tk.Frame(self.root,width=self.width - x, height=self.height , bg="white", borderwidth=0, highlightthickness=0)
        body_bar.place(x=x+1,y=0)
        self.body_bar = body_bar

        self.temp_img_send = None
        
    def get_w_h(self,w):
        w.update_idletasks()
        return w.winfo_width(), w.winfo_height()
    def create_line(self,canvas, x1, y1, x2, y2, color="black", width=1):
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
    def create_border(self,canvas, btype="LRTB", color="black", width=1): # type = "LRTB"
        w,h = self.get_w_h(canvas)
        if 'L' in btype:
            canvas.create_line(0, 0, 0, h, fill=color, width=width)
        if 'R' in btype:
            canvas.create_line(w-1, 0, w-1, h, fill=color, width=width)
        if 'B' in btype:
            canvas.create_line(0, h-1, w , h -1, fill=color, width=width)
        if 'T' in btype:
            canvas.create_line(0, 0, w -1, 0, fill=color, width=width)
    def on_enter(self,event):
        event.widget.config(cursor="hand2") 
    def on_leave(self,event):
        event.widget.config(cursor="arrow") 
    def render_img(self,canvas,img_path, width,height, x,y,anchor="nw",on_click = None ):
        image = Image.open(img_path)
        image = image.resize((width, height)) 
        photo = ImageTk.PhotoImage(image)
        image_id = canvas.create_image(x, y, image=photo,anchor=anchor)
        if on_click is not None:
            canvas.tag_bind(image_id, "<Button-1>", on_click)
            canvas.tag_bind(image_id, "<Enter>", self.on_enter)
            canvas.tag_bind(image_id, "<Leave>", self.on_leave)
        return photo
    def truncate_text(self,text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
    def render_list_bar(self,RType = 'r'): #RType = m, g, o
        if RType != 'r':
            self.typeList = RType
        
        self.__def__sub_canvas.delete("all")
        bbox = self.__def__sub_canvas.bbox("all") 
        self.__def__sub_canvas.config(width=0, height=0)
        if self.typeList == 'm':
            for index, row in enumerate(self.recent_user_inbox): # [{'message_id': 21, 'message': 'Message 21', 'time': '2024-12-03', 'isRead': True, 'isMe': False, 'col': {'id': 2, 'username': 'hoangminh7', 'password': 'password123', 'fullname': 'Hoàng Minh Tâm'}}]
                child_can = tk.Canvas(self.__def__sub_canvas, width=self._w_temp, height=70, bg="white",borderwidth=0, highlightthickness=0)
                self.__def__sub_canvas.create_window(0, (index)*70, window=child_can,anchor='nw')
                child_can.create_text(10,  10,anchor='nw', text=row.col.fullname, fill="black",font=("Arial", 15)) 
                child_can.create_text(10,  40,anchor='nw', text=self.truncate_text(row.message, 45), fill="black",font=("Arial", 10)) 
                child_can.create_text(self._w_temp-50,  10,anchor='nw', text=row.time, fill="black",font=("Arial", 10)) 
                # datamess = [{'content':"Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn tôi đến từ Xin chào tất cả các bạn, tôi đến từ ", 'isMe': True, 'time': '11/12', 'isRead':True},{'content':"Xin chào", 'isMe': False, 'time': '11/12', 'isRead':True}]*1
                child_can.bind("<Button-1>", lambda x , id = row.col.id: asyncio.create_task(self.joinRoomChat(('p'+str(id)))))
                child_can.update_idletasks()
                child_can.create_line(0, 69, self._w_temp, 69, fill="black", width=1)
        elif self.typeList == 'g':
            for index, row in enumerate(self.usergroups): # [{'message_id': 21, 'message': 'Message 21', 'time': '2024-12-03', 'isRead': True, 'isMe': False, 'col': {'id': 2, 'username': 'hoangminh7', 'password': 'password123', 'fullname': 'Hoàng Minh Tâm'}}]
                child_can = tk.Canvas(self.__def__sub_canvas, width=self._w_temp, height=70, bg="white",borderwidth=0, highlightthickness=0)
                self.__def__sub_canvas.create_window(0, (index)*70, window=child_can,anchor='nw')
                child_can.create_text(10,  10,anchor='nw', text=row.title, fill="black",font=("Arial", 15)) 
                child_can.create_text(10,  40,anchor='nw', text=self.truncate_text(row.last_message.message, 45), fill="black",font=("Arial", 10)) 
                child_can.create_text(self._w_temp-50,  10,anchor='nw', text=row.last_message.time, fill="black",font=("Arial", 10)) 
                # datamess = [{'content':"Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn tôi đến từ Xin chào tất cả các bạn, tôi đến từ ", 'isMe': True, 'time': '11/12', 'isRead':True},{'content':"Xin chào", 'isMe': False, 'time': '11/12', 'isRead':True}]*1
                child_can.bind("<Button-1>", lambda x , id = row.group_id: asyncio.create_task(self.joinRoomChat('g'+str(id))))
                child_can.update_idletasks()
                child_can.create_line(0, 69, self._w_temp, 69, fill="black", width=1)
        elif self.typeList == 'o':
            for index, row in enumerate(self.list_user_online): 
                child_can = tk.Canvas(self.__def__sub_canvas, width=self._w_temp, height=70, bg="white",borderwidth=0, highlightthickness=0)
                self.__def__sub_canvas.create_window(0, (index)*70, window=child_can,anchor='nw')
                child_can.create_text(self._w_temp//2,  70//2,anchor='center', text=row['fullname'], fill="black",font=("Arial", 15))
                datamess = [{'content':"Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn tôi đến từ Xin chào tất cả các bạn, tôi đến từ ", 'isMe': True, 'time': '11/12', 'isRead':True},{'content':"Xin chào", 'isMe': False, 'time': '11/12', 'isRead':True}]*1
                child_can.bind("<Button-1>", lambda x ,  id = row['id']: asyncio.create_task(self.joinRoomChat('p'+str(id))))
                child_can.update_idletasks()
                child_can.create_line(0, 69, self._w_temp, 69, fill="black", width=1)
        bbox = self.__def__sub_canvas.bbox("all") 
        if bbox:
            self.__def__sub_canvas.config(width=bbox[2], height=bbox[3])
        self.__def__canvas_root.create_window((0, 0), window=self.__def__sub_canvas, anchor=tk.NW)
        self.__def__sub_canvas.update_idletasks()
        self.__def__canvas_root.config(scrollregion=self.__def__canvas_root.bbox("all"))
        self.update_scrollbar_visibility(self.__def__canvas_root,self.__def__scrollbar,self.__def__temp)
    
    def render_mess(self,dataG,name):
        data = dataG.messList
        body_bar = self.body_bar
        height = self.height
        width = self.width
        left_bar = self.left_bar
        x,y = self.get_w_h(left_bar)
        self.clear_frame(body_bar)
        main_bar = tk.Frame(body_bar, width=600, height=height, bg="white", borderwidth=0, highlightthickness=0)
        main_bar.place(x=0,y=0)
        main_bar_header = tk.Canvas(main_bar, width=width-x, height=80, bg="white", borderwidth=0, highlightthickness=0)
        main_bar_header.place(x=0, y=0)
        self.create_border(main_bar_header,btype="B")
        main_bar_header.create_text(20,  20,anchor='nw', text=name, fill="black",font=("Arial", 15)) 
        main_bar_header.create_text(30,  45,anchor='nw', text="(Đang hoạt động)", fill="black",font=("Arial", 13)) 
        w,h = self.get_w_h(main_bar_header)
        w2,h2 = self.get_w_h(main_bar)
        __def__width = w2
        __def__height = h2-h-100
        __def__temp = tk.Frame(main_bar, width=__def__width, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
        __def__temp.place(x=0,y=h)
        __def__canvas_root = tk.Canvas(__def__temp, width=__def__width-15, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
        __def__canvas_root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        __def__scrollbar = tk.Scrollbar(__def__temp, orient=tk.VERTICAL, command=__def__canvas_root.yview,width=10)
        __def__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        __def__canvas_root.config(yscrollcommand=__def__scrollbar.set)
        _w_temp = __def__width-15
        __def__sub_canvas = tk.Canvas(__def__canvas_root, width=_w_temp-10, bg="white",borderwidth=0, highlightthickness=0)
        for index, row in enumerate(data): 
            bbox2 = __def__sub_canvas.bbox("all")
            if bbox2 is None:
                bbox2 = (0,0,0,0)
            child_can = tk.Canvas(__def__sub_canvas,  bg="white", highlightthickness=0,relief="solid",bd="1")
            child_can.create_text(10, 10, anchor="nw", text=row.message, width=250, font=("Arial", 12), fill="black")
            # Cập nhật kích thước của Canvas để chứa văn bản
            bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
            child_can.config(width=bbox[2]+10, height=bbox[3]+40)
            child_can.create_text(10, bbox[3]+10, anchor="nw", text=f"{row.time} {row.isRead}", width=250, font=("Arial", 10), fill="black")
            bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
            child_can.config(width=bbox[2]+10, height=bbox[3])
            if not row.isMe :
                __def__sub_canvas.create_window(10, bbox2[3] + 10, window=child_can,anchor='nw')
            else :
                __def__sub_canvas.create_window(_w_temp - bbox[2]-30, bbox2[3] + 10, window=child_can,anchor='nw')
        __def__sub_canvas.update_idletasks()
        bbox2 = __def__sub_canvas.bbox("all")
        __def__sub_canvas.config( height=bbox2[3]+10)
        __def__canvas_root.create_window((1, 10), window=__def__sub_canvas, anchor=tk.NW)
        __def__sub_canvas.update_idletasks()
        __def__canvas_root.config(scrollregion=__def__canvas_root.bbox("all"))
        __def__sub_canvas.update_idletasks()
        _,_,w,h = __def__canvas_root.bbox("all")
        ##################################
        __def__canvas_root.yview_moveto(1)
        ##################################
        x,y = self.get_w_h(left_bar)
        main_bar_footer = tk.Canvas(main_bar, width=600, height=100, bg="white", borderwidth=0, highlightthickness=0)
        main_bar_footer.place(x=0, y=y-100)
        self.create_border(main_bar_footer,btype="T")
        text_widget = tk.Text(self.root, font=("Arial", 13), width=50, height=3, bd=1, relief="solid")
        text_widget.config(padx=10, pady=10)
        main_bar_footer.create_window(10, 13, window=text_widget,anchor="nw")

        def add_mess_to_box(new_message):
            text_widget.delete("1.0", "end")
            bbox2 = __def__sub_canvas.bbox("all")
            if bbox2 is None:
                bbox2 = (0,0,0,0)
            child_can = tk.Canvas(__def__sub_canvas,  bg="white", highlightthickness=0,relief="solid",bd="1")
            child_can.create_text(10, 10, anchor="nw", text=new_message.message, width=250, font=("Arial", 12), fill="black")
            # Cập nhật kích thước của Canvas để chứa văn bản
            bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
            child_can.config(width=bbox[2]+10, height=bbox[3]+40)
            child_can.create_text(10, bbox[3]+10, anchor="nw", text=f"{new_message.time} (Đã xem)", width=250, font=("Arial", 10), fill="black")
            bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
            child_can.config(width=bbox[2]+10, height=bbox[3])
            if new_message.sender.id != self.uid :
                __def__sub_canvas.create_window(10, bbox2[3] + 10, window=child_can,anchor='nw')
            else :
                __def__sub_canvas.create_window(_w_temp - bbox[2]-30, bbox2[3] + 10, window=child_can,anchor='nw')

            __def__sub_canvas.update_idletasks()
            bbox2 = __def__sub_canvas.bbox("all")
            __def__sub_canvas.config( height=bbox2[3]+10)
            __def__canvas_root.create_window((1, 10), window=__def__sub_canvas, anchor=tk.NW)
            __def__sub_canvas.update_idletasks()
            __def__canvas_root.config(scrollregion=__def__canvas_root.bbox("all"))
            __def__sub_canvas.update_idletasks()
            _,_,w,h = __def__canvas_root.bbox("all")
            self.update_scrollbar_visibility(__def__canvas_root,__def__scrollbar,__def__temp) 
            __def__canvas_root.yview_moveto(1)

        async def add_mess():
            message = text_widget.get("1.0", "end-1c")
            # print(message)
            if dataG.typeM == 'p':
                try:
                    self.stub.SendMessage(
                        chat_pb2.SendMessageRequest(message=message,receiver_id=dataG.id),
                        metadata=self.metadata
                    )   
                except Exception as e:
                    print(e)
                # add_mess_to_box()
            elif dataG.typeM == 'g':
                try:
                    self.stub.SendMessage(
                        chat_pb2.SendMessageRequest(message=message,group_id=dataG.id),
                        metadata=self.metadata
                    )   
                except Exception as e:
                    print(e)
                # add_mess_to_box()


        self.temp_img_send = self.render_img(main_bar_footer,"send.png",30,30,530,35,on_click=lambda _ : asyncio.create_task(add_mess()))
        self.update_scrollbar_visibility(__def__canvas_root,__def__scrollbar,__def__temp)    
        body_bar.update_idletasks()  # Cập nhật thông tin kích thước
        width = body_bar.winfo_reqwidth()
        height = body_bar.winfo_reqheight()
        body_bar.config(width=width, height=height)
        return add_mess_to_box



    def clear_frame(self,frame):
        for widget in frame.winfo_children():
            widget.destroy()


async def main():
    client = ChatClient()
    client.login()
    if client.isLogin() :
        await client.run()
asyncio.run(main())
exit(0)

#######################################






# Lấy kích thước màn hình và tính toán vị trí











# root.mainloop()
# exit(0)



exit(0)
# canvas_header = tk.Canvas(root, width=width, height=151, bg="white", borderwidth=0, highlightthickness=0)
# canvas_header.place(x=0, y=0)
# canvas_frame5 = tk.Frame(canvas_frame2, width=canvas_frame2.winfo_width()-canvas_frame3.winfo_width() -canvas_frame4.winfo_width(), height=canvas_frame3.winfo_height(), bg="white", borderwidth=0, highlightthickness=0)
# canvas_frame5.place(x=canvas_frame3.winfo_width()+canvas_frame4.winfo_width(),y=0)


x,y = get_w_h(main_bar)
x2,y2 = get_w_h(left_bar)
right_bar = tk.Frame(root, width=width-x-x2, height=height, bg="white", borderwidth=0, highlightthickness=0)
right_bar.place(x=x+x2,y=0)
right_bar_header = tk.Canvas(right_bar, width=width-x-x2, height=80, bg="white", borderwidth=0, highlightthickness=0)
right_bar_header.place(x=0, y=0)
create_border(right_bar_header,btype="BL")
w,h = get_w_h(right_bar_header)
right_bar_header.create_text(w//2,  h//2,anchor='center', text="Thông tin người dùng", fill="black",font=("Arial", 15)) 
w2,h2 = get_w_h(right_bar)
right_bar_main = tk.Canvas(right_bar, width=width-x-x2, height=h2-h, bg="white", borderwidth=0, highlightthickness=0)
right_bar_main.place(x=0, y=h)
create_border(right_bar_main,btype="BL")

root.mainloop()