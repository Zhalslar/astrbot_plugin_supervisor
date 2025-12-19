
from astrbot.core.message.components import At
from astrbot.core.platform.astr_message_event import AstrMessageEvent


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