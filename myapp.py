import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog
import datetime
import sqlite3
import io
import numpy as np
from io import BytesIO
from PIL import Image, ImageTk

def update_scrollbar_visibility(canvas, scrollbar, frame):
    """ Kiểm tra xem thanh cuộn có cần thiết hay không và ẩn/hiện nó. """
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
    """ Kiểm tra xem thanh cuộn trục ngang có cần thiết hay không và ẩn/hiện nó. """
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
def get_w_h(w):
    w.update_idletasks()
    return w.winfo_width(), w.winfo_height()
def create_line(canvas, x1, y1, x2, y2, color="black", width=1):
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
def create_border(canvas, btype="LRTB", color="black", width=1): # type = "LRTB"
    w,h = get_w_h(canvas)
    if 'L' in btype:
        canvas.create_line(0, 0, 0, h, fill=color, width=width)
    if 'R' in btype:
        canvas.create_line(w-1, 0, w-1, h, fill=color, width=width)
    if 'B' in btype:
        canvas.create_line(0, h-1, w , h -1, fill=color, width=width)
    if 'T' in btype:
        canvas.create_line(0, 0, w -1, 0, fill=color, width=width)
def on_enter(event):
    event.widget.config(cursor="hand2") 
def on_leave(event):
    event.widget.config(cursor="arrow") 
def render_img(canvas,img_path, width,height, x,y,anchor="nw",on_click = None ):
    image = Image.open(img_path)
    image = image.resize((width, height)) 
    photo = ImageTk.PhotoImage(image)
    image_id = canvas.create_image(x, y, image=photo,anchor=anchor)
    if on_click is not None:
        canvas.tag_bind(image_id, "<Button-1>", on_click)
        canvas.tag_bind(image_id, "<Enter>", on_enter)
        canvas.tag_bind(image_id, "<Leave>", on_leave)
    return photo
root = tk.Tk()
root.title("CHATTING")
width = 1200
height = 650
# Lấy kích thước màn hình và tính toán vị trí
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (width // 2)
y = (screen_height // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")
root.resizable(False, False)

left_bar = tk.Frame(root, width=300, height=height, bg="white", borderwidth=0, highlightthickness=0)
left_bar.place(x=0,y=0)

left_bar_header = tk.Canvas(left_bar, width=300, height=80, bg="white", borderwidth=0, highlightthickness=0)
left_bar_header.place(x=0, y=0)
create_border(left_bar_header,btype="B")
entry = tk.Entry(left_bar_header, font=("Arial", 13), width=25,bd=1, relief="solid")
left_bar_header.create_window(10, 13, window=entry,anchor="nw")
def on_add_group_click(event):
    print("Ảnh đã được nhấn!")
__temp = render_img(left_bar_header,"group-add.png",30,30,240,10,on_click=on_add_group_click)
text_id =  left_bar_header.create_text(10,  50,anchor='nw', text=f"Tin nhắn", fill="black",font=("Arial", 12)) 
left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: print("Click text 1"))
create_line(left_bar_header,10,70,70,70,width=2)
text_id  = left_bar_header.create_text(10 + 90,  50,anchor='nw', text=f"Nhóm", fill="black",font=("Arial", 12))  
left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: print("Click text 2"))
create_line(left_bar_header,100,70,140,70,width=2)
text_id  = left_bar_header.create_text(10 + 160,  50,anchor='nw', text=f"Đang hoạt động", fill="black",font=("Arial", 12))  
left_bar_header.tag_bind(text_id, "<Button-1>", lambda x: print("Click text 3"))
create_line(left_bar_header,170,70,280,70,width=2)

