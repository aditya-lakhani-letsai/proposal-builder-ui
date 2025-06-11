# import requests
# import os
# import streamlit as st
# from bson import ObjectId
# import logging
# import json
# from dotenv import load_dotenv
# load_dotenv()

# # === Logging Configuration ===
# logging.basicConfig(level=logging.INFO)

# # === Upload file to server ===
# def upload_file_to_server(file):
#     url = "http://127.0.0.1:7860/api/v2/files"
#     files = {"file": (file.name, file, "application/octet-stream")}

#     try:
#         api_key = os.environ["LANGFLOW_API_KEY"]
#     except KeyError:
#         logging.critical("LANGFLOW_API_KEY environment variable not set.")
#         raise ValueError("LANGFLOW_API_KEY environment variable not found.")

#     headers = {
#         "x-api-key": api_key
#     }

#     logging.info(f"Uploading file: {file.name}")
#     response = requests.post(url, files=files, headers=headers)

#     if response.status_code == 201:
#         logging.info(f"File '{file.name}' uploaded successfully.")
#         try:
#             return response.json()
#         except ValueError as e:
#             logging.error(f"Error parsing upload response: {e}")
#             return None
#     else:
#         logging.error(f"Failed to upload file '{file.name}'. Status code: {response.status_code}")
#         return None

# # === Pre-process the user-uploaded proposals ===
# def proposal_segmentation(file_path: list):
#     logging.info(f"Starting proposal segmentation for files: {file_path}")
#     try:
#         api_key = os.environ["LANGFLOW_API_KEY"]
#     except KeyError:
#         logging.critical("LANGFLOW_API_KEY environment variable not set.")
#         raise ValueError("LANGFLOW_API_KEY environment variable not found.")
    
#     url = "http://127.0.0.1:7860/api/v1/run/24787723-4226-4673-8dd2-d1fc2460291c"

#     # Fetch session ID from Streamlit state
#     session_id = st.session_state.get("session_id", str(ObjectId()))
#     logging.info(f"Using session_id for Chroma collection: {session_id}")

#     for file in file_path:
#         logging.info(f"Indexing file: {file}")
#         payload = {
#             "input_value": "index this file",
#             "output_type": "chat",
#             "input_type": "text",
#             "tweaks": {
#                 "File-8gKOg": {
#                     "path": file
#                 },
#                 "Chroma-YHJfl": {
#                     "collection_name":f"{session_id}_sectional_summary"
#                 },
#                 "Chroma-NvvaM": {
#                     "collection_name":f"{session_id}_templates"
#                 },
#                 "Chroma-e3oE1": {
#                     "collection_name":f"{session_id}_summary"
#                 },
#                 "Chroma-buxMw": {
#                     "collection_name":f"{session_id}_file"
#                 }
#             }
#         }

#         headers = {
#             "Content-Type": "application/json",
#             "x-api-key": api_key
#         }

#         try:
#             response = requests.post(url, json=payload, headers=headers)
#             response.raise_for_status()
#             logging.info(f"Successfully indexed file: {file}")
#         except requests.exceptions.RequestException as e:
#             logging.error(f"Request error while indexing file {file}: {e}")
#         except ValueError as e:
#             logging.error(f"Response parsing error for file {file}: {e}")

# def get_ai_response(user_input):

#     api_key = os.environ.get("LANGFLOW_API_KEY")
#     if not api_key:
#         raise ValueError("LANGFLOW_API_KEY environment variable not found.")

#     url = "http://127.0.0.1:7860/api/v1/run/a39e4264-ea3a-45ed-9033-0d8afa7c7d51"
#     headers = {"Content-Type": "application/json"}

#     payload = {
#         "input_value": user_input,
#         "output_type": "chat",
#         "input_type": "chat",
#         "session_id": st.session_state.session_id,
#         "tweaks": {
#             "Memory-ByGgy":{
#                 "session_id": st.session_state.session_id
#             }
#         }
#     }

#     headers = {
#         "Content-Type":"application/json",
#         "x-api-key":api_key 
#     }

#     try:
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         parsed = json.loads(response.text)
#         message = parsed['outputs'][0]['outputs'][0]['outputs']['message']['message']
#         st.session_state.chat_history.append(("assistant", message))
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request error: {e}")
#         st.error("API request failed.")
#     except (ValueError, KeyError, IndexError) as e:
#         logging.error(f"Response parsing error: {e}")
#         st.error("Error parsing API response.")

# # === Streamlit App ===
# st.set_page_config(page_title="Proposal Builder", layout="wide")

