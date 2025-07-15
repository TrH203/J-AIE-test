class ChatState(dict):
    query: str
    docs: list
    reasoning: str
    answer: str
    latency_ms: int
    chat_id: str
    enable_reasoning: bool