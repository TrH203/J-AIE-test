from enum import Enum
class ChatState(dict):
    query: str
    docs: list
    reasoning: str
    answer: str
    latency_ms: int
    chat_id: str
    enable_reasoning: bool
    
class LogsStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    OTHER = 'other'
    
class LogsActionType(str, Enum):
    LIST = 'list'
    SEARCH = 'search'
    UPSERT = 'upsert'
    DELETE = 'delete'
    CHAT = 'chat'
    UPDATE = 'updated'
    INSERT = 'inserted'