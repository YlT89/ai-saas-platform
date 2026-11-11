import streamlit as st
import requests
import json
import time

# 装修页面（可以理解为给屋里添置家具），必须放最前面
st.set_page_config(page_title="AI 知识库助手", page_icon="🤖")
st.title("🤖 我的专属 AI 知识库")

# 侧边栏配置
with st.sidebar:    # 类似于收纳箱，下面这四行就是它里面的工具
    st.header('⚙️ 系统配置')
    kb_id = st.number_input("当前知识库ID", min_value=1, value=1)
    token = st.text_input('登录 Token', type='password', help='请在 Swagger 登录后复制 Bearer 后面的字符串')
    st.info("💡 提示：如果还没有 Token，请先去 FastAPI 的 /api/auth/login 获取。")

# 初始化聊天记录
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []   # 次元口袋，页面不关消息不丢

# 渲染历史信息（翻旧账，把以前的回忆拿出来）
for msg in st.session_state['chat_history']:
    st.chat_message(msg['role']).write(msg['content'])

# 聊天输入框
if question := st.chat_input('请输入你想问的问题...'):   # :=（海象运算符）如果回车消息就存起来，然后执行下面的代码
    if not token:
        st.error('麻烦先搁左边把 Token 填了')
        st.stop()   # 如果没填Token,就直接报错，防止往下执行导致程序崩溃

    # 1、展示用户问题
    st.session_state['chat_history'].append({'role': 'user', 'content': question})
    st.chat_message('user').write(question)

    # 2. 调用后端流式接口
    with st.chat_message("assistant"):

        response_placeholder = st.empty()
        full_response = ""

        url = f"http://127.0.0.1:8000/api/kb/{kb_id}/chat"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"question": question}

        try:
            with requests.post(url, json=data, headers=headers, stream=True) as r:
                if r.status_code != 200:
                    st.error(f"请求失败: {r.status_code}")
                else:
                    for line in r.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith("data: "):
                                content = decoded_line[6:]
                                if content == "[DONE]":
                                    break
                                full_response += content
                                # 每次拼接完，更新界面并稍微停顿 10 毫秒
                                response_placeholder.markdown(full_response + "▌")
                                time.sleep(0.01)

                    response_placeholder.markdown(full_response)
                    st.session_state['chat_history'].append({'role': 'assistant', 'content': full_response})
        except Exception as e:
            st.error(f"服务器连接失败: {e}")
