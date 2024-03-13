import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src":
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

import time
import logging
import prompts.engine as engine_prompts
from openai import OpenAI
from llm.chat.messages import PrintStreamHandler, StreamlitStreamHandler
from llm.chat.conversations import Conversation, StreamlitConversation
from llm.chat.chat import general_completion_request
from llm import my_tools
from utils.errors import (
    DatabaseError,
    NetworkError,
    ArgumentParseError,
    handle_error,
)
from utils.logging_setup import setup_logging


class CerebraUser:
    def __init__(self, userid=None, persistent_log=False, modality="cmd"):
        self.userid = userid
        self.add_userid_if_missing()
        # set up logging
        setup_logging(
            __file__, self.userid, persistent_log=persistent_log, modality=modality
        )
        logging.info("-----STARTING NEW SESSION-----")
        # set up tmp dir
        self.setup_tmp_dir()

    def add_userid_if_missing(self):
        def generate_userid():
            import uuid

            return str(uuid.uuid4())[:8]

        if not self.userid:
            self.userid = generate_userid()

    def setup_tmp_dir(self):
        save_dir = Path(src_dir) / "tmp" / self.userid / "plots"
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)


class Session:
    def __init__(self, userid, persistent_log=False, debug=False, modality="cmd"):
        self.userid = userid
        self.modality = modality
        self.debug = debug
        if self.debug:
            self.default_respond_wait_time = 0.0
            self.persistent_log = True
        else:
            self.persistent_log = persistent_log
            self.default_respond_wait_time = 0.05

        self.user = CerebraUser(
            self.userid, persistent_log=self.persistent_log, modality=self.modality
        )
        self.conversation = self.start_conversation()
        self.conversation.add_text_message("system", engine_prompts.system)
        self.backoff = True
        self.client = OpenAI()
        self.model = "gpt-4-1106-preview"
        self.stream_handler_class = PrintStreamHandler
        self.tool_module = my_tools

        # pio.renderers.default = 'browser'

    def start_conversation(self):
        return Conversation()

    def completion_request(self, prompt):
        """
        This is where the main error handling is performed.
        This is also where I add in tools and some specificications for the run.
        """

        self.conversation.add_text_message("user", prompt)

        for msg in self.conversation.messages:
            logging.info(f"START {msg['role']}: {msg}")
        try:
            general_completion_request(
                self,
                prompt,
            )

        except Exception as e:
            err_msg_for_user = handle_error(e)
            self.respond_to_error(err_msg_for_user)

            if self.debug:  # debug raises error
                raise e

    # both for error responding
    def respond(self, text):
        stream_handler = self.stream_handler_class()
        for r in text:
            time.sleep(self.default_respond_wait_time)
            stream_handler.add_text(r)
        stream_handler.finish()
        self.conversation.add_obj_message(stream_handler)

    def respond_to_error(self, error_message):
        self.conversation.add_text_message("assistant", error_message)
        self.respond(error_message)


class StreamlitSession(Session):
    def __init__(self, userid, debug=False):
        super().__init__(userid, debug=debug, modality="streamlit")
        self.stream_handler_class = StreamlitStreamHandler

    def start_conversation(self):
        return StreamlitConversation()
