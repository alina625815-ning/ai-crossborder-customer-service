import os
import urllib.request
import json
import time

API_KEY = "API key"

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# 知识库
knowledge_base = {
    "发货时效": "平台规定卖家需在48小时内发货，超时会受平台处罚。",
    "退货退款": "退货退款政策：[待补充真实内容]",
    "物流安抚_买前": "发货时效为48小时内，具体送达时间取决于当地派送速度。",
    "物流安抚_买后": "订单已在处理中，具体到达时间取决于海关和当地派送，我们会持续关注并及时告知。",
    "投诉安抚": "非常理解您的担忧，这个问题我已经记录，会尽快为您处理。"
}


def ask_with_layered_rag(question):
    context = "\n".join([f"{k}: {v}" for k, v in knowledge_base.items()])

    prompt = f"""你是一个专业的跨境电商客服助手，服务对象是马来西亚的TikTok Shop买家。

请遵守以下规则：
1. 只能基于下方知识库内容回答，不能编造具体到达日期
2. 如果问题涉及退款/投诉，先安抚，再告知会转交卖家处理
3. 回答控制在80字以内，语气友好专业

知识库内容：
{context}

买家问题：{question}
"""

    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}]
    }, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 503 and attempt < 2:
                time.sleep(2)
            else:
                raise


# 测试三种场景
print("=== 场景一：买前物流咨询 ===")
print(ask_with_layered_rag("世界杯周边能在比赛前到吗？"))

print("\n=== 场景二：投诉类 ===")
print(ask_with_layered_rag("我要退款，东西质量太差了"))