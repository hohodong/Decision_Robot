import os
import asyncio
import json
import re
import requests
import streamlit as st
from streamlit_chatbox import *
from webui_pages.utils import *

from lagent.agents import Agent
from lagent.prompts.parsers import PluginParser
from lagent.agents.stream import PLUGIN_CN, get_plugin_prompt
from lagent.schema import AgentMessage, ActionReturn
from lagent.hooks import Hook
from lagent.llms import GPTAPI

from fastapi import HTTPException
from server.chat.utils import History
from lagent.actions import ArxivSearch, WeatherQuery
from lagent.agents.stream import INTERPRETER_CN, META_CN, PLUGIN_CN, AgentForInternLM, get_plugin_prompt, AgentMessage

YOUR_TOKEN_HERE = "fake"
# YOUR_TOKEN_HERE = os.getenv('token')
if not YOUR_TOKEN_HERE:
    raise EnvironmentError("未找到环境变量 'token'，请设置后再运行程序。")

# Hook类，用于对消息添加前缀
class PrefixedMessageHook(Hook):
    def __init__(self, prefix, senders=None):
        """
        初始化Hook
        :param prefix: 消息前缀
        :param senders: 指定发送者列表
        """
        self.prefix = prefix
        self.senders = senders or []

    def before_agent(self, agent, messages, session_id):
        """
        在代理处理消息前修改消息内容
        :param agent: 当前代理
        :param messages: 消息列表
        :param session_id: 会话ID
        """
        for message in messages:
            if message.sender in self.senders:
                message.content = self.prefix + message.content

class AsyncPlanner:
    """方案生成类，整合写作者和批评者。"""

    def __init__(self, model_type, api_base, writer_prompt, critic_prompt, critic_prefix='', extract_prompt='', extract_prefix='', max_turn=2):
        """
        初始化方案生成器
        :param model_type: 模型类型
        :param api_base: API 基地址
        :param writer_prompt: 写作者提示词
        :param critic_prompt: 批评者提示词
        :param critic_prefix: 批评消息前缀
        :param extract_prompt: 提取消息提示词
        :param extract_prefix: 提取消息前缀
        :param max_turn: 最大轮次
        """
        self.model_type = model_type
        self.api_base = api_base
        self.llm = GPTAPI(
            model_type=model_type,
            api_base=api_base,
            key=YOUR_TOKEN_HERE,
            max_new_tokens=4096,
        )
        self.plugins = [dict(type='lagent.actions.WeatherQuery')]
        self.writer = Agent(
            self.llm,
            writer_prompt,
            name='写作者',
            output_format=dict(
                type=PluginParser,
                template=PLUGIN_CN,
                prompt=get_plugin_prompt(self.plugins)
            )
        )
        self.critic = Agent(
            self.llm,
            critic_prompt,
            name='批评者',
            hooks=[PrefixedMessageHook(critic_prefix, ['user'])]
        )
        self.extract = Agent(
            self.llm,
            extract_prompt,
            name="提取者",
            # hooks=[PrefixedMessageHook(extract_prefix, ['user'])]
        )
        self.max_turn = max_turn

    async def forward(self, message: AgentMessage,
                       chat_box: ChatBox, first_plan: str):
        """
        执行多阶段方案生成流程
        :param message: 初始消息
        :param update_placeholder: Streamlit占位符
        :return: 最终优化的方案内容
        """

        text = ""
        feedback = "无"
        weather_results = "未提供天气信息"
        # 第一步：生成初始内容
        text = "**Step 1: 生成初始内容...**\n\n" + first_plan + "\n\n"
        chat_box.update_msg(text, element_index=0, streaming=False)

        # 第二步：批评者提供反馈
        text = "\n**Step 2: 批评者正在提供反馈...**\n"
        message = self.critic(message)

        if message.content:
            # 解析批评者反馈
            message_for_extract_place = AgentMessage(
                sender='user',
                content=f"对于内容：{message.content} \n 请你提取出《事件发生的地点》并且不带任何前缀直接输出"
            )
            message_for_extract_advice = AgentMessage(
                sender='user',
                content=f"对于内容：{message.content} \n 请你提取出《批评建议》并且不带任何前缀直接输出"
            )
            keywords = self.extract(message_for_extract_place)
            suggestions = self.extract(message_for_extract_advice)
            feedback = suggestions.content if suggestions.content else "未提供批评建议"
            keywords = keywords.content if keywords.content else "海南省海口市"
            # print(keywords)
            # print(feedback)
            # 天气查询
            weather_search = WeatherQuery()
            weather_data = weather_search.run(keywords)
            weather_data = weather_data['result']
            weather_results = f"天气：{weather_data['weather']}，温度：{weather_data['temperature']}， 风向：{weather_data['wind_direction']}， 风速：{weather_data['wind_speed']}， 湿度：{weather_data['humidity']}"

            # 显示天气信息和批评建议
            text += f"\n**当地天气**:\n\n{weather_results}\n"
            text += f"\n**批评建议**:\n\n{feedback}\n"
        else:
            
            text += "**批评内容为空，请检查批评逻辑。**\n"

        chat_box.update_msg(text, element_index=0, streaming=False)
        # print(message.content)

        # 第三步：写作者根据反馈优化内容
        text = "\n**Step 3: 根据反馈改进内容...**\n"
        improvement_prompt = AgentMessage(
            sender="critic",
            content=(
                f"初步得到的应急方案是：{first_plan}\n\n"
                f"当地天气：\n{weather_results}\n\n"
                f"反馈建议：\n{feedback}\n\n"
                f"根据当地天气和反馈建议对内容进行改进，使其更加符合当前实际环境。"
            ),
        )
        message = self.writer(improvement_prompt)
        if message.content:
            text += f"\n**最终优化的应急方案**:\n\n{message.content}\n"
            print(message.content)
        else:
            text += "\n**最终优化的应急方案为空，请检查生成逻辑。**\n"
        
        chat_box.update_msg(text, element_index=0, streaming=False)

        return message


