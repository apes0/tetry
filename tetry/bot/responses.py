import logging

from trio_websocket import connect_websocket_url

from .chatMessage import ChatMessage
from .commands import authorize as _authorize
from .commands import hello as _hello
from .commands import resume
from .frame import Frame
from .game import Game
from .invite import Invite
from .ribbons import conn, send
from .room import Room

logger = logging.getLogger(__name__)


async def _reconnect(ws, sockid, resumeToken, nurs, bot):
    ws = await connect_websocket_url(nurs, ws)
    ws.nurs = nurs
    ws.bot = bot
    bot.ws = ws
    await conn.trigger(nurs, bot)
    await send(resume(sockid, resumeToken), ws)  # resume message
    # hello message
    await send(_hello([message.message for message in bot.messages]), ws)


async def hello(bot, msg, caller):
    bot.sockid = msg['id']
    bot.resume = msg['resume']
    messages = msg['packets']
    # get the raw json for the seen messages
    seen = [m.message for m in bot.serverMessages]
    for m in messages:
        if m not in seen:
            await caller(bot.ws, m)  # handle every unseen message
    # authorize message
    await send(_authorize(bot.messageId, bot.token, bot.handling), bot.ws)


async def authorize(bot, _msg):
    await bot.setPresence('online')  # set the presence
    await bot._trigger('ready')


async def migrate(bot, msg):
    await bot.ws.aclose()  # close the connection to the websocket
    ws = msg['data']['endpoint']  # get the new endpoint
    await _reconnect(ws, bot.sockid, bot.resume, bot.nurs, bot)  # reconnect


async def err(_bot, msg):
    logger.error(msg['data'])  # log the error


async def gmupdate(bot, msg):
    comm = msg['command']
    coms = comm.split('.')  # command and its subcommands
    if len(coms) == 1:  # only gmupdate
        oldRoom = bot.room
        room = Room(msg['data'], bot)  # create a new room object
        bot.room = room
        if not oldRoom:  # trigger the joined room event if the room was of None type
            await bot._trigger('joinedRoom', room)
    else:
        subcomm = coms[1]
        if subcomm == 'host':  # changed host
            bot.room.owner = msg['data']
            owner = bot.room.getPlayer(bot.room.owner)
            await bot._trigger('changeOwner', owner)
        elif subcomm == 'bracket':  # bracket change
            ind = bot.room._getIndex(msg['data']['uid'])
            bot.room.players[ind]['bracket'] = msg['data']['bracket']
            await bot._trigger('changeBracket', bot.room.players[ind])
        elif subcomm == 'leave':  # player leaving
            player = bot.room.getPlayer(msg['data'])
            bot.room.players.remove(player)
            await bot._trigger('userLeave', player)
        elif subcomm == 'join':  # player joining
            bot.room.players.append(msg['data'])
            await bot._trigger('userJoin', msg['data'])


async def chat(bot, msg):  # chat messages
    await bot._trigger('message', ChatMessage(msg['data']))


async def kick(_bot, msg):  # kick message, sent only when there is a fatal error, similar to nope
    raise BaseException(msg['data']['reason'])


async def nope(_bot, msg):
    raise BaseException(msg['data']['reason'])


async def endmulti(bot, _msg):  # end of game
    bot.room.inGame = False
    await bot._trigger('gameEnd')


async def startmulti(bot, _msg):  # start of game
    bot.room.inGame = True
    await bot._trigger('gameStart')


async def replay(bot, msg):  # replay message
    for f in msg['data']['frames']:  # go through every frame
        fr = Frame(f)  # make a frame object
        if fr.type == 'start':
            await bot._trigger('playing', bot.room)
            await bot.room.game.start()
        # nothing else currently, TODO: implement this


async def readymulti(bot, msg):  # data for the game before it starts
    bot.room.game = Game(msg['data'], bot)


async def social(bot, msg):
    comm = msg['command']
    coms = comm.split('.')  # command and its subcommands
    subcomm = coms[1]
    if subcomm == 'invite':
        print('a')
        await bot._trigger('invited', Invite(msg['data'], bot))


async def leaveroom(bot, msg):
    bot.room = None
    await bot._trigger('leftRoom', msg['data'])
