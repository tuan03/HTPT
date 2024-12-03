import tkinter as tk
from tkinter import messagebox

__login_frame = tk.Tk()
__login_frame.title("Đăng nhập")
entry_username = None
entry_password = None
def handle_confirm(entry_name, root):
    """Xử lý sau khi người dùng nhập họ và tên"""
    name = entry_name.get()
    if name.strip():
        messagebox.showinfo("Thông báo", f"Họ và tên của bạn là: {name}")
        root.destroy()  # Đóng cửa sổ
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập họ và tên!")
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
def handle_login():
    """Hàm xử lý khi nhấn nút Đăng nhập"""
    username = entry_username.get()
    password = entry_password.get()
    if username and password:  # Kiểm tra xem ô nhập không rỗng
        confirm_name()
        __login_frame.destroy()
    else:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập Tài khoản và Mật khẩu!")

def login():
    global entry_password
    global entry_username
    # Lấy kích thước màn hình
    screen_width = __login_frame.winfo_screenwidth()
    screen_height = __login_frame.winfo_screenheight()

    # Kích thước cửa sổ
    window_width = 300
    window_height = 150

    # Tính toán vị trí để cửa sổ nằm giữa màn hình
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2

    # Đặt kích thước và vị trí cho cửa sổ
    __login_frame.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    __login_frame.resizable(False, False)  # Không cho phép thay đổi kích thước cửa sổ
    # Khung nhập tài khoản
    frame = tk.Frame(__login_frame, padx=20, pady=20)
    frame.pack(pady=10)

    # Nhãn và ô nhập cho Tài khoản
    label_username = tk.Label(frame, text="Tài khoản:")
    label_username.grid(row=0, column=0, pady=5, sticky="w")
    entry_username = tk.Entry(frame, width=25)
    entry_username.grid(row=0, column=1, pady=5)

    # Nhãn và ô nhập cho Mật khẩu
    label_password = tk.Label(frame, text="Mật khẩu:")
    label_password.grid(row=1, column=0, pady=5, sticky="w")
    entry_password = tk.Entry(frame, show="*", width=25)
    entry_password.grid(row=1, column=1, pady=5)

    # Nút Đăng nhập
    btn_login = tk.Button(frame, text="Đăng nhập", command=handle_login, width=15)
    btn_login.grid(row=2, column=0, columnspan=2, pady=10)

    # Chạy ứng dụng
    __login_frame.mainloop()

login()
