
from astrbot.core.message.components import At
from astrbot.core.platform.astr_message_event import AstrMessageEvent
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent


def get_ats(
    event: AstrMessageEvent,
    noself: bool = False,
    block_ids: list[str] | None = None,
):
    """获取被at者们的id列表(@增强版)"""
    ats = {str(seg.qq) for seg in event.get_messages()[1:] if isinstance(seg, At)}
    ats.update(
        arg[1:]
        for arg in event.message_str.split()
        if arg.startswith("@") and arg[1:].isdigit()
    )
    if noself:
        ats.discard(event.get_self_id())
    if block_ids:
        ats.difference_update(block_ids)
    return list(ats)


async def get_nickname(event: AstrMessageEvent, user_id: int | str) -> str:
    """获取指定群友的群昵称或 Q 名，群接口失败/空结果自动降级到陌生人资料"""
    if not isinstance(event, AiocqhttpMessageEvent):
        return str(user_id)
    info = {}
    group_id = event.get_group_id()
    if group_id.isdigit():
        try:
            info = (
                await event.bot.get_group_member_info(
                    group_id=int(group_id), user_id=int(user_id)
                )
                or {}
            )
        except Exception:
            pass
    if not info:
        try:
            info = await event.bot.get_stranger_info(user_id=int(user_id)) or {}
        except Exception:
            pass

    # 依次取群名片、QQ 昵称、通用 nick，兜底数字 UID
    return info.get("card") or info.get("nickname") or info.get("nick") or str(user_id)
