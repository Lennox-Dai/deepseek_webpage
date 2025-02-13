import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import time
import sys
import pdb
import re

import streamlit as st
from openai import OpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

class QuizApp:
    def __init__(self):

        """Initialize the quiz application with modern styling."""
        # Configure page with wider layout
        self._setup_page_config()

        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.deepinfra.com/v1/openai")
        if not OPENAI_API_KEY:
            pdb.set_trace()
            raise EnvironmentError(
                "OPENAI_API_KEY not found in environment variables.")
        os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

        # Load custom CSS
        self._load_custom_css()
        self.round = 2
        self.mode = "Report"

    def _setup_page_config(self):
        """Configure page settings and style."""
        st.set_page_config(
            page_title="Chat Playground", 
            page_icon="🧩", 
            layout="wide"
        )
        # Custom CSS for enhanced styling
        st.markdown("""
        <style>
        .stApp {
            background-color: #f0f2f6;
        }
        .stTextArea, .stTextInput {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .highlight-box {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

    def _load_custom_css(self):
        """Load custom CSS for styling the Streamlit app with enhanced font styling."""
        st.markdown("""
        <style>
        /* Background and overall app styling */
        .stApp {
            background-color: #f0f2f6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Input areas styling */
        .stTextArea textarea, .stTextInput input {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            font-size: 16px;
            color: #333;
            padding: 10px;
            transition: all 0.3s ease;
        }

        /* Input areas focus state */
        .stTextArea textarea:focus, .stTextInput input:focus {
            border-color: #4CAF50;
            box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
            outline: none;
        }

        /* Placeholder text styling */
        .stTextArea textarea::placeholder, .stTextInput input::placeholder {
            color: #888;
            font-style: italic;
        }

        /* Button styling */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }

        .stButton>button:hover {
            background-color: #45a049;
        }

        /* Additional styling for labels and headers */
        .stMarkdown h4 {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #2c3e50;
            font-weight: 600;
        }
        </style>
        """, unsafe_allow_html=True)

    # def response_generator(self, history_message):
    #     response = self.client.chat.completions.create(
    #         model="deepseek-ai/DeepSeek-R1",
    #         messages=st.session_state.messages,
    #         stream=False,
    #         temperature=st.session_state.temperature
    #     )
        
    #     response = response.choices[0].message.content
    #     if isinstance(response, str):
    #         think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    #         main_content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    #         think_content = think_match.group(1).strip()
    #         response = f"""💭 **思考过程：** {think_content}\n  📝 **详细解答：** {main_content}"""
            
    #     for line in response.split('\n'):
    #         yield line + "\n"
    #         time.sleep(0.05)

    def response_generator(self, history_message):
        response = self.client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=st.session_state.messages,
            stream=False,
            temperature=st.session_state.temperature
        )
        
        response = response.choices[0].message.content
        if isinstance(response, str):
            think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
            main_content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            
            if think_match:
                think_content = think_match.group(1).strip()
    #             formatted_response = f"""💭 **思考过程：**

    # *{think_content}*

    # 📝 **详细解答：**

    # {main_content}"""
                formatted_response = f"""💭 思考过程：

{think_content}

📝 详细解答：

{main_content}"""
            else:
                formatted_response = main_content
                
            chunk_size = 3  
            for i in range(0, len(formatted_response), chunk_size):
                chunk = formatted_response[i:i + chunk_size]
                yield chunk
                time.sleep(0.02) 

    def run(self):
        st.title("🧩 Chat Playground")
        st.markdown("**没有限制上下文窗口的context长度,需要的话可以设置**")
        
        with st.sidebar:
            st.header("设置")
            
            if "temperature" not in st.session_state:
                st.session_state.temperature = 1.3
            
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.temperature,
                step=0.1,
                help="较高的值（如1.3）会使输出更加随机，较低的值（如0.2）会使其更加集中和确定"
            )
            
            # System prompt input
            if "system_prompt" not in st.session_state:
                st.session_state.system_prompt = "你是一个可靠的知识助手，尽可能详细的分析和解决用户的问题"
            
            new_system_prompt = st.text_area(
                "System Prompt",
                value=st.session_state.system_prompt,
                help="设置AI助手的行为和角色指令"
            )
            
            if new_system_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_system_prompt
                st.session_state.messages = []
                st.rerun()
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if not st.session_state.messages:
            st.session_state.messages = [
                {"role": "system", "content": st.session_state.system_prompt}
            ]
        
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        if prompt := st.chat_input("试着输入一些内容"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                response = st.write_stream(self.response_generator(prompt))
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response
            })
#     def response_generator(self, history_message):

#         response = self.client.chat.completions.create(
#             model="deepseek-ai/DeepSeek-R1",
#             messages=st.session_state.messages,
#             stream=False,
#             temperature=1.3
#         )

#         response = response.choices[0].message.content

#         if isinstance(response, str):
#             think_match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
#             main_content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
#             think_content = think_match.group(1).strip()
#             response = f"""💭 **思考过程：**
# *{think_content}*\n

# 📝 **详细解答：**
# {main_content}"""
                        
#         for word in response.split():
#             yield word + " "
#             time.sleep(0.05)

#     def run(self):
#         st.title("🧩 Chat Playground")
#         st.markdown("**没有限制上下文窗口的context长度,需要的话可以设置**")

#         # history_message = []
        
#         if "messages" not in st.session_state:
#             st.session_state.messages = []
#                 # {"role": "system", "content": "你是一个可靠的知识助手，尽可能详细的分析和解决用户的问题"}

#         for message in st.session_state.messages:
#             with st.chat_message(message["role"]):
#                 if message["role"] != "system":
#                     st.markdown(message["content"])

#         if prompt := st.chat_input("试着输入一些内容"):
#             st.session_state.messages.append({"role": "user", "content": prompt})
#             with st.chat_message("user"):
#                 st.markdown(prompt)

#             with st.chat_message("assistant"):
#                 response = st.write_stream(self.response_generator(prompt))

#             st.session_state.messages.append({
#                 "role": "assistant", 
#                 "content": response
#             })


if __name__ == "__main__":
    quiz_app = QuizApp()
    quiz_app.run()
