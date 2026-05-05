import streamlit as st
import requests

from api_client import (
    firebase_signup,
    firebase_login,
    get_current_user,
    create_note,
    get_notes,
    update_note,
    delete_note,
)

try:
    from api_client import reset_password
except ImportError:
    def reset_password(firebase_api_key, email):
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email,
        }
        return requests.post(url, json=payload)

VIDEO_URL = "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260429_114316_1c7889ad-2885-410e-b493-98119fee0ddb.mp4"

st.set_page_config(
    page_title="Note App Firebase",
    page_icon="📝",
    layout="wide",
)

firebase_config = dict(st.secrets["firebase_client"])
firebase_api_key = firebase_config["apiKey"]

if "id_token" not in st.session_state:
    st.session_state.id_token = None

if "email" not in st.session_state:
    st.session_state.email = None

if "name" not in st.session_state:
    st.session_state.name = None

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

if "editing_note_id" not in st.session_state:
    st.session_state.editing_note_id = None

if "editing_title" not in st.session_state:
    st.session_state.editing_title = ""

if "editing_content" not in st.session_state:
    st.session_state.editing_content = ""


def show_api_error(response, default_message):
    try:
        data = response.json()
        message = data.get("error", {}).get("message", "")
    except Exception:
        message = ""

    friendly_messages = {
        "INVALID_LOGIN_CREDENTIALS": "Email hoặc mật khẩu không đúng. Nếu bạn đã dùng Google trước đó, hãy bấm Đăng nhập bằng Google.",
        "EMAIL_EXISTS": "Email này đã được đăng ký. Hãy chuyển sang đăng nhập hoặc dùng email khác.",
        "EMAIL_NOT_FOUND": "Email này chưa được đăng ký.",
        "INVALID_PASSWORD": "Mật khẩu không đúng.",
        "WEAK_PASSWORD : Password should be at least 6 characters": "Mật khẩu phải có ít nhất 6 ký tự.",
        "MISSING_PASSWORD": "Vui lòng nhập mật khẩu.",
        "INVALID_EMAIL": "Email không hợp lệ.",
        "USER_DISABLED": "Tài khoản này đã bị vô hiệu hóa.",
        "TOKEN_EXPIRED": "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
        "INVALID_ID_TOKEN": "Phiên đăng nhập không hợp lệ. Vui lòng đăng nhập lại.",
    }

    if message in friendly_messages:
        st.error(friendly_messages[message])
    elif message:
        st.error(f"{default_message} Mã lỗi: {message}")
    else:
        st.error(default_message)

query_params = st.query_params

if "id_token" in query_params:
    st.session_state.id_token = query_params["id_token"]
    st.session_state.email = query_params.get("email", "")
    st.session_state.name = query_params.get("name", "")

    st.query_params.clear()
    st.success("Đăng nhập Google thành công.")
    st.rerun()