rows = [{'name': "Nguyễn Anh Tuấn", "content": "Xin chào, bạn là ai vậy, tôi biết bạn ư??? Bạn làm ơn nói cho tôi biết tên của bạn đi", 'time':'11/12'}]*20
w,h = get_w_h(left_bar_header)
w2,h2 = get_w_h(left_bar)
__def__width = 300
__def__height = h2-h
__def__temp = tk.Frame(left_bar, width=__def__width, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
__def__temp.place(x=0,y=h)


__def__canvas_root = tk.Canvas(__def__temp, width=__def__width-15, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
__def__canvas_root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
__def__scrollbar = tk.Scrollbar(__def__temp, orient=tk.VERTICAL, command=__def__canvas_root.yview,width=10)
__def__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
__def__canvas_root.config(yscrollcommand=__def__scrollbar.set)
def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text
_w_temp = __def__width-15
__def__sub_canvas = tk.Canvas(__def__canvas_root, width=_w_temp, height=70*len(rows), bg="white",borderwidth=0, highlightthickness=0)
for index, row in enumerate(rows): 
    child_can = tk.Canvas(__def__sub_canvas, width=_w_temp, height=70, bg="white",borderwidth=0, highlightthickness=0)
    __def__sub_canvas.create_window(0, (index)*70, window=child_can,anchor='nw')
    
    child_can.create_text(10,  10,anchor='nw', text=row['name'], fill="black",font=("Arial", 15)) 
    child_can.create_text(10,  40,anchor='nw', text=truncate_text(row['content'], 45), fill="black",font=("Arial", 10)) 
    child_can.create_text(_w_temp-50,  10,anchor='nw', text=row['time'], fill="black",font=("Arial", 10)) 
    child_can.bind("<Button-1>", lambda x: print('click'+str(index)))
    child_can.update_idletasks()
    child_can.create_line(0, 69, _w_temp, 69, fill="black", width=1)
    # Thêm Canvas con vào Canvas chính sử dụng create_window
    

__def__canvas_root.create_window((0, 0), window=__def__sub_canvas, anchor=tk.NW)
__def__sub_canvas.update_idletasks()
__def__canvas_root.config(scrollregion=__def__canvas_root.bbox("all"))
# update_scrollbar_visibility(__def__canvas_root,__def__scrollbar,__def__temp)




x,y = get_w_h(left_bar)
main_bar = tk.Frame(root, width=600, height=height, bg="white", borderwidth=0, highlightthickness=0)
main_bar.place(x=x,y=0)
main_bar_header = tk.Canvas(main_bar, width=width-x, height=80, bg="white", borderwidth=0, highlightthickness=0)
main_bar_header.place(x=0, y=0)
create_border(main_bar_header,btype="BL")
main_bar_header.create_text(20,  20,anchor='nw', text="Nguyễn Anh Tuấn", fill="black",font=("Arial", 15)) 
main_bar_header.create_text(30,  45,anchor='nw', text="(Đang hoạt động)", fill="black",font=("Arial", 13)) 






data = [{'content':"Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn, tôi đến từ Xin chào tất cả các bạn tôi đến từ Xin chào tất cả các bạn, tôi đến từ ", 'isMe': True, 'time': '11/12', 'isRead':True},{'content':"Xin chào", 'isMe': False, 'time': '11/12', 'isRead':True}]*20

w,h = get_w_h(main_bar_header)
w2,h2 = get_w_h(main_bar)
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
    child_can.create_text(10, 10, anchor="nw", text=row['content'], width=250, font=("Arial", 12), fill="black")
    
    # Cập nhật kích thước của Canvas để chứa văn bản
    bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
    child_can.config(width=bbox[2]+10, height=bbox[3]+40)
    child_can.create_text(10, bbox[3]+10, anchor="nw", text="Gửi vào: 2 ngày trước (Đã xem)", width=250, font=("Arial", 10), fill="black")
    bbox = child_can.bbox("all")  # Lấy bounding box của văn bản
    child_can.config(width=bbox[2]+10, height=bbox[3])
    if not row['isMe'] :
        __def__sub_canvas.create_window(10, bbox2[3] + 10, window=child_can,anchor='nw')
    else :
        __def__sub_canvas.create_window(_w_temp - bbox[2]-30, bbox2[3] + 10, window=child_can,anchor='nw')
    
    # child_can.create_text(10,  10,anchor='nw', text=row['name'], fill="black",font=("Arial", 15)) 
    # child_can.create_text(10,  40,anchor='nw', text=truncate_text(row['content'], 45), fill="black",font=("Arial", 10)) 
    # child_can.create_text(_w_temp-50,  10,anchor='nw', text=row['time'], fill="black",font=("Arial", 10)) 
    # child_can.bind("<Button-1>", lambda x: print('click'+str(index)))
    # child_can.update_idletasks()
    # child_can.create_line(0, 69, _w_temp, 69, fill="black", width=1)
    # print(child_can.winfo_width())
__def__sub_canvas.update_idletasks()
bbox2 = __def__sub_canvas.bbox("all")

__def__sub_canvas.config( height=bbox2[3]+10)
__def__canvas_root.create_window((1, 10), window=__def__sub_canvas, anchor=tk.NW)

__def__sub_canvas.update_idletasks()
__def__canvas_root.config(scrollregion=__def__canvas_root.bbox("all"))
__def__sub_canvas.update_idletasks()
_,_,w,h = __def__canvas_root.bbox("all")

create_line(__def__canvas_root,0,0,0,h)
#auto roll
__def__canvas_root.yview_moveto(1)

x,y = get_w_h(left_bar)
main_bar_footer = tk.Canvas(main_bar, width=600, height=100, bg="white", borderwidth=0, highlightthickness=0)
main_bar_footer.place(x=0, y=y-100)
create_border(main_bar_footer,btype="TRL")
text_widget = tk.Text(root, font=("Arial", 13), width=50, height=3, bd=1, relief="solid")
text_widget.config(padx=10, pady=10)
main_bar_footer.create_window(10, 13, window=text_widget,anchor="nw")

__temp = render_img(main_bar_footer,"send.png",30,30,530,35,on_click=on_add_group_click)



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