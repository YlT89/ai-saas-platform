# pip install langgraph
from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1、定义状态（图例传递的数据）
class GraphState(TypedDict):
    question: str
    context: str

# 2、定义节点 A （假装去查了库）
def retrieve_node(state: GraphState):
    print("--- 直接回答，不查库 ---")
    return {"context": "查到的前端知识是：Vue/React"}

# 3、定义节点 B (假装直接回答)
def direct_node(state: GraphState):
    print("--- 直接回答，不查库 ---")
    return {"context": "无上下文"}

# 4、定义路由逻辑（关键：大模型或关键字决定走向）
def router(state: GraphState):
    if "前端" in state["question"]:
        return "retrieve"   # 去查库
    return "direct"         # 直接回

# 5、组装图
workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("direct", direct_node)

# 设定入口和路由
workflow.set_conditional_entry_point(router)
workflow.add_edge("retrieve", END)
workflow.add_edge("direct", END)

app = workflow.compile()

# 测试运行
print(app.invoke({"question": "前端是什么？"}))

# 终端python test_graph.py