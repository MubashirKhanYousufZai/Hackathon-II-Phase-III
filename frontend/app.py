import streamlit as st
import requests
from typing import List, Dict

# =======================
# CONFIG
# =======================
API_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

st.set_page_config(
    page_title="Pro To-Do",
    page_icon="✅",
    layout="centered"
)

# =======================
# LOAD CUSTOM CSS
# =======================
def load_css(path: str):
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found")

load_css("style.css")

# =======================
# API FUNCTIONS
# =======================
def api_request(method: str, endpoint: str, payload=None):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json() if response.content else True
    except requests.exceptions.ConnectionError:
        st.error("❌ Backend is not running. Start FastAPI backend first!")
    except requests.exceptions.Timeout:
        st.error("⏱ Backend took too long to respond!")
    except requests.HTTPError:
        st.error(f"API Error {response.status_code}: {response.text}")
    return None

def get_todos() -> List[Dict]:
    return api_request("GET", "/todos/") or []

def add_todo(title: str):
    return api_request("POST", "/todos/", {"title": title, "description": "", "completed": False})

def update_todo(todo_id: int, title: str = None, description: str = None, completed: bool = None):
    payload = {}
    if title is not None: payload["title"] = title
    if description is not None: payload["description"] = description
    if completed is not None: payload["completed"] = completed
    return api_request("PUT", f"/todos/{todo_id}", payload)

def delete_todo(todo_id: int):
    return api_request("DELETE", f"/todos/{todo_id}")

def bulk_delete(ids: List[int]):
    return api_request("POST", "/todos/delete", {"ids": ids})

# =======================
# STATE MANAGEMENT
# =======================
if "todos" not in st.session_state:
    with st.spinner("Loading tasks..."):
        st.session_state.todos = get_todos()

if "editing" not in st.session_state:
    st.session_state.editing = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

todos = st.session_state.todos

# =======================
# SIDEBAR
# =======================
with st.sidebar:
    st.header("➕ Add New Task")
    with st.form("add_form", clear_on_submit=True):
        title = st.text_input("", placeholder="Enter task title...")
        if st.form_submit_button("Add Task"):
            if title.strip():
                new_todo = add_todo(title.strip())
                if new_todo:
                    st.session_state.todos.append(new_todo)
                    st.rerun()
            else:
                st.warning("Title cannot be empty")

    if todos:
        st.divider()
        if st.button("🧹 Clear All Tasks", type="primary"):
            if bulk_delete([t["id"] for t in todos]):
                st.session_state.todos = []
                st.rerun()

# =======================
# TASK CARD
# =======================
def task_card(todo: Dict, prefix: str):
    st.markdown("<div class='task-card'>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([0.05, 0.6, 0.15, 0.15])

    with col1:
        checked = st.checkbox("", value=todo["completed"], key=f"{prefix}_check_{todo['id']}")

    with col2:
        if todo["completed"]:
            st.markdown(f"<span class='completed-task'>{todo['title']}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{todo['title']}**")
        if todo.get("description"):
            st.caption(todo["description"])

    with col3:
        if st.button("✏️ Edit", key=f"{prefix}_edit_{todo['id']}"):
            st.session_state.editing = todo["id"]

    with col4:
        if st.button("🗑️", key=f"{prefix}_del_{todo['id']}"):
            if delete_todo(todo["id"]):
                st.session_state.todos = [t for t in todos if t["id"] != todo["id"]]
                st.session_state.editing = None
                st.rerun()

    if st.session_state.editing == todo["id"]:
        with st.expander("Edit Task", expanded=True):
            with st.form(f"{prefix}_edit_form_{todo['id']}"):
                new_title = st.text_input("Title", value=todo["title"])
                new_desc = st.text_area("Description", value=todo.get("description", ""))

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("Save"):
                        if update_todo(todo["id"], new_title.strip(), new_desc.strip()):
                            todo["title"] = new_title.strip()
                            todo["description"] = new_desc.strip()
                            st.session_state.editing = None
                            st.rerun()
                with col_b:
                    if st.form_submit_button("Cancel"):
                        st.session_state.editing = None
                        st.rerun()

    if checked != todo["completed"]:
        if update_todo(todo["id"], completed=checked):
            todo["completed"] = checked
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =======================
# MAIN UI
# =======================
st.title("✅ Pro To-Do App")
st.caption("Organize your tasks efficiently and stay productive 💡")

pending = [t for t in todos if not t["completed"]]
completed = [t for t in todos if t["completed"]]

tab1, tab2, tab3, tab4 = st.tabs([
    f"📋 All ({len(todos)})",
    f"⏳ Pending ({len(pending)})",
    f"✔ Completed ({len(completed)})",
    "🤖 AI Assistant"
])

with tab1:
    if not todos:
        st.info("No tasks yet.")
    for t in todos:
        task_card(t, "all")

with tab2:
    if not pending:
        st.success("Nothing pending 🎉")
    for t in pending:
        task_card(t, "pending")

with tab3:
    if not completed:
        st.info("No completed tasks.")
    for t in completed:
        task_card(t, "completed")

# =======================
# AI CHAT TAB
# =======================
with tab4:
    st.subheader("🤖 AI Todo Assistant")
    st.caption("Ask anything about productivity or tasks")

    user_msg = st.text_input("Your message", key="chat_input")

    if st.button("Send", key="chat_send") and user_msg:
        with st.spinner("AI is thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/chat",
                    json={"message": user_msg},
                    timeout=30  # Increased timeout for AI processing
                )
                if res.status_code == 200:
                    reply = res.json()["reply"]
                    st.session_state.chat_history.append(("You", user_msg))
                    st.session_state.chat_history.append(("AI", reply))
                    st.rerun()
                elif res.status_code == 401:
                    st.error("❌ Authentication error: Invalid GROQ API key. Please check your backend configuration.")
                elif res.status_code == 429:
                    st.error("Rate limit exceeded. Please try again later.")
                else:
                    error_detail = res.json().get("detail", "Unknown error") if res.content else "No response from server"
                    st.error(f"AI service error ({res.status_code}): {error_detail}")
            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. The AI service may be slow to respond.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection error. Make sure the backend server is running.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}:** {msg}")

# =======================
# FOOTER
# =======================
st.markdown("---")
st.markdown(
    "<center style='color:gray'>Built by <b>Mubashir Khan</b> • Streamlit x FastAPI</center>",
    unsafe_allow_html=True
)
