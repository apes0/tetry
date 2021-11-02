import os
from tetry.bot import Bot

# export TETRIO_TOKEN=token
token = os.getenv('TETRIO_TOKEN')
bot = Bot(token)

user = None


@bot.event
async def ready():
    print('starting!')
    global user
    user = bot.owner['name']
    await test()


class Tests:
    async def unfriend(self):
        bot.removeFriend(name=user)
        friend = await bot.waitFor('friendRemoved')
        friend = friend[0]
        assert friend.name.upper() == user

    async def friend(self):
        bot.addFriend(name=user)
        friend = await bot.waitFor('friendAdded')
        friend = friend[0]
        assert friend.name.upper() == user

    async def dm(self):
        content = 'test'
        dm = await bot.dm(content, name=user)
        assert dm.content == content

    async def createRoom(self):
        room = await bot.createRoom(False)
        assert room is not None

    async def invite(self):
        await bot.invite(name=user)
        _user = await bot.waitFor('userJoin')
        _user = _user[0]
        assert _user['username'].upper() == user

    async def roomConfig(self):
        name = 'test'
        await bot.room.updateConfig({'meta.name': name})
        await bot.waitFor('roomUpdate')
        assert bot.room.name == name

    async def chat(self):
        content = 'test'
        await bot.room.send(content)
        msg = await bot.waitFor('message')
        msg = msg[0]
        assert msg.content == content

    async def ban(self):
        await bot.room.banUser(bot.owner['id'])
        await bot.waitFor('userLeave')

    async def unban(self):
        await bot.room.unbanUser(user)


async def test():
    tests = Tests()
    for name in tests.__dir__():
        current = tests.__getattribute__(name)
        if name.startswith('_'):
            continue
        try:
            await current()
            print('*', end=' ')
        except AssertionError:
            print('-', end=' ')
        except Exception as e:
            print(f'\n! {e}')
    print('\ndone!')

bot.run()
