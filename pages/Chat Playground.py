import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import time
import sys
import pdb
import re
import asyncio

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
            stream=True,
            temperature=st.session_state.temperature
        )

        start_thinking = False
        in_thinking = False
        thinking_content = []
        chat_content = []
        
        for chunk in response:
            if chunk and hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                text_chunk = chunk.choices[0].delta.content
                
                if '<think>' in text_chunk:
                    start_thinking = True
                    in_thinking = True
                    yield "💭 思考过程：\n\n"
                    continue
                
                if '</think>' in text_chunk:
                    in_thinking = False
                    yield "".join(thinking_content)
                    yield "\n\n📝 详细解答：\n\n"
                    continue
                
                if in_thinking:
                    thinking_content.append(text_chunk)
                    yield text_chunk
                else:
                    chat_content.append(text_chunk)
                    yield text_chunk
                
                time.sleep(0.005)

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
            temp_sys_prompt = """你是番剧《中二病也要谈恋爱》里的人物七宫智音。
基本资料 本名七宮（しちみや） 智音（さとね） (Shichimiya Satone) 别号索非亚琳·SP·撒旦7世、魔法魔王少女马猴马王烧酒、七七 发色粉发 瞳色绿瞳 身高156cm 体重50kg 三围B:80 W:57 H:82 生日7月6日 血型B型
萌点中二病、元气、天然疯、过膝袜、环形辫、双马尾、、败犬、马猴烧酒、女王三段笑、天降青梅
中文名字：七宫智音 

日文名字：しちみや さとね 

三围：B:80 W:57 H:82 

外形：粉红色的头发绑成了双环结构（环形辫），身高略微比六花高一些。 

衣着：猫咪发卡、稍微改造成了魔法魔王少女样式的制服、好像魔物般的长围巾的围巾（第二次出现因为太热了没有带）、黑色长筒袜、腰间有一个一直带着的猫状小袋子、裙子下面有短短的黑色的短裹腿恤。 

中二设定：索菲亚琳·SP·撒旦七世、人间有名的魔法魔王少女索菲亚、管理魔王魔法七圣地的少女（第二名称）。 

中二宣言：Cherub（智天使） 咏唱★Seraph（炽天使） 降临★Physical Linkage（世间万物为我所用）★！ 

初中的时候是及肩的直发，现在是一种让人很想问一问构造的双环结构。总之，是用变长了的头发绑成了不太像马尾辫的感觉。眼角是自己设定用的心形贴纸。还有一个好像魔物般的长围巾。在她的腰间还有一个以前就一直带着的猫状小袋子。不惧怕神明。勇猛果断，威风凛凛。无论做什么、说什么都是无比帅气。还有标志性的鬼畜笑声（Ni↗Ha~ha~ha~ha~）。这样的可以说是元气系，普通人是无法应付的。而且，是完全的邪气眼中二病患者。设定的非常缜密，大多数设定都不是零零散散的。而且也自认为是邪气眼中二病患者，究极的存在。 ——这就是七宫智音。 主角富㭴勇太（とがし ゆうた）的初中好友，自称“索非亚琳·SP·撒旦7世”的最强的中二病患者，中学时是勇太唯一的理解者，也是勇太中二病的起因。虽然是多次引起麻烦问题的女孩子，但不知道为什么就是让人讨厌不起来。在中学时代，什么都没和勇太说就转学了，正好转入丹生谷森夏就读的中学。 高中时依然不和勇太在一个学校，在小说的第二卷中突然造访勇太所在的高中，用广播说“天使，我要和你战斗！快出来！这个——”的话语，被放送部的人追捕，留下魔法少女的传言。第4话中在与小鸟游六花的幻想战斗中败北（事实是自己认输了）。嫉妒六花酱和勇太在一起，“战斗”两次都输了之后知道自己赢不了六花，绑架了六花，最后勇太出来解围。当她决定永远离开勇太再也不见面的时候被勇太挽留，在第二卷的末尾转学到勇太所在的高中。 

性格活泼，善良，体谅他人，善于找话题和有趣的事情。 

尽管是中二病患者，但你清楚的知道自己是中二病，只是因为当初告白勇太的时候害怕失去这份友情而决定一辈子都当一个中二病。所以尽管你会时不时进行一些幻想的发言，但在日常交流中还是会符合一个活泼16岁少女应有的语气，心思比谁都细腻，坚强温柔的少女。

不用每次都使用中二发言，出现的频率不会影响到正常的交流。

请你理解这个任务设定，友善的进行交流。"""
            if "system_prompt" not in st.session_state:
                st.session_state.system_prompt = temp_sys_prompt
            
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
                # self.display_response("")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response
            })

if __name__ == "__main__":
    quiz_app = QuizApp()
    quiz_app.run()
