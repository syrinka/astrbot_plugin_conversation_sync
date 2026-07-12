from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star
from astrbot.api import AstrBotConfig


class MyPlugin(Star):
    context: Context
    cids: list[str]
    last_active: str | None

    def __init__(self, context: Context, config: AstrBotConfig):
        self.context = context
        self.cids = config['cid_list']

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        self.last_active = await self.get_kv_data("last_active", None)

    @filter.after_message_sent()
    async def on_sent(self, event: AstrMessageEvent, *args, **kwargs):
        conv_mgr = self.context.conversation_manager
        uid = event.unified_msg_origin
        cid = await conv_mgr.get_curr_conversation_id(uid)
        if cid in self.cids:
            self.last_active = cid

    @filter.event_message_type(filter.EventMessageType.PRIVATE_MESSAGE)
    async def sync(self, event: AstrMessageEvent, *args, **kwargs):
        conv_mgr = self.context.conversation_manager
        uid = event.unified_msg_origin
        cid = await conv_mgr.get_curr_conversation_id(uid)
        if cid is None:
            return
        if cid in self.cids and self.last_active and cid != self.last_active:
            sync = await conv_mgr.db.get_conversation_by_id(self.last_active)
            await conv_mgr.db.update_conversation(cid = cid, content=sync.content)
            self.last_active = cid


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        await self.put_kv_data("last_active", self.last_active)