api_base="http://0.0.0.0:23333/v1/chat/completions"
model_type="/root/models/internlm2_5-7b-chat"



class MultiAgent:

    def __init__(self, chat_box: ChatBox, api: ApiRequest) -> None:
        self.chat_box = chat_box
        self.api = api
        # 初始化提示词
        self.meta_prompt = META_CN
        self.plugin_prompt = PLUGIN_CN
        # 初始化插件列表
        action_list = [
            ArxivSearch(),
            WeatherQuery(),
        ]
        plugin_map = {action.name: action for action in action_list}
        plugin_name = list(plugin_map.keys())
        # 根据选择的插件生成插件操作列表
        self.plugin_action = [plugin_map[name] for name in plugin_name]

        # 动态生成插件提示
        if self.plugin_action:
            self.plugin_prompt = get_plugin_prompt(self.plugin_action)

        # 获取模型和插件信息
        self.plugins = [dict(type=f"lagent.actions.{plugin.__class__.__name__}") for plugin in self.plugin_action]

        """初始化 GPTAPI 实例作为 chatbot。"""
        
        # 创建完整的 meta_prompt，保留原始结构并动态插入侧边栏配置
        meta_prompt = [
            {"role": "system", "content": self.meta_prompt, "api_role": "system"},
            {"role": "user", "content": "", "api_role": "user"},
            {"role": "assistant", "content": self.plugin_prompt, "api_role": "assistant"},
            {"role": "environment", "content": "", "api_role": "environment"}
        ]

        self.api_model = GPTAPI(
            model_type="internlm2.5-latest",
            api_base=api_base,
            key=YOUR_TOKEN_HERE,  # 在环境变量中获取授权令牌
            meta_template=meta_prompt,
            max_new_tokens=512,
            temperature=0.8,
            top_p=0.9
        )


    def multi_agent_answer(self, query: str, selected_kb: str, kb_top_k: int, score_threshold: float, history: List[Dict], llm_model: str, prompt_template_name: str, temperature: float) -> str:
        """
        主函数：处理用户交互
        """

        topic = query


        if (
            'blogger' not in st.session_state or
            st.session_state['model_type'] != model_type or
            st.session_state['api_base'] != api_base
        ):
            st.session_state['blogger'] = AsyncPlanner(
                model_type=model_type,
                api_base=api_base,
                writer_prompt="你是一位优秀的应急管理指挥员，善于针对应急问题给出合理的解决方案",
                critic_prompt="你是一位经验丰富的应急指挥员，面对应急问题和初步方案，善于根据当地的天气对初步方案给出改进建议",
                critic_prefix="""面对应急问题和初步方案，请你首先提取出应急事件发生的地点，然后根据当地的天气对初步方案给出改进建议，注意，请严格按照以下格式提供反馈:
                    1. 事件发生的地点：
                    - （具体地名）
                    2. 批评建议:
                    - （具体建议）""",
                extract_prompt="你是一个专业的信息提取助手，你的任务是由提供的文档中准确提取特定的内容，并按照规定的格式返回结果\n",
                extract_prefix=""
            )
            st.session_state['model_type'] = model_type
            st.session_state['api_base'] = api_base

        text = ""
        first_plan = ""
        for d in self.api.knowledge_base_chat(query,
                                         knowledge_base_name=selected_kb,
                                         top_k=kb_top_k,
                                         score_threshold=score_threshold,
                                         history=history,
                                         model=llm_model,
                                         prompt_name=prompt_template_name,
                                         temperature=temperature):
            if error_msg := check_error_msg(d):  # check whether error occured
                st.error(error_msg)
            elif chunk := d.get("answer"):
                text += chunk
                first_plan += chunk
                self.chat_box.update_msg(text, element_index=0)
        self.chat_box.update_msg("\n\n".join(d.get("docs", [])), element_index=1, streaming=False)

        async def run_async_blogger():
            message = AgentMessage(
                sender='user',
                content=f"对于问题：{topic}，我们给出了初步方案：{first_plan}。"
                # content=first_plan
            )
            result = await st.session_state['blogger'].forward(message, self.chat_box, first_plan)
            return result

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_async_blogger())

        

