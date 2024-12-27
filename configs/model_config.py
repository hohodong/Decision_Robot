import os

# 可以指定一个绝对路径，统一存放所有的Embedding和LLM模型。
# 每个模型可以是一个单独的目录，也可以是某个目录下的二级子目录。
# 如果模型目录名称和 MODEL_PATH 中的 key 或 value 相同，程序会自动检测加载，无需修改 MODEL_PATH 中的路径。
MODEL_ROOT_PATH = ""

# 选用的 Embedding 名称
EMBEDDING_MODEL = "bge-m3"

# Embedding 模型运行设备。设为 "auto" 会自动检测(会有警告)，也可手动设定为 "cuda","mps","cpu","xpu" 其中之一。
EMBEDDING_DEVICE = "auto"

# 选用的reranker模型
RERANKER_MODEL = "bce-reranker-base"
# 是否启用reranker模型
USE_RERANKER = False
RERANKER_MAX_LENGTH = 1024

# 如果需要在 EMBEDDING_MODEL 中增加自定义的关键字时配置
EMBEDDING_KEYWORD_FILE = "keywords.txt"
EMBEDDING_MODEL_OUTPUT_PATH = "output"

# 要运行的 LLM 名称，可以包括本地模型和在线模型。列表中本地模型将在启动项目时全部加载。
# 列表中第一个模型将作为 API 和 WEBUI 的默认模型。

LLM_MODELS = ["openai-api"]
Agent_MODEL = None

# LLM 模型运行设备。设为"auto"会自动检测(会有警告)，也可手动设定为 "cuda","mps","cpu","xpu" 其中之一。
LLM_DEVICE = "auto"

HISTORY_LEN = 3

MAX_TOKENS = 2048

TEMPERATURE = 0.7

ONLINE_LLM_MODEL = {
    "openai-api": {
        "model_name": "/root/models/internlm2_5-7b-chat",
        "api_base_url": "http://0.0.0.0:23333/v1",
        "api_key": "fake",
    },

}

# 在以下字典中修改属性值，以指定本地embedding模型存储位置。支持3种设置方法：
# 1、将对应的值修改为模型绝对路径
# 2、不修改此处的值（以 text2vec 为例）：
#       2.1 如果{MODEL_ROOT_PATH}下存在如下任一子目录：
#           - text2vec
#           - GanymedeNil/text2vec-large-chinese
#           - text2vec-large-chinese
#       2.2 如果以上本地路径不存在，则使用huggingface模型

MODEL_PATH = {
    "embed_model": {
        "bge-m3": "BAAI/bge-m3",
    },

    "llm_model": {
        "internlm-7b": "internlm/internlm-7b",
        "internlm-chat-7b": "internlm/internlm-chat-7b",
        "internlm2-chat-7b": "internlm/internlm2-chat-7b",
        "internlm2-chat-20b": "internlm/internlm2-chat-20b",
    },

    "reranker": {
        "bge-reranker-large": "BAAI/bge-reranker-large",
        "bge-reranker-base": "BAAI/bge-reranker-base",
        "bce-reranker-base": "/root/models/bce-reranker-base_v1",
    }
}


# nltk 模型存储路径
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nltk_data")

SUPPORT_AGENT_MODEL = [
    "openai-api",  # openai 接口模型
    "internlm2_5-20b-chat", # Internlm系列本地模型
]
