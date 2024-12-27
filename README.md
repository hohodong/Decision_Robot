持续更新中

# 应急决策支持系统
本项目旨在构建一个基于InternLM大模型的应急决策支持系统，目的在于有效地结合实时态势数据和已有专业知识，生成规范可靠的应急方案，为决策者提供准确、实时和系统的决策支持，确保决策过程高效、有序进行。

本项目技术架构图如图：

![系统架构图](https://github.com/user-attachments/assets/d3b50f89-4570-40d5-b3bb-89df791de787)


# 本地部署方案
```bash
# 使用conda创建环境
$ conda create -n env_name python=3.10
$ conda activate env_name # Activate the environment
# 安装全部依赖
$ pip install -r requirements_webui.txt
```

## 模型下载
将项目所需的模型下载至本地，通常开源 LLM 与 Embedding 模型可以在 HuggingFace 或者 ModelScope 下载。
以 LLM 模型 Shanghai_AI_Laboratory/internlm2_5-7b-chat 与 Embedding 模型 BAAI/bge-m3 为例，
下载模型需要先安装Git LFS，然后运行

```bash
$ git lfs install
$ git clone https://www.modelscope.cn/Shanghai_AI_Laboratory/internlm2_5-7b-chat.git
$ git clone https://www.modelscope.cn/BAAI/bge-m3.git
```

## 启动项目
一键启动脚本 startup.py， 一键启动所有 Fastchat 服务、API 服务、WebUI 服务，示例代码：
```bash
$ python startup.py --all-webui
```


## 开源协议

本项目基于 [Apache-2.0](LICENSE) 协议开源



## 引用
本项目参考了以下开源项目，特此致谢：
```
@software{langchain_chatchat,
    title        = {{langchain-chatchat}},
    author       = {Liu, Qian and Song, Jinke, and Huang, Zhiguo, and Zhang, Yuxuan, and glide-the, and liunux4odoo},
    year         = 2024,
    journal      = {GitHub repository},
    publisher    = {GitHub},
    howpublished = {\url{https://github.com/chatchat-space/Langchain-Chatchat}}
}
```





