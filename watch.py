from datetime import datetime
from datetime import timedelta

def time_ago(time_str):
    # Chuyển chuỗi thời gian thành đối tượng datetime (bao gồm microseconds)
    time_format = "%Y-%m-%d %H:%M:%S.%f"
    time_obj = datetime.strptime(time_str, time_format)

    # Lấy thời gian hiện tại
    now = datetime.now()

    # Tính toán độ chênh lệch giữa thời gian hiện tại và thời gian đã cho
    time_diff = now - time_obj

    # Nếu độ chênh lệch lớn hơn 1 tuần
    if time_diff > timedelta(weeks=1):
        return time_obj.strftime("%d/%m")  # Trả về ngày/tháng

    # Nếu độ chênh lệch là dưới 1 tuần, kiểm tra từng trường hợp
    print(time_diff)
    print(timedelta(minutes=1))
    if time_diff < timedelta(minutes=1):
        return f"{time_diff.seconds} giây trước"
    elif time_diff < timedelta(hours=1):
        return f"{time_diff.seconds // 60} phút trước"
    elif time_diff < timedelta(days=1):
        return f"{time_diff.seconds // (60*60)} giờ trước"
    else:
        return f"{time_diff.days} ngày trước"

# Ví dụ sử dụng
time_str = "2024-12-04 07:31:57.626571"
print(time_ago(time_str))