st.markdown(
    f"""
    <style>
    @font-face {{
        font-family: "Helvetica Regular";
        src: url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.eot");
        src: url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.eot?#iefix")format("embedded-opentype"),
        url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.woff2")format("woff2"),
        url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.woff")format("woff"),
        url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.ttf")format("truetype"),
        url("https://db.onlinewebfonts.com/t/a64ff11d2c24584c767f6257e880dc65.svg#Helvetica Regular")format("svg");
    }}

    :root {{
        --font-sans: "Helvetica Regular", Arial, sans-serif;
    }}

    html, body, [class*="css"] {{
        font-family: var(--font-sans) !important;
    }}

    body {{
        background: #050505;
        color: white;
    }}

    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    .stApp {{
        background: transparent;
        min-height: 115vh;
        overflow-x: hidden;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        z-index: 0;
        background:
            radial-gradient(circle at 50% 20%, rgba(255,255,255,0.12), transparent 34%),
            linear-gradient(180deg, rgba(0,0,0,0.18), rgba(0,0,0,0.78));
        pointer-events: none;
    }}

    .video-background {{
        position: fixed;
        inset: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        z-index: -2;
    }}

    .block-container {{
        position: relative;
        z-index: 10;
        max-width: 1280px;
        min-height: 115vh;
        padding-top: 10px;
        padding-bottom: 42px;
    }}

    .hero {{
        text-align: center;
        padding: 22px 18px 32px;
        color: white;
    }}

    .main-title {{
        font-size: clamp(46px, 8vw, 112px);
        line-height: 0.95;
        font-weight: 700;
        letter-spacing: -0.07em;
        margin: 0 auto 18px;
        text-shadow: 0 20px 70px rgba(0,0,0,0.55);
    }}

    .sub-title {{
        max-width: 900px;
        margin: 0 auto;
        color: rgba(255,255,255,0.72);
        font-size: 17px;
        line-height: 1.7;
    }}

    .top-auth-bar {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin-bottom: 18px;
        color: rgba(255,255,255,0.78);
        font-size: 13px;
    }}

    /* Input: chỉ còn 1 lớp nền, không bị 2 màu lồng nhau */
    .stTextInput input,
    .stTextArea textarea {{
        background: transparent !important;
        color: white !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}

    .stTextInput div[data-baseweb="input"],
    .stTextArea div[data-baseweb="textarea"] {{
        background: rgba(10, 16, 24, 0.82) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: none !important;
        border-radius: 999px !important;
    }}

    .stTextArea div[data-baseweb="textarea"] {{
        border-radius: 22px !important;
    }}

    .stTextInput div[data-baseweb="input"] > div,
    .stTextArea div[data-baseweb="textarea"] > div {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    label, .stMarkdown, .stCaption, h1, h2, h3, h4, p, span {{
        color: rgba(255,255,255,0.92) !important;
    }}

    .stButton > button,
    .stLinkButton > a {{
        width: 100%;
        border-radius: 999px !important;
        border: 1px solid rgba(255,255,255,0.22) !important;
        color: white !important;
        background: rgba(10, 16, 24, 0.82) !important;
        backdrop-filter: blur(10px);
        transition: 0.25s ease;
        font-weight: 700 !important;
    }}

    .stButton > button:hover,
    .stLinkButton > a:hover {{
        background: rgba(255,255,255,0.20) !important;
        border-color: rgba(255,255,255,0.46) !important;
    }}

    .note-card {{
        padding: 18px 20px;
        margin: 14px 0;
        border-radius: 20px;
        background: rgba(0,0,0,0.56);
        border: 1px solid rgba(255,255,255,0.14);
        backdrop-filter: blur(12px);
    }}

    .note-card h4 {{
        margin: 0 0 8px;
        color: white;
        font-size: 18px;
    }}

    .note-card p {{
        margin: 0 0 10px;
        color: rgba(255,255,255,0.78);
        line-height: 1.55;
    }}

    .note-card small {{
        color: rgba(255,255,255,0.48);
    }}

    .liquid-glass {{
      background: rgba(255, 255, 255, 0.01);
      background-blend-mode: luminosity;
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      border: none;
      box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
      position: relative;
      overflow: hidden;
    }}

    .liquid-glass::before {{
      content: '';
      position: absolute;
      inset: 0;
      border-radius: inherit;
      padding: 1.4px;
      background: linear-gradient(180deg,
        rgba(255,255,255,0.45) 0%, rgba(255,255,255,0.15) 20%,
        rgba(255,255,255,0) 40%, rgba(255,255,255,0) 60%,
        rgba(255,255,255,0.15) 80%, rgba(255,255,255,0.45) 100%);
      -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
      -webkit-mask-composite: xor;
      mask-composite: exclude;
      pointer-events: none;
    }}

    .liquid-footer {{
        width: 100%;
        border-radius: 30px;
        padding: 28px;
        color: rgba(255,255,255,0.7);
        margin-top: 128px;
        animation: footerIn 1s ease-out 0.4s both;
    }}

    @keyframes footerIn {{
        from {{ opacity: 0; transform: translateY(40px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .footer-grid {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 40px;
        margin-bottom: 40px;
    }}

    .brand-row {{
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        font-size: 20px;
        font-weight: 500;
        margin-bottom: 18px;
    }}

    .brand-desc {{
        max-width: 390px;
        font-size: 14px;
        line-height: 1.7;
        color: rgba(255,255,255,0.62);
    }}

    .footer-links {{
        display: grid;
        grid-template-columns: 1fr;
        gap: 26px;
    }}

    .footer-links h4 {{
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: white;
        font-weight: 500;
        margin: 0 0 16px;
    }}

    .footer-links a {{
        display: block;
        font-size: 12px;
        color: rgba(255,255,255,0.58);
        text-decoration: none;
        margin: 9px 0;
        transition: color 0.2s ease;
    }}

    .footer-links a:hover {{
        color: white;
    }}

    .footer-bottom {{
        padding-top: 24px;
        border-top: 1px solid rgba(255,255,255,0.10);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        gap: 18px;
    }}

    .footer-bottom p, .journey-label {{
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.22em;
        opacity: 0.5;
        margin: 0;
    }}

    .socials {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}

    .socials a {{
        color: rgba(255,255,255,0.70);
        text-decoration: none;
        font-size: 16px;
        transition: 0.2s ease;
    }}

    .socials a:hover {{
        color: white;
        opacity: 1;
    }}

    @media (min-width: 768px) {{
        .liquid-footer {{
            padding: 40px;
            margin-top: 256px;
        }}

        .footer-grid {{
            grid-template-columns: 5fr 7fr;
            gap: 48px;
        }}

        .footer-links {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .footer-bottom {{
            flex-direction: row;
            gap: 16px;
        }}
    }}
    </style>

    <video class="video-background" autoplay loop muted playsinline>
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """,
    unsafe_allow_html=True,
)

