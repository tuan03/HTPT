import copy
users = [
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
groups = [
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
                  ]
            }
        ]
def add_message_to_group(group_id, sender_id, message):
    # Tìm nhóm theo group_id
    group = next((g for g in groups if g['group_id'] == group_id), None)
    
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
        cob = next((user for user in users if user['id'] == sender_id), {})
        pmess['sender'] = cob if cob else {}
        sender_id = pmess.pop('sender_id', None)
        return pmess


print(add_message_to_group(3,111,"AHIHI"))