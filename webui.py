import streamlit as st
from webui_pages.utils import *
from streamlit_option_menu import option_menu
from webui_pages.dialogue.dialogue import dialogue_page, chat_box
from webui_pages.knowledge_base.knowledge_base import knowledge_base_page
import os
import sys
from server.utils import api_address

VERSION = "0.1.0"

api = ApiRequest(base_url=api_address())

if __name__ == "__main__":
    is_lite = "lite" in sys.argv

    st.set_page_config(
        "应急管理问答系统 WebUI",
        os.path.join("img", "logo.svg"),
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/hohodong/Decision_Robot',
            'Report a bug': "https://github.com/hohodong/Decision_Robot/issues",
            'About': f"""欢迎使用 应急管理问答系统 WebUI {VERSION}！"""
        }
    )

    pages = {
        "应急管理问答": {
            "icon": "chat",
            "func": dialogue_page,
        },
        "知识库管理": {
            "icon": "hdd-stack",
            "func": knowledge_base_page,
        },
    }

    with st.sidebar:
        st.image(
            os.path.join(
                "img",
                "logo.svg"
            ),
            use_column_width=True
        )
        # st.caption(
        #     f"""<p align="middle">应急管理问答系统</p>""",
        #     unsafe_allow_html=True,
        # )
        st.caption(
            ":blue[应急管理问答系统]"
        )
        options = list(pages)
        icons = [x["icon"] for x in pages.values()]

        default_index = 0
        selected_page = option_menu(
            "",
            options=options,
            icons=icons,
            # menu_icon="chat-quote",
            default_index=default_index,
        )

    if selected_page in pages:
        pages[selected_page]["func"](api=api, is_lite=is_lite)
