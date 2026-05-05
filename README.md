# Note App Firebase - LAB 2 (API & Firebase)

Ứng dụng **Note App Firebase**:

- **Backend**: FastAPI cung cấp REST API.
- **Frontend**: Streamlit.
- **Auth**: Firebase Authentication, Email/Password và Google OAuth.
- **Database**: Cloud Firestore lưu ghi chú theo từng user.

---

# Thông Tin Sinh Viên

- Họ và tên: Hồ Hữu Nghiêm
- MSSV: 24120390
- Môn học: Tư duy tính toán
- Giảng viên: Lê Đức Khoan
- Trường: Đại học Khoa Học Tự Nhiên - ĐHQG TP.HCM

## 1. Cấu trúc thư mục

```
24120390_Lab2/
├── backend/
│   └── app/
│       ├── main.py
│       ├── firebase_config.py
│       └── routes/
│           ├── notes.py
│           └── google_auth.py
├── frontend/
│   ├── app.py
│   └── api_client.py
├── .streamlit/
│   └── secrets.toml
├── requirements.txt
├── .gitignore
└── README.md
```

## 2. Cài đặt môi trường

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Chạy backend

```bash
uvicorn backend.app.main:app --reload
```

## 4. Chạy frontend

```bash
streamlit run frontend/app.py
```

Frontend:
http://localhost:8501

## 5. Cấu hình Firebase

Tạo file `.streamlit/secrets.toml` và thêm cấu hình Firebase.

## 6. API endpoints

- GET /users/me
- GET /notes
- POST /notes
- PUT /notes/{note_id}
- DELETE /notes/{note_id}

## 7. Feature

- Đăng nhập Email/Password
- Đăng nhập Google
- Thêm ghi chú
- Sửa ghi chú
- Xóa ghi chú
- Reset mật khẩu

## 8. Demo API

Mở:
http://localhost:8000/docs

Bấm:
Try it out → Execute

Xem:
Response body


## 9. Video demo

[![Xem video demo](https://img.youtube.com/vi/kIUn8j_z36s/0.jpg)](https://youtu.be/kIUn8j_z36s)