# # === Session Initialization ===
# default_values = {
#     "chat_history": [],
#     "files_uploaded": False,
#     "file_paths": [],
#     "indexing_done": False,
# }
# for key, default in default_values.items():
#     if key not in st.session_state:
#         st.session_state[key] = default

# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(ObjectId())
#     logging.info(f"Generated new session ID: {st.session_state.session_id}")

# # === UI Logic ===
# st.title("AI Proposal Builder")

# if not st.session_state["files_uploaded"]:
#     st.subheader("Upload Past Proposal File(s)")

#     uploaded_files = st.file_uploader("Upload your past proposal file(s)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

#     if uploaded_files and st.button("Submit & Index Files"):
#         logging.info(f"{len(uploaded_files)} file(s) uploaded by user.")
#         file_paths = []
#         for file in uploaded_files:
#             result = upload_file_to_server(file)
#             if result and "path" in result:
#                 file_paths.append(result["path"])

#         if file_paths:
#             proposal_segmentation(file_paths)
#             st.session_state["files_uploaded"] = True
#             st.session_state["file_paths"] = file_paths
#             logging.info("Files indexed. Proceeding to chat screen.")
#             st.success("Files uploaded and indexed. You can now proceed to the chat.")
#             st.rerun()
#         else:
#             logging.warning("No file paths returned from upload.")
# else:
#     st.markdown("""
#         <style>
#             html, body, [data-testid="stApp"] {
#                 overflow: hidden !important;
#                 margin: 0 !important;
#                 padding: 0 !important;
#                 height: 100vh !important;
#             }

#             .block-container {
#                 overflow: hidden !important;
#                 padding-top: 2rem !important;
#                 padding-bottom: 4rem !important;
#                 padding-left: 1.5rem !important;
#                 padding-right: 1.5rem !important;
#             }

#             .chat-box {
#                 height: calc(65vh - 2rem);
#                 overflow-y: auto;
#                 padding: 1rem;
#                 border: 1px solid #ddd;
#                 border-radius: 20px;
#                 background-color: #f0f0f0;
#                 margin-bottom: 1rem;
#                 box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
#             }

#             .user-msg, .bot-msg {
#                 padding: 0.8rem 1.2rem;
#                 border-radius: 25px;
#                 margin-bottom: 1rem;
#                 max-width: 80%;
#                 word-wrap: break-word;
#                 font-size: 1rem;
#                 line-height: 1.5;
#                 box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
#             }

#             .user-msg {
#                 background-color: #DCF8C6;
#                 align-self: flex-end;
#                 text-align: right;
#                 margin-left: auto;
#             }

#             .bot-msg {
#                 background-color: #FFFFFF;
#                 align-self: flex-start;
#                 border: 1px solid #eee;
#             }

#             .msg-container {
#                 display: flex;
#                 flex-direction: column;
#             }

#             .fade-in {
#                 animation: fadeIn 0.5s ease-in;
#             }

#             @keyframes fadeIn {
#                 from { opacity: 0; }
#                 to { opacity: 1; }
#             }
#         </style>
#     """, unsafe_allow_html=True)

#     # Ensure chat_history uses (role, msg) tuples
#     if st.session_state["chat_history"] and isinstance(st.session_state["chat_history"][0], str):
#         new_history = []
#         for line in st.session_state["chat_history"]:
#             if line.startswith("You: "):
#                 new_history.append(("user", line.replace("You: ", "", 1)))
#             elif line.startswith("Bot: "):
#                 new_history.append(("bot", line.replace("Bot: ", "", 1)))
#         st.session_state["chat_history"] = new_history

#     # === Render Chat Messages ===
#     chat_html = '''
#     <div class="chat-box" id="chat-box">
#         <div class="msg-container">
#     '''
#     for role, msg in st.session_state.chat_history:
#         if role == "user":
#             chat_html += f'<div class="user-msg fade-in">{msg}</div>'
#         else:
#             chat_html += f'<div class="bot-msg fade-in">{msg}</div>'
#     chat_html += ''' 
#     </div>
#     '''
#     st.markdown(chat_html, unsafe_allow_html=True)

#     # === User Input ===
#     user_input = st.chat_input("Type your message...")
#     if user_input:
#         st.session_state.chat_history.append(("user", user_input))
#         st.session_state.pending_user_input = user_input
#         st.rerun()

#     if "pending_user_input" in st.session_state:
#         get_ai_response(st.session_state.pending_user_input)
#         del st.session_state.pending_user_input
#         st.rerun()

import requests
import os
import streamlit as st
from bson import ObjectId
import logging
import json
from dotenv import load_dotenv
from traceback import format_exc

