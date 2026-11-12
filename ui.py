import streamlit as st
import requests
import json
import time
import os

# 默认使用本地地址，如果服务器 Docker 注入了 API_BASE_URL 环境变量，就用 Docker 里的地址
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")



# 装修页面（可以理解为给屋里添置家具），必须放最前面
st.set_page_config(page_title="AI 知识库助手", page_icon="🤖")
st.title("🤖 我的专属 AI 知识库")

# 侧边栏配置
with st.sidebar:    # 类似于收纳箱，下面这四行就是它里面的工具
    st.header('⚙️ 系统配置')
    kb_id = st.number_input("当前知识库ID", min_value=1, value=1)
    token = st.text_input('登录 Token', type='password', help='请在 Swagger 登录后复制 Bearer 后面的字符串')
    st.info("💡 提示：如果还没有 Token，请先去 FastAPI 的 /api/auth/login 获取。")
    st.divider()
    st.subheader('📁 上传知识库文档')

    # 1、文件上传组件
    uploaded_file = st.file_uploader('选择 txt / pdf 文件', type=['txt', 'pdf'])

    # 2、上传按钮
    if st.button('开始上传并解析', use_container_width=True):
        if not uploaded_file:
            st.warning('选个文件呗伙计...')
        elif not token:
            st.warning('哥们 Token 没写')
        else:
            # 准备发给后端的 multipart
            files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/octet-stream')}
            headers = {"Authorization": f"Bearer {token}"}

            # 3、发给 FastAPI
            with st.spinner('文件上传中...'):
                try:
                    res = requests.post(
                        url = f"{API_BASE_URL}/api/kb/{kb_id}/upload",
                        files=files,
                        headers=headers,
                        timeout=10
                    )
                    if res.status_code != 200:
                        st.error(f"上传失败，状态码: {res.status_code}")
                        st.write(f"后端返回类型: {type(res)}")  # 看看它到底是个啥
                        st.stop()
                    task_data = res.json()
                    task_id = task_data.get('task_id')
                    if not task_id:
                        st.error(f"后端没返回 task_id: {task_data}")
                        st.stop()
                    st.success('上传成功了~ 稍等后台正在处理...')

                    # 4、轮询查询进度（放进一个状态圈里）
                    with st.status('AI 正在拼命切分和向量化...', expanded=True) as status:
                        while True:
                            try:
                                # 调用时后端状态查询窗口（确保路径一致）
                                status_res = requests.get(
                                    url = f"{API_BASE_URL}/api/kb/{kb_id}/task/{task_id}/status",
                                    headers=headers,
                                    timeout=5
                                )
                                if status_res.status_code != 200:
                                    status.update(label='查询状态失败', state='error')
                                    st.error(f"查询失败: {status_res.text}")
                                    break
                                state = status_res.json().get('status')

                                if state == 'SUCCESS':
                                    st.write('弄完了，来聊天吧~')
                                    status.update(label='解析完成', state='complete', expanded=False)
                                    break
                                elif state == 'FAILURE':
                                    st.write('吆喝失败了，去看看后端日志')
                                    status.update(label='解析失败', state='error')
                                    break
                                else:
                                    # 状态是 'STARTED' 或者 'PENDING' 等，继续等
                                    status.update(label=f'AI 正在处理中... (当前状态: {state})', state='running')
                                    time.sleep(3)   # 间隔三秒查询一次
                            except requests.exceptions.RequestException as req_err:
                                    status.update(label='网络请求异常', state='error')
                                    st.error(f'查询进度网络断开: {req_err}')
                                    break

                except Exception as e:
                    st.error(f'上传请求报错: {e}')


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

        url = f"{API_BASE_URL}/api/kb/{kb_id}/chat"
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

