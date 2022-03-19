import discord
import asyncio
from discord.errors import ClientException
import credits
import json
import youtube_dl as yt
import subprocess
from discord.ext import commands, tasks
from discord.utils import get

print(discord.__version__)

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

yt.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = yt.YoutubeDL(ytdl_format_options)
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

client = discord.Client()
bot = commands.Bot(command_prefix='!')
token = "".join(credits.bot_token)
song = ''
s_id = 0
rep = 0
break_playing = False
explateves = ['еб', 'хуй', 'хуи', 'пидор', 'сук', 'хер', 'бля', 'пизд', 'пидр', 'ахуе', 'лох', 'деби', 'дроч', 'пидар']


@bot.event
async def on_message(message):
    global explateves

    await bot.process_commands(message)

    with open('mus_data.json', 'r') as f:
        data = json.load(f)
    
    phrase = message.content
    words = explateves
    fragments = []
    ex = False

    for word in words:
        for part in range(len(phrase)):
            fragment = phrase[part: part+len(word)]
            fragments.append(fragment)

    for word in words:
        for fragment in fragments:
            if word == fragment:
                ex = True
                data['accs'][message.author.name]['expl'] += 1
    if ex:
        with open('mati.jpg', 'rb') as f:
            pic = f
        await message.channel.send(pic)

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='start')
async def start(ctx):
    await ctx.send(':male_sign:Welcome to the club, buddy!:male_sign:\nНапиши !help_me для ознакомления с командами бота')


@bot.command(name='help_me')
async def help_me(ctx):
    await ctx.send('''Рады приветствовать! Ознакомься с инструктажем:

Регистрация:

!add_me - добавить свой аккаунт, создается автоматически, без него прослушивание окажется невозможным.
!del_me - удалить свой аккаунт.

Как только ты создал аккаунт, можно приступать к руководству:

1. Как добавить свою песню?
Для этого тебе понадобится Youtube ссылка на видео с музыкой.
Чтобы добавить песню, воспользуйся командой !add_song [ссылка] [название(любое)]
После этого музыка автоматически добавится в твой плейлист.
Пример : !add_song https://youtu.be/dQw4w9WgXcQ 3:32 NGGYU

2. Как удалить песню из плейлиста?
Чтобы стереть музыку, есть команда !remove_song [название(которое ты вводил при добавлении песни)]

3. Как очистить свой плейлист?
Для этого пользуйся командой remove_all, которая очистит твой плейлист полностью.

4. Как посмотреть песни в плейлисте?
Команда !music_list тебе поможет!

5.Наконец, как слушать музыку?
чтобы начать слушать музыку, во-первых необходимо будет наполнить свой плейлист различными песнями.
После этого нужно зайти в любой голосовой чат и выполнить команду !join, которая пригласит бота к тебе.
Чтобы выгнать бота, напиши !leave.
Все готово! Осталось ввести команду !play [количество повторений плейлиста] и наслаждаться!
Помимо этого есть команда !stop, которая полностью останавливает прослушивание
И команда !next, проматывающая плейлист до следущей песни.

Надеюсь, все было понятно, по багами и другим проблемам сообщать в чат #баги, наш недопрограммист постарается их исправить
Приятного прослушивания!''')


@bot.command(name='saltuha')
async def saltuha(ctx):
    with open('saltuha.gif', 'rb') as f:
        picture = discord.File(f)
    await ctx.send(file=picture)


