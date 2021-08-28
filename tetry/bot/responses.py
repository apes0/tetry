import logging


from .friend import Friend
from .chatMessage import ChatMessage
from .commands import authorize as _authorize
from .dm import Dm
from .frame import Frame
from .game import Game
from .invite import Invite
from .room import Room
from .notification import Notification
from ..api.commitId import getCommit

logger = logging.getLogger(__name__)


async def hello(bot, msg, caller):
    bot.sockid = msg['id']
    bot.resume = msg['resume']
    messages = msg['packets']
    if not messages:
        # authorize message
        await bot.connection.send(_authorize(bot.messageId, bot.token, bot.handling, getCommit()))
    # get the ids for the seen messages
    seenIds = [m.message['id'] for m in bot.serverMessages]
    for m in messages:
        if m['id'] not in seenIds:
            await caller(bot.connection.ws, m)  # handle every unseen message


async def authorize(bot, msg, _caller):
    bot.worker = msg['data']['worker']
    bot.onlineUsers = msg['data']['social']['total_online']
    bot.presences = msg['data']['social']['presences']
    bot.friends = [Friend(f, bot)
                   for f in msg['data']['social']['relationships']]
    bot.notifications = [Notification(
        n, bot) for n in msg['data']['social']['notifications']]
    if not bot.loggedIn:
        await bot.setPresence('online')  # set the presence
        await bot._trigger('ready')
        bot.loggedIn = True


async def migrate(bot, msg, _caller):
    await bot.connection.close()  # close the connection to the websocket
    ws = msg['data']['endpoint']  # get the new endpoint
    await bot.recconect(ws)  # reconnect


async def migrated(bot, msg, _caller):
    bot.worker = msg['data']['worker']
    await bot._trigger('migrated', bot.worker)


async def err(_bot, msg, _caller):
    logger.error(msg['data'])  # log the error


async def gmupdate(bot, msg, _caller):
    comm = msg['command']
    coms = comm.split('.')  # command and its subcommands
    if len(coms) == 1:  # only gmupdate
        oldRoom = bot.room
        room = Room(msg['data'], bot)  # create a new room object
        bot.room = room
        if not oldRoom or oldRoom.left:  # trigger the joined room event if the room was of None type
            await bot._trigger('joinedRoom', room)
    else:
        subcomm = coms[1]
        if subcomm == 'host':  # changed host
            bot.room.owner = msg['data']
            owner = bot.room.getPlayer(bot.room.owner)
            await bot._trigger('changeOwner', owner)
        elif subcomm == 'bracket':  # bracket change
            ind = bot.room._getIndex(msg['data']['uid'])
            if msg['data']['uid'] == bot.id:
                bot.room.playing = (msg['data']['bracket'] == 'player')
            bot.room.players[ind]['bracket'] = msg['data']['bracket']
            await bot._trigger('changeBracket', bot.room.players[ind])
        elif subcomm == 'leave':  # player leaving
            player = bot.room.getPlayer(msg['data'])
            bot.room.players.remove(player)
            await bot._trigger('userLeave', player)
        elif subcomm == 'join':  # player joining
            bot.room.players.append(msg['data'])
            await bot._trigger('userJoin', msg['data'])


async def chat(bot, msg, _caller):  # chat messages
    await bot._trigger('message', ChatMessage(msg['data']))


# kick message, sent only when there is a fatal error, similar to nope
async def kick(_bot, msg, _caller):
    raise BaseException(msg['data']['reason'])


async def nope(_bot, msg, _caller):
    raise BaseException(f'server noped out: {msg["reason"]}')


async def endmulti(bot, _msg, _caller):  # end of game
    bot.room.inGame = False
    await bot._trigger('gameEnd')


async def ige(bot, msg, _caller):
    #    print(f'ige: {msg}')
    type = msg['data']['data']['type']
    if type == 'attack':
        bot.room.game._acceptGarbage(msg['data'])
    # TODO: add kev type


async def startmulti(bot, _msg, _caller):  # start of game
    bot.room.inGame = True
    await bot._trigger('gameStart')


async def replay(bot, msg, _caller):  # replay message
    for f in msg['data']['frames']:  # go through every frame
        fr = Frame(f)  # make a frame object
        if fr.type == 'start' and bot.room.playing:
            await bot._trigger('playing', bot.room)
            await bot.room.game.start()
        # nothing else currently, TODO: implement more frame types


async def readymulti(bot, msg, _caller):  # data for the game before it starts
    bot.room.game = Game(msg['data'], bot)


async def social(bot, msg, _caller):
    comm = msg['command']
    coms = comm.split('.')  # command and its subcommands
    subcomm = ''.join(coms[1:])
    if subcomm == 'invite':
        await bot._trigger('invited', Invite(msg['data'], bot))
    elif subcomm == 'online':
        bot.onlineUsers = msg['data']
    elif subcomm == 'dm':
        await bot._trigger('dm', Dm(msg['data']))
    elif subcomm == 'presence':
        bot.presences[msg['data']['user']] = msg['data']['presence']
    elif subcomm == 'notification':
        notif = Notification(msg['data'], bot)
        await bot._trigger('notification', notif)
        bot.notifications.append(notif)


async def leaveroom(bot, msg, _caller):
    if bot.room.id == msg['data']:
        bot.room.left = True
    await bot._trigger('leftRoom', msg['data'])