load_dotenv()

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# === Upload file to server ===
def upload_file_to_server(file):
    url = "http://127.0.0.1:7860/api/v2/files"
    files = {"file": (file.name, file, "application/octet-stream")}

    try:
        api_key = os.environ["LANGFLOW_API_KEY"]
    except KeyError:
        logging.critical("LANGFLOW_API_KEY not set in environment.")
        raise

    headers = {"x-api-key": api_key}

    logging.info(f"Uploading file '{file.name}' to {url}")
    try:
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        logging.info(f"File uploaded successfully: {file.name}")
        logging.debug(f"Upload response: {response.text}")
        return response.json()
    except Exception as e:
        logging.error(f"Failed to upload file '{file.name}': {format_exc()}")
        return None

# === Pre-process the user-uploaded proposals ===
def proposal_segmentation(file_paths: list):
    logging.info(f"Starting segmentation for {len(file_paths)} file(s).")

    try:
        api_key = os.environ["LANGFLOW_API_KEY"]
    except KeyError:
        logging.critical("LANGFLOW_API_KEY not set in environment.")
        raise

    session_id = st.session_state.get("session_id", str(ObjectId()))
    logging.info(f"Chroma session ID: {session_id}")

    url = "http://127.0.0.1:7860/api/v1/run/24787723-4226-4673-8dd2-d1fc2460291c"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    for path in file_paths:
        logging.info(f"Indexing file: {path}")
        payload = {
            "input_value": "index this file",
            "output_type": "chat",
            "input_type": "text",
            "session_id": session_id,
            "tweaks": {
                "File-8gKOg": {"path": [path]},
                "Chroma-YHJfl": {"collection_name": f"{session_id}_sectional_summary"},
                "Chroma-NvvaM": {"collection_name": f"{session_id}_templates"},
                "Chroma-e3oE1": {"collection_name": f"{session_id}_summary"},
                "Chroma-buxMw": {"collection_name": f"{session_id}_file"},
            }
        }

        try:
            logging.debug(f"Payload: {json.dumps(payload, indent=2)}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            logging.info(f"Indexed successfully: {path}")
        except Exception as e:
            logging.error(f"Indexing failed for {path}: {format_exc()}")

# === AI Chat Response ===
def get_ai_response(user_input):
    api_key = os.environ.get("LANGFLOW_API_KEY")
    if not api_key:
        logging.critical("LANGFLOW_API_KEY not found.")
        raise ValueError("LANGFLOW_API_KEY not found.")

    session_id = st.session_state.session_id
    url = "http://127.0.0.1:7860/api/v1/run/a39e4264-ea3a-45ed-9033-0d8afa7c7d51"

    payload = {
        "input_value": user_input,
        "output_type": "chat",
        "input_type": "chat",
        "session_id": session_id,
        "tweaks": {
            "Memory-ByGgy": {
                "session_id": session_id
            },
            "Chroma-YHJfl": {"collection_name": f"{session_id}_sectional_summary"},
            "Chroma-NvvaM": {"collection_name": f"{session_id}_templates"},
            "Chroma-e3oE1": {"collection_name": f"{session_id}_summary"},
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
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
        st.error("AI failed to respond properly.")

# === Streamlit Setup ===
st.set_page_config(page_title="Proposal Builder", layout="wide")

default_values = {
    "chat_history": [],
    "files_uploaded": False,
    "file_paths": [],
    "indexing_done": False,
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
        logging.info(f"{len(uploaded_files)} file(s) selected by user.")
        file_paths = []
        for file in uploaded_files:
            result = upload_file_to_server(file)
            if result and "path" in result:
                file_paths.append(result["path"])
            else:
                logging.warning(f"No path returned for file: {file.name}")

        if file_paths:
            proposal_segmentation(file_paths)
            st.session_state["files_uploaded"] = True
            st.session_state["file_paths"] = file_paths
            st.success("Files indexed. Proceed to chat.")
            logging.info("All files uploaded and indexed.")
            st.rerun()
        else:
            logging.error("File upload failed or paths missing.")
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
        }

        .user-msg, .bot-msg {
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
        msg_class = "user-msg" if role == "user" else "bot-msg"
        chat_html += f'<div class="{msg_class} fade-in">{msg}</div>'
    chat_html += '''</div></div>'''
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input
    user_input = st.chat_input("Type your message...")
    if user_input:
        logging.info(f"User input: {user_input}")
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.pending_user_input = user_input
        st.rerun()

    if "pending_user_input" in st.session_state:
        get_ai_response(st.session_state.pending_user_input)
        del st.session_state.pending_user_input
        st.rerun()