# Thanh đăng nhập/đăng ký góc phải
if st.session_state.id_token:
    left_space, user_col, logout_col = st.columns([6, 2.3, 1.2])
    with user_col:
        st.markdown(
            f"<div class='top-auth-bar'>Đang đăng nhập: {st.session_state.email}</div>",
            unsafe_allow_html=True,
        )
    with logout_col:
        if st.button("Đăng xuất"):
            st.session_state.id_token = None
            st.session_state.email = None
            st.session_state.name = None
            st.session_state.auth_mode = "login"
            st.rerun()

st.markdown(
    """
    <section class="hero">
        <h1 class="main-title">Note App Firebase</h1>
        <p class="sub-title">
            Ứng dụng ghi chú sử dụng FastAPI, Firebase Authentication,
            Google Cloud OAuth và Cloud Firestore.<br>
            Người phát triển: Hồ Hữu Nghiêm<br>
            Mã số sinh viên: 24120390<br>
            Môn học: Tư duy tính toán<br>
            Giảng viên: Lê Đức Khoan<br>
            Trường Đại học Khoa Học Tự Nhiên - Đại học Quốc gia Thành phố Hồ Chí Minh
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.id_token:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.session_state.auth_mode == "signup":
            st.subheader("Đăng ký tài khoản")

            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Mật khẩu", type="password", key="signup_password")

            if st.button("Tạo tài khoản"):
                if email.strip() == "" or password.strip() == "":
                    st.warning("Vui lòng nhập email và mật khẩu.")
                else:
                    response = firebase_signup(firebase_api_key, email, password)

                    if response.status_code == 200:
                        st.success("Đăng ký thành công. Đang chuyển sang đăng nhập.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        show_api_error(response, "Đăng ký thất bại.")

            if st.button("Đã có tài khoản? Chuyển sang đăng nhập"):
                st.session_state.auth_mode = "login"
                st.rerun()

        else:
            st.subheader("Đăng nhập")

            email = st.text_input("Email", key="login_email")
            password = st.text_input("Mật khẩu", type="password", key="login_password")

            if st.button("Đăng nhập bằng Email"):
                if email.strip() == "" or password.strip() == "":
                    st.warning("Vui lòng nhập email và mật khẩu.")
                else:
                    response = firebase_login(firebase_api_key, email, password)

                    if response.status_code == 200:
                        data = response.json()

                        st.session_state.id_token = data["idToken"]
                        st.session_state.email = data["email"]
                        st.session_state.name = data.get("displayName", "")

                        st.success("Đăng nhập thành công.")
                        st.rerun()
                    else:
                        show_api_error(response, "Đăng nhập thất bại.")
            if st.button("Quên mật khẩu?"):
                if email.strip() == "":
                    st.warning("Vui lòng nhập email trước khi đặt lại mật khẩu.")
                else:
                    response = reset_password(firebase_api_key, email)

                    if response.status_code == 200:
                        st.success("Đã gửi email đặt lại mật khẩu. Vui lòng kiểm tra hộp thư.")
                    else:
                        st.error("Không thể gửi email đặt lại mật khẩu. Kiểm tra lại email.")

            st.divider()

            st.link_button(
                "Đăng nhập bằng Google",
                "http://localhost:8000/auth/google/start",
            )

            if st.button("Chưa có tài khoản? Chuyển sang đăng ký"):
                st.session_state.auth_mode = "signup"
                st.rerun()

else:
    col1, col2, col3 = st.columns([1, 2.2, 1])

    with col2:
        st.subheader("Ghi chú của bạn")

        user_response = get_current_user(st.session_state.id_token)

        if user_response.status_code == 200:
            user = user_response.json()
            st.caption(f"Người dùng: {user.get('email')}")
        else:
            st.caption(f"Người dùng: {st.session_state.email}")

        # ===== FORM SỬA GHI CHÚ =====
        if st.session_state.editing_note_id:
            st.markdown("### Sửa ghi chú")

            edit_title = st.text_input(
                "Tiêu đề mới",
                value=st.session_state.editing_title,
                key="edit_title_input",
            )

            edit_content = st.text_area(
                "Nội dung mới",
                value=st.session_state.editing_content,
                height=160,
                key="edit_content_input",
            )

            col_save, col_cancel = st.columns(2)

            with col_save:
                if st.button("Cập nhật ghi chú"):
                    if edit_title.strip() == "" or edit_content.strip() == "":
                        st.warning("Vui lòng nhập đầy đủ tiêu đề và nội dung.")
                    else:
                        response = update_note(
                            st.session_state.id_token,
                            st.session_state.editing_note_id,
                            edit_title,
                            edit_content,
                        )

                        if response.status_code in (200, 204):
                            st.success("Đã cập nhật ghi chú.")
                            st.session_state.editing_note_id = None
                            st.session_state.editing_title = ""
                            st.session_state.editing_content = ""
                            st.rerun()
                        else:
                            show_api_error(response, "Cập nhật ghi chú thất bại.")

            with col_cancel:
                if st.button("Hủy sửa"):
                    st.session_state.editing_note_id = None
                    st.session_state.editing_title = ""
                    st.session_state.editing_content = ""
                    st.rerun()

            st.divider()

        st.markdown("### Thêm ghi chú mới")

        title = st.text_input("Tiêu đề", key="new_title")
        content = st.text_area("Nội dung", height=160, key="new_content")

        if st.button("Lưu ghi chú"):
            if title.strip() == "" or content.strip() == "":
                st.warning("Vui lòng nhập đầy đủ tiêu đề và nội dung.")
            else:
                response = create_note(st.session_state.id_token, title, content)

                if response.status_code == 200:
                    st.success("Đã lưu ghi chú.")
                    st.rerun()
                else:
                    show_api_error(response, "Lưu ghi chú thất bại.")

        st.divider()
        st.markdown("### Danh sách ghi chú")

        response = get_notes(st.session_state.id_token)

        if response.status_code == 200:
            notes = response.json().get("notes", [])

            if len(notes) == 0:
                st.info("Chưa có ghi chú nào.")
            else:
                for note in notes:
                    note_id = note.get("id") or note.get("note_id")

                    st.markdown(
                        f"""
                        <div class="note-card">
                            <h4>{note.get('title')}</h4>
                            <p>{note.get('content')}</p>
                            <small>Thời gian tạo: {note.get('created_at')}</small>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    col_edit, col_delete = st.columns(2)

                    with col_edit:
                        if st.button("Sửa ghi chú", key=f"edit_{note_id}"):
                            if not note_id:
                                st.error("Không tìm thấy ID ghi chú để sửa.")
                            else:
                                st.session_state.editing_note_id = note_id
                                st.session_state.editing_title = note.get("title", "")
                                st.session_state.editing_content = note.get("content", "")
                                st.rerun()

                    with col_delete:
                        if st.button("Xóa ghi chú", key=f"delete_{note_id}"):
                            if not note_id:
                                st.error("Không tìm thấy ID ghi chú để xóa.")
                            else:
                                response = delete_note(st.session_state.id_token, note_id)

                                if response.status_code in (200, 204):
                                    st.success("Đã xóa ghi chú.")
                                    if st.session_state.editing_note_id == note_id:
                                        st.session_state.editing_note_id = None
                                        st.session_state.editing_title = ""
                                        st.session_state.editing_content = ""
                                    st.rerun()
                                else:
                                    show_api_error(response, "Xóa ghi chú thất bại.")
        else:
            show_api_error(response, "Không đọc được danh sách ghi chú.")

st.markdown(
    """
    <footer class="liquid-footer liquid-glass">
        <div class="footer-grid">
            <div>
                <div class="brand-row">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 256 256" fill="currentColor"><path d="M 4.688 136 C 68.373 136 120 187.627 120 251.312 C 120 252.883 119.967 254.445 119.905 256 L 0 256 L 0 136.096 C 1.555 136.034 3.117 136 4.688 136 Z M 251.312 136 C 252.883 136 254.445 136.034 256 136.096 L 256 256 L 136.095 256 C 136.032 254.438 136.001 252.875 136 251.312 C 136 187.627 187.627 136 251.312 136 Z M 119.905 0 C 119.967 1.555 120 3.117 120 4.688 C 120 68.373 68.373 120 4.687 120 C 3.117 120 1.555 119.967 0 119.905 L 0 0 Z M 256 119.905 C 254.445 119.967 252.883 120 251.312 120 C 187.627 120 136 68.373 136 4.687 C 136 3.117 136.033 1.555 136.095 0 L 256 0 Z" /></svg>
                    <span>LUMINA</span>
                </div>
                <p class="brand-desc">
                    Lumina provides premium clarity on global events and cosmic wonders - shared with all for free.
                </p>
            </div>

            <div class="footer-links">
                <div>
                    <h4>Discover</h4>
                    <a href="#">Labs & Workshops</a>
                    <a href="#">Deep Dive Series</a>
                    <a href="#">Global Circle</a>
                    <a href="#">Resource Vault</a>
                    <a href="#">Future Roadmap</a>
                </div>
                <div>
                    <h4>The Mission</h4>
                    <a href="#">Origin Story</a>
                    <a href="#">The Collective</a>
                    <a href="#">Newsroom Hub</a>
                    <a href="#">Join the Team</a>
                </div>
                <div>
                    <h4>Concierge</h4>
                    <a href="#">Get in Touch</a>
                    <a href="#">Legal Privacy</a>
                    <a href="#">User Agreement</a>
                    <a href="#">Report Concern</a>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            <p>Curated by @GotInGeorgiG</p>
            <div class="socials">
                <span class="journey-label">Join the Journey:</span>
                <a href="#" title="Music">♫</a>
                <a href="#" title="Facebook">f</a>
                <a href="#" title="Twitter">𝕏</a>
                <a href="#" title="Youtube">▶</a>
                <a href="#" title="Instagram">◎</a>
            </div>
        </div>
    </footer>
    """,
    unsafe_allow_html=True,
)
