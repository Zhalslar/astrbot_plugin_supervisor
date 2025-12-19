import os
import random
import time

from astrbot.api import logger
from astrbot.api.event import filter
from astrbot.api.star import Context, Star
from astrbot.core import AstrBotConfig
from astrbot.core.message.components import At, Image, Plain
from astrbot.core.platform import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
    AiocqhttpMessageEvent,
)
from astrbot.core.star.filter.event_message_type import EventMessageType

from .utils import get_ats


class SupervisorPlugin(Star):
    """
    监督插件（生产级）

    设计要点：
    - 无定时器
    - 监督状态 = qq -> 过期时间戳
    - 消息入口裁决 + 顺手回收过期数据
    """

    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        self.image_dir = os.path.join(
            "data", "plugins", "astrbot_plugin_supervisor", "image"
        )

        # qq -> expire_ts
        self.supervisors: dict[str, int] = {}

        # 兜底配置
        self.default_minute: int = int(self.config.get("default_minute", 10))

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _now(self) -> int:
        return int(time.time())

    def _cleanup_expired(self) -> None:
        """清理过期监督（轻量、无副作用）"""
        now = self._now()
        expired = [qq for qq, ts in self.supervisors.items() if ts <= now]

        if not expired:
            return

        for qq in expired:
            self.supervisors.pop(qq, None)

        self.config["supervisors"] = self.supervisors
        self.config.save_config()
        logger.debug(f"已清理过期监督: {expired}")

    def _is_supervising(self, qq: str) -> bool:
        """是否在监督期内"""
        expire = self.supervisors.get(qq)
        return bool(expire and expire > self._now())

    @staticmethod
    def _get_random_image(image_dir: str) -> str | None:
        try:
            entries = os.listdir(image_dir)
        except FileNotFoundError:
            logger.warning("监督图片目录不存在")
            return None

        if not entries:
            logger.warning("监督图片目录为空")
            return None

        return os.path.join(image_dir, random.choice(entries))

    async def _ai_supervisor(self, text: str) -> str | None:
        try:
            llm_response = await self.context.get_using_provider().text_chat(
                prompt=f"他来水群了：{text}",
                contexts=[
                    {
                        "role": "system",
                        "content": self.config.get(
                            "supervisor_prompt", "你是一个严格但幽默的群监工"
                        ),
                    }
                ],
            )
            return " " + llm_response.completion_text
        except Exception as e:
            logger.error(f"LLM 监工失败: {e}")
            return None

    async def _poke_supervisor(self, event: AiocqhttpMessageEvent) -> None:
        try:
            await event.bot.send_poke(
                user_id=int(event.get_sender_id()),
                group_id=int(event.get_group_id()),
            )
        except Exception as e:
            logger.error(f"戳一戳监工失败: {e}")

    # ------------------------------------------------------------------
    # 消息入口
    # ------------------------------------------------------------------

    @filter.event_message_type(EventMessageType.GROUP_MESSAGE)
    async def on_supervisor(self, event: AstrMessageEvent):
        """消息入口"""
        sender_id = event.get_sender_id()

        # 顺手清理（成本极低）
        self._cleanup_expired()

        if not self._is_supervising(sender_id):
            return

        rand = random.random()
        chain = []

        if rand < 0.4:
            if image := self._get_random_image(self.image_dir):
                chain = [At(qq=sender_id), Image(image)]

        elif rand < 0.8:
            if text := await self._ai_supervisor(event.get_message_str()):
                chain = [Plain(text)]

        elif isinstance(event, AiocqhttpMessageEvent):
            await self._poke_supervisor(event)

        if chain:
            yield event.chain_result(chain)  # type: ignore

    # ------------------------------------------------------------------
    # 指令：监督
    # ------------------------------------------------------------------

    @filter.command("监督")
    async def add_supervisor(self, event: AstrMessageEvent):
        parts = event.message_str.split()
        minute = (
            int(parts[-1]) if parts and parts[-1].isdigit() else self.default_minute
        )

        at_ids = get_ats(event, noself=True)
        if not at_ids:
            yield event.plain_result("请 @ 要监督的对象")
            return

        expire = self._now() + minute * 60
        for qq in at_ids:
            self.supervisors[qq] = expire

        self.config["supervisors"] = self.supervisors
        self.config.save_config()

        yield event.plain_result(f"已监督 {at_ids}，时长 {minute} 分钟")

    # ------------------------------------------------------------------
    # 指令：解除监督
    # ------------------------------------------------------------------

    @filter.command("解除监督")
    async def remove_supervisor(self, event: AstrMessageEvent):
        at_ids = get_ats(event, noself=True)
        if not at_ids:
            yield event.plain_result("请 @ 要解除监督的对象")
            return

        for qq in at_ids:
            self.supervisors.pop(qq, None)

        self.config["supervisors"] = self.supervisors
        self.config.save_config()

        yield event.plain_result(f"已解除监督: {at_ids}")

    # ------------------------------------------------------------------
    # 指令：查看监督
    # ------------------------------------------------------------------

    @filter.command("监督列表")
    async def list_supervisors(self, event: AstrMessageEvent):
        self._cleanup_expired()

        if not self.supervisors:
            yield event.plain_result("当前没有正在监督的对象")
            return

        now = self._now()
        lines = []
        for qq, ts in self.supervisors.items():
            remain = max(0, (ts - now) // 60)
            lines.append(f"{qq}（剩余 {remain} 分钟）")

        yield event.plain_result("监督中：\n" + "\n".join(lines))
