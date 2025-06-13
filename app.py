import requests
import os
import streamlit as st
from bson import ObjectId
import logging
import json
import time
from traceback import format_exc

# ==== Logging Configuration ====
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === Upload file to server ===
def upload_file_to_server(file):
    url = "http://172.212.104.191:7860/api/v2/files"
    files = {"file": (file.name, file, "application/octet-stream")}

    logging.info(f"Uploading file '{file.name}' to {url}")
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        result = response.json()
        logging.info(f"File uploaded successfully: {file.name}")
        logging.debug(f"Upload response: {response.text}")
        return True, result
    except Exception as e:
        logging.error(f"Failed to upload file '{file.name}': {format_exc()}")
        return False, str(e)

# === Pre-process the user-uploaded proposals ===
def proposal_segmentation(file_paths: list):
    logging.info(f"Starting segmentation for {len(file_paths)} file(s).")

    session_id = st.session_state.get("session_id", str(ObjectId()))
    logging.info(f"Chroma session ID: {session_id}")

    url = "http://172.212.104.191:7860/api/v1/run/dc5b03b3-fbf4-4138-b062-b255b3d92708"

    headers = {
        "Content-Type": "application/json"
    }

    successful_indexings = []
    failed_indexings = []

    for path in file_paths:
        logging.info(f"Indexing file: {path}")
        payload = {
            "input_value": "index this file",
            "output_type": "chat",
            "input_type": "text",
            "session_id": session_id,
            "tweaks": {
                "File-RA5qA": {"path": [path]},
                "Chroma-J68Wh": {"collection_name": f"{session_id}_sectional_summary"},
                "Chroma-f9KL9": {"collection_name": f"{session_id}_templates"},
                "Chroma-2a8Oh": {"collection_name": f"{session_id}_summary"},
                "Chroma-YOqvu": {"collection_name": f"{session_id}_file"},
            }
        }
        try:
            logging.debug(f"Payload: {json.dumps(payload, indent=2)}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            successful_indexings.append(path)
            logging.info(f"Indexed successfully: {path}")
        except Exception as e:
            error_msg = f"Indexing failed for {path}: {format_exc()}"
            logging.error(error_msg)
            failed_indexings.append((path, str(e)))

    if successful_indexings:
        st.session_state["files_uploaded"] = True
        logging.info(f"Segmentation completed: {len(successful_indexings)} successful, {len(failed_indexings)} failed.")
    else:
        logging.error("No files were indexed successfully.")

    return successful_indexings, failed_indexings

# === AI Chat Response ===
def get_ai_response(user_input):
    session_id = st.session_state.session_id
    url = "http://172.212.104.191:7860/api/v1/run/ffa64877-77dd-4d20-9b4e-55640342713e"

    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat",
        "session_id": session_id,
        "tweaks": {
            "Memory-Ebik4": {
                "session_id": session_id
            },
            "Chroma-XBYmZ": {"collection_name": f"{session_id}_sectional_summary"},
            "Chroma-qIpQj": {"collection_name": f"{session_id}_templates"},
            "Chroma-3HjaI": {"collection_name": f"{session_id}_summary"},
            "Chroma-8YxKQ": {"collection_name": f"{session_id}_file"}
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    logging.info(f"Posting user input to API: {user_input}")
    logging.debug(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        parsed = response.json()

        message = parsed['outputs'][0]['outputs'][0]['outputs']['message']['message']
        st.session_state.chat_history.append(("assistant", message))

        logging.info("Assistant response received successfully.")
        logging.debug(f"Assistant message: {message}")
    except Exception as e:
        logging.error(f"AI response error: {format_exc()}")
        st.session_state.chat_history.append(("assistant", "AI failed to respond properly."))

def scroll_chatbox():
    dummy_scroll_key = len(st.session_state.chat_history)
    st.components.v1.html(f"""
        <script>
            function scrollToBottom(dummy) {{
                const chatBoxes = window.parent.document.querySelectorAll('.chat-box');
                chatBoxes.forEach(box => {{
                    box.scrollTop = box.scrollHeight;
                }});
            }}
            setTimeout(() => scrollToBottom({dummy_scroll_key}), 100);
        </script>
    """, height=0)

def pause_and_rerun(seconds=2, state_flag="pause_done"):
    if st.session_state.get(state_flag) is False:
        time.sleep(seconds)
        st.session_state[state_flag] = True
        st.rerun()

# === Streamlit Setup ===
st.set_page_config(page_title="Proposal Builder", layout="wide")

default_values = {
    "chat_history": [],
    "files_uploaded": False,
    "file_paths": [],
}
for key, default in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = default

if "session_id" not in st.session_state:
    st.session_state.session_id = str(ObjectId())
    logging.info(f"Generated new session ID: {st.session_state.session_id}")

# === UI ===
st.title("AI Proposal Builder")

if not st.session_state["files_uploaded"]:
    st.subheader("Upload Past Proposal File(s)")

    uploaded_files = st.file_uploader("Upload files", type=["pdf", "docx", "txt"], accept_multiple_files=True)

    if uploaded_files and st.button("Submit & Index Files"):
        with st.spinner("Hang tight, we're processing your proposals...", show_time=True):
            logging.info(f"{len(uploaded_files)} file(s) selected by user.")
            uploaded_successfully = []
            upload_failed = []
            file_paths = []

            for file in uploaded_files:
                success, result = upload_file_to_server(file)
                if success and "path" in result:
                    file_paths.append(result["path"])
                    uploaded_successfully.append(file.name)
                else:
                    upload_failed.append(file.name)

            if file_paths:
                successful_indexings, failed_indexings = proposal_segmentation(file_paths)
                if successful_indexings:
                    st.session_state["file_paths"] = successful_indexings
                    if upload_failed or failed_indexings:
                        st.warning("Some files failed to process:")
                        if upload_failed:
                            for failure in upload_failed:
                                st.write(f"Failed to upload: {failure}")
                        if failed_indexings:
                            for path, error in failed_indexings:
                                st.write(f"Failed to index: {path} - {error}")
                else:
                    st.error("No files were indexed successfully.")
                    for path, error in failed_indexings:
                        st.write(f"Failed to index: {path} - {error}")
            else:
                st.error("No files were uploaded successfully.")
                for failure in upload_failed:
                    st.write(f"Failed to upload: {failure}")
        st.success("Processing done, proceeding to chat.")
        st.session_state["pause_done"] = False
        pause_and_rerun()

else:
    # Custom Chat UI CSS
    st.markdown("""
    <style>
        html, body, [data-testid="stApp"] {
            overflow: hidden !important;
            margin: 0 !important;
            padding: 0 !important;
            height: 100vh !important;
        }

        .block-container {
            overflow: hidden !important;
            padding-top: 2rem !important;
            padding-bottom: 4rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        .chat-box {
            height: calc(65vh - 2rem);
            overflow-y: auto;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 20px;
            background-color: #f0f0f0;
            margin-bottom: 1rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            scroll-behavior: smooth;
        }

        .user-msg, .bot-msg, .loading-msg {
            padding: 0.8rem 1.2rem;
            border-radius: 25px;
            margin-bottom: 1rem;
            max-width: 80%;
            word-wrap: break-word;
            font-size: 1rem;
            line-height: 1.5;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        }

        .user-msg {
            background-color: #DCF8C6;
            align-self: flex-end;
            text-align: right;
            margin-left: auto;
        }

        .bot-msg {
            background-color: #FFFFFF;
            align-self: flex-start;
            border: 1px solid #eee;
        }

        .loading-msg {
            background-color: #E8ECEF;
            align-self: flex-start;
            border: 1px solid #ddd;
            font-style: italic;
            color: #555;
            display: flex;
            align-items: center;
        }

        .loading-msg::before {
            content: '';
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #555;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
        }

        .msg-container {
            display: flex;
            flex-direction: column;
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state["chat_history"] and isinstance(st.session_state["chat_history"][0], str):
        # Convert raw lines to structured tuples
        new_history = []
        for line in st.session_state["chat_history"]:
            if line.startswith("You: "):
                new_history.append(("user", line.replace("You: ", "")))
            elif line.startswith("Bot: "):
                new_history.append(("assistant", line.replace("Bot: ", "")))
        st.session_state["chat_history"] = new_history

    # Render chat
    chat_html = '''
    <div class="chat-box" id="chat-box"><div class="msg-container">
    '''
    for role, msg in st.session_state.chat_history:
        if role == "user":
            msg_class = "user-msg"
        elif role == "loading":
            msg_class = "loading-msg"
        else:
            msg_class = "bot-msg"
        chat_html += f'<div class="{msg_class} fade-in">{msg}</div>'
    chat_html += '''</div></div>'''
    st.markdown(chat_html, unsafe_allow_html=True)

    scroll_chatbox()

    # Input
    user_input = st.chat_input("Type your message...")
    if user_input:
        logging.info(f"User input: {user_input}")
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.pending_user_input = user_input
        st.session_state.chat_history.append(("loading", " "))
        st.rerun()

    if "pending_user_input" in st.session_state:
        # Remove the loading message
        if st.session_state.chat_history and st.session_state.chat_history[-1][0] == "loading":
            st.session_state.chat_history.pop()
        get_ai_response(st.session_state.pending_user_input)
        del st.session_state.pending_user_input
        st.rerun()