@bot.command(name='add_me')
async def add_me(ctx):
    with open('mus_data.json') as f:
        data = json.load(f)

    if ctx.message.author.name in data['accs']:
        await ctx.send('Вы уже есть в каталоге пользователей.')
    else:
        data['accs'][ctx.message.author.name] = {'id' : ctx.message.author.id, 'music' : {}, 'expl' : 0} 
        await ctx.send('Вы были успешно добавлены в каталог пользователей!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='del_me')
async def add_me(ctx):
    with open('mus_data.json') as f:
        data = json.load(f)

    if not ctx.message.author.name in data['accs']:
        await ctx.send('Вас еще нет в каталоге пользователей.')
    else:
        del data['accs'][ctx.message.author.name]
        await ctx.send('Вы были успешно удалены из каталога пользователей!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='join')
async def join(ctx):
    try:
        chnl = ctx.message.author.voice.channel
        await chnl.connect()
    except:
        AttributeError
        await ctx.send('Бот уже есть в голосовом чате!')


@bot.command(name='leave')
async def leave(ctx):
    try:
        voice_client = ctx.guild.voice_client
        await voice_client.disconnect()
    except:
        AttributeError
        await ctx.send('Бота еще нет в голосовом чате!')


@bot.command(name='add_song')
async def add_song(ctx, url, name):
    with open('mus_data.json') as f:
        data = json.load(f)

    if ctx.message.author.name in data['accs']:
        data['accs'][ctx.message.author.name]['music'].append([name, url])
        await ctx.send('Песня была успешно добавлена!')
    else:
        await ctx.send('Сначала создайте аккаунт!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='remove_song')
async def remove_song(ctx, name):
    with open('mus_data.json') as f:
        data = json.load(f)

    if ctx.message.author.name in data['accs']:
        cor = False
        for m in data['accs'][ctx.message.author.name]['music']:
            if name in m:
                del data['accs'][ctx.message.author.name]['music'][m]
                cor = True
        if cor:
            await ctx.send('Песня была успешно удалена!')
        else:
            await ctx.send('Что-то пошло не так!')
    else:
        await ctx.send('Сначала создайте аккаунт!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='remove_all')
async def remove_all(ctx):
    with open('mus_data.json') as f:
        data = json.load(f)

    if ctx.message.author.name in data['accs']:
        data['accs'][ctx.message.author.name]['music'] = []
        await ctx.send('Песни были успешно удалены!')
    else:
        await ctx.send('Сначала создайте аккаунт!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='music_list')
async def music_list(ctx):
    with open('mus_data.json') as f:
        data = json.load(f)

    if ctx.message.author.name in data['accs']:
        text = 'Список песен:\n'
        name = ctx.message.author.name
        ind = 1
        try:
            for i in data['accs'][name]['music']:
                text += (str(ind) + '. ' + i[0] + '\n')
                ind += 1
        except:
            KeyError
    else:
        await ctx.send('Сначала создайте учетную запись!')
    
    await ctx.send(text)


@bot.command(name='play')
async def play(ctx, r):
    global rep, s_id, voice, break_playing
    voice = get(bot.voice_clients, guild=ctx.guild)

    await ctx.send('Повысь lil mishannyya пж')

    with open('mus_data.json') as f:
        data = json.load(f)
    print(ctx.message.author.name)
    if ctx.message.author.name in data['accs']:
        rep = int(r)
        name = ctx.message.author.name

        text = ''
        ind = 0
        for i in data['accs'][name]['music']:
            if s_id == ind:
                text += (str(ind + 1) + '. ' + '🎵' + i[0] + '🎵' + '\n')
            else:
                text += (str(ind + 1) + '. ' + i[0] + '\n')
            ind += 1
        message = await ctx.send(text)

        for i in range(int(rep)):
            for j in range(len(data['accs'][name]['music'])):
                print(s_id)
                song = data['accs'][name]['music'][s_id][1]
                filename = await YTDLSource.from_url(song, loop=bot.loop)
                voice.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
                while voice.is_playing():
                    await asyncio.sleep(1)
                if break_playing:
                    break
                s_id += 1

                text = ''
                ind = 0
                for i in data['accs'][name]['music']:
                    if s_id == ind:
                        text += (str(ind + 1) + '. ' + '🎵' + i[0] + '🎵' + '\n')
                    else:
                        text += (str(ind + 1) + '. ' + i[0] + '\n')
                    ind += 1
                await message.edit(content=text)

            if break_playing:
                break
            s_id = 0
        break_playing = False
        rep = 0
        s_id = 0
    else:
        await ctx.send('Сначала создайте аккаунт или добавьте песни!')

    with open('mus_data.json', 'w') as f:
        json.dump(data, f, indent=4)


@bot.command(name='stop')
async def stop(ctx):
    global rep, s_id, break_playing
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.stop()
        break_playing = True
        rep = 0
        s_id = 0
    else:
        await ctx.send('Для начала запустите бота, пригласив его в чат и запустив')


@bot.command(name='next')
async def next(ctx):
    voice.stop()


bot.run(token)
