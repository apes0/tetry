
# Tetry

![PyPi version](https://img.shields.io/pypi/v/tetry.svg) ![Code size](https://img.shields.io/github/languages/code-size/apes0/tetry)

A simple python library for interacting with the [Tetr.io](https://tetr.io/) API.

## contents

- [About](#About)
- [Instalation](#Instalation)
- [Documentation](#Documentation)
- [Examples](#Examples)
- [Contribution](#Contribution)
- [Helpful links](#Helpful-links)

## About

This library is a simple wrapper around the [Tetr.io](https://tetr.io/) API. It uses trio to provide a simple async interface.

## Instalation

### installing from pip

```sh
python3 -m pip install tetry
```

### installing from source

```sh
git clone https://github.com/apes0/tetry
cd tetry
python3 -m pip install -U .
```

## Documentation

Coming soon!

## Examples

Here you will find code examples for the library.

### General api

```python
from tetry import api

def printRecords(username):
    records = api.getRecords(username).records
    for name, record in records.items():
        print(f'{name}: {record}')

while (name := input()):
    printRecords(name)

```

### Chat commands

```python
from tetry import bot

bot = bot.Bot(token='token', commandPrefix='>')

@bot.chatCommand
async def ping(_msg):
    await bot.room.send(f'The bot\'s ping is {round(bot.ping*1000, 2)}ms')

bot.run()

```

### Simple auto-host bot

```python
import trio

from tetry.bot import Bot

bot = Bot(token='token')

@bot.event
async def ready():
    await bot.createRoom(False)

@bot.event
async def joinedRoom(room):
    print(room.invite)

@bot.event
async def userLeave(user):
    name = user['username']
    print(f'{name} has left')
    await bot.room.send(f'Goodbye {name}, hope to see you here again soon!')

async def start(room):
    delay = 20 # seconds
    needed = 2 # players
    if len(room.getPlaying()) >= needed:
        await room.send(f'Starting in {d} seconds!')
        await trio.sleep(delay)
        if len(room.getPlaying()) >= needed:
            await room.startGame()
        else:
            await room.send('Not enough players!')
    else:
        await room.send('Not enough players!')

@bot.event
async def userJoin(user):
    room = bot.room
    name = user['username']
    await room.send(f'Welcome to this room, {name}!')
    await start(room)

@bot.event
async def gameEnd():
    room = bot.room
    print('the game has ended')
    await start(room)

bot.run()

```

## Contribution

You can feel free to contribute to the this project by making a PR, making suggestions and opening issues for bugs/questions.

## Helpful links

- [tetrio bot docs](https://github.com/Poyo-SSB/tetrio-bot-docs/) - bot api documentation
- [tetr.js](https://github.com/tetrjs/tetr.js/) - a javascript library for the api
- [tetrio public api docs](https://tetr.io/about/api/) - the official api documentation
