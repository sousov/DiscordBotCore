import discord
import json
import os
import asyncio
from discord.ext import commands, tasks
from config import settings
from itertools import cycle

client = commands.Bot(command_prefix = settings['prefix'])
titlebot = settings['bot']
ider = settings['id']
prefixes = settings['prefix']
status = cycle([f'Мой префикс: \"{prefixes}\"', f'Чтобы узнать мои команды, напиши: \"{prefixes}commands\"', 'Создатель бота: im.not.sousov#9960'])

Expression = settings['mat']

@client.event
async def on_ready():
    change_status.start()
    print('Запускается конфиг:')
    print(f'Бот: \"{titlebot}\"')
    print(f'ID: \"{ider}\"')
    print(f'Префикс: \"{prefixes}\"')
    print('Проверка успешно завершена!\nСтатус: Online')

# status
@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(status)))

# expression
@client.event
async def on_message(ctx):
    await client.process_commands(ctx)
    for a in Expression:
        if a in ctx.content:
            await ctx.delete()
            author = ctx.author
            await ctx.channel.send(f'{author.mention}, не используйте матерную лексику, иначе получите мут!')

# Level Config
@client.event
async def on_message(message):
    with open('users.json', 'r') as f:
        users = json.load(f)
    async def update_data(users,user):
        if not user in users:
            users[user] = {}
            users[user]['exp'] = 0
            users[user]['lvl'] = 1
    async def add_exp(users,user,exp):
        users[user]['exp'] += exp
    async def add_lvl(users,user):
        exp = users[user]['exp']
        lvl = users[user]['lvl']
        if exp > lvl:
            users[user]['exp'] = 0
            users[user]['lvl'] = lvl + 1
            level = lvl + 1
            await message.channel.send(f'{message.author.mention} получил уровень {level}!')
            exp = 0
    await update_data(users,str(message.author.id))
    await add_exp(users,str(message.author.id),0.1)
    await add_lvl(users,str(message.author.id))
    with open('users.json', 'w') as f:
        json.dump(users,f)

# joined
@client.event
async def on_member_join(member):
    print(f'{member} присоединился на сервер!')

# leaved
@client.event
async def on_member_remove(member):
    print(f'{member} покинул сервер :(')

# commands
@client.command(aliases=['команды', 'commands'])   
async def _commands_(ctx):
     await ctx.send(f'Основные команды:\n```css\n{prefixes}ping - Показывает задержку бота.\n{prefixes}prefix - Узнать префикс на сервере.\n{prefixes}arguments - Показывает количество аргументов и слов в вашем тексте.\n{prefixes}replay - Повторяет ваше сообщение.```')

# arguments
@client.command(aliases=['аргументы', 'arguments'])
async def _arguments_(ctx, *args):
    await ctx.send('Количество аргументов в тексте: {}\nCлова из вашего текста через запятую: \"{}\"'.format(len(args), ', '.join(args)))

# replay
@client.command(aliases=['replay', 'повтор'])
async def _replay_(ctx, *, arg):
    await ctx.channel.purge(limit=1)
    await ctx.send(arg)

# ping
@client.command(aliases=['ping', 'пинг'])   
async def _ping_(ctx):
    await ctx.send(f'Пинг: {round(client.latency * 1000)}ms')

# prefix
@client.command(aliases=['префикс', 'prefix'])   
async def _prefix_(ctx):
    await ctx.send(f'Префикс: `\"{prefixes}\"`')

# clear
@client.command(past_context=True, aliases=['clear', 'удалить']) 
@commands.has_permissions(manage_messages=True)
async def _clear_(ctx, arg):
    await ctx.channel.purge(limit=int(arg))
    author = ctx.author
    await ctx.send(f'{author.mention}, удалено \"{arg}\" сообщений!')

# mute
@client.command(aliases=['мут', 'mute'])
@commands.has_permissions(view_audit_log=True)
async def _mute_(ctx, member:discord.Member, time:int, reason):
    channel = client.get_channel(732925483829690448)
    muterole = discord.utils.get(ctx.guild.roles, id=735139347312934963)
    emb = discord.Embed(title='Информация о выданном нарушении', color=0xff0000)
    emb.add_field(name='Модератор', value=ctx.message.author.mention, inline=True)
    emb.add_field(name='Нарушитель', value=member.mention, inline=True)
    emb.add_field(name='Время наказания', value=f'{time} мин', inline=False)
    emb.add_field(name='Причина:', value=reason, inline=True)
    await member.add_roles(muterole)
    await channel.send(embed = emb)
    muted = member
    await muted.send(f'{member.mention}, вам выдан мут!')
    await muted.send(embed = emb)
    await asyncio.sleep(time * 60)
    await member.remove_roles(muterole)
    await channel.send(f'Мут с Участника \"{member.mention}\" был успешно снят!')
    await muted.send(f'{member.mention}, ваш мут успешно снят!')

# unmute
@client.command(aliases=['размут', 'unmute'])
@commands.has_permissions(view_audit_log=True)
async def _unmute_(ctx, member:discord.Member):
    channel = client.get_channel(732925483829690448)
    muterole = discord.utils.get(ctx.guild.roles, id=735139347312934963)
    emb = discord.Embed(title='Снял наказание', color=0xff0000)
    emb.add_field(name='Модератор', value=ctx.message.author.mention, inline=False)
    await member.remove_roles(muterole)
    await channel.send(f'Наказание \"Мут\" с Участника \"{member.mention}\" было снято!')
    await channel.send(embed = emb)
    unmuted = member
    await unmuted.send(f'{member.mention}, с вас сняли наказание \"Мут\"!\nПодробнее:')
    await unmuted.send(embed = emb)

# Запуск
client.run(settings['token'])



# @client.command(aliases=['кик', 'kick']) 
# async def _kick(ctx, member:discord.Member, *, reason=None):
#   await member.kick(reason=reason)

# @client.command(past_context=True, aliases=['ban', 'бан']) 
# async def _ban(ctx, member:discord.Member, *, reason=None):