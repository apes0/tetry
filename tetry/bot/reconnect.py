from .commands import resume
from .commands import hello as _hello
from .ribbons import Connection


async def reconnect(ws, sockid, resumeToken, nurs, bot):
    conn = Connection(bot, ws)
    await conn.connect(nurs)
    bot.connection = conn
    await conn.conn.trigger(nurs, bot)
    await conn.send(resume(sockid, resumeToken))  # resume message
    # hello message
    await conn.send(_hello([message.message for message in bot.messages]))
