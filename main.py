from database import *
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
import nextcord
import botconfig
import json
import random
from waifu import WaifuClient
import os
import requests

client = commands.Bot(command_prefix="!")
client.remove_command("help")
waifu = WaifuClient()

@client.event
async def on_ready():
	print("On ready!")
	await client.change_presence( status = nextcord.Status.online, activity = nextcord.Game( '!help' ) )

@client.event
async def on_member_join(member):
	member.send("Добро пожаловать!")
	with open(f"money/{member.name}.txt", 'a') as file:
		file.write(f"{member.name}\n")
		file.write("1000")
	print("Added to economy!")
	with open(f"abilities/{member.name}.txt", 'a') as file:
		file.write(f"{member.name}\n")
		file.write("5")
	print("Ability added!")

@client.command(aliases=["добавить"])
@commands.has_permissions( administrator = True )
async def add_boss(ctx, name: str, hp: int):
	data = Boss.add_boss(name=name, health=hp)
	msg = await ctx.send("One second...")
	await msg.add_reaction("✅")


@client.command(aliases=["босс"])
async def boss(ctx, name: str):
	boss = Boss.get(name=name)

	emb = nextcord.Embed( title = 'Информация о боссе', colour = nextcord.Color.green() )
	emb.add_field( name = 'Имя:', value = f"**{boss.name}**" )
	emb.add_field( name = 'HP:', value = f"**{boss.health}**" )
	await ctx.send( embed = emb )

@client.command(aliases=["сражение"])
async def fight(ctx, name: str):
	boss = Boss.get_boss(name=name)
	boss.execute()
	fight = False
	if fight == False:
		emb = nextcord.Embed( title = 'Сражение', colour = nextcord.Color.green() )
		emb.add_field( name = 'Босс:', value = f"**{boss.name}**" )
		emb.add_field( name = 'HP:', value = f"**{boss.health}**" )
		emb.add_field( name = 'Управление:', value = "**Чтобы ударить используйте команду !hit**" )		
		await ctx.send( embed = emb )
		fight = True
	elif fight == True:
		ctx.send("Упс! Сражение уже идёт!")

@client.command(aliases=["удар"])
async def hit(ctx, name: str):
	with open(f"abilities/{ctx.message.author.id}.txt", 'r') as file:
		adata = file.readlines()
	strength = random.randint(1, int(adata[1]))
	boss = Boss.get_boss(name=name)
	hp = int(boss.health) - strength
	boss.update_boss(name=name, type="health", value=hp)
	if hp <= 0:
		emb = nextcord.Embed( title = 'Победа', colour = nextcord.Color.green() )
		emb.add_field( name = 'Босс:', value = f"**{data[0]}**" )
		await ctx.send( embed = emb )
		os.remove(f"bosses/{name}.txt", dir_fd=None)
	else:	
		emb = nextcord.Embed( title = 'Удар', colour = nextcord.Color.green() )
		emb.add_field( name = 'Имя босса:', value = f"**{boss.name}**" )
		emb.add_field( name = 'Нанесено:', value = f"**{strength}** урона" )
		emb.add_field( name = 'Осталось ХП:', value = f"**{hp}/{boss.health}**" )
		emb.set_thumbnail( url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Crossed_swords.svg/1200px-Crossed_swords.svg.png" )
		await ctx.send( embed = emb )

@client.command(aliases=["прокачка"])
async def upgrade(ctx, ability: str):
	with open(f"money/{ctx.message.author.id}.txt", 'r') as file:
		data = file.readlines()
		money = data[1]
	with open(f"money/{ctx.message.author.id}.txt", 'w') as file:
		file.write(str(ctx.message.author))
		file.write(money)
	if ability == "сила":
		if int(money) < 5:
			ctx.send("Недостаточно средств!")
		else:
			money = int(money) - 5			
			with open(f"abilities/{ctx.message.author.id}.txt", 'r') as file:
				adata = file.readlines()
				strength = int(adata[1]) + 2
			with open(f"money/{ctx.message.author.id}.txt", 'w') as file:
				file.write(f"{ctx.message.author}\n")
				file.write(str(money))
			with open(f"abilities/{ctx.message.author.id}.txt", 'w') as file:
				file.write(f"{ctx.message.author}\n")
				file.write(str(strength))

			emb = nextcord.Embed( title = 'Прокачка персонажа', colour = nextcord.Color.green() )
			emb.add_field( name = 'Пользователь:', value = f"**{ctx.author.mention}**" )
			emb.add_field( name = 'Навык:', value = f"**{ability}**" )
			emb.add_field( name = 'Осталось денег:', value = f"**{money}**" )
			emb.add_field( name = 'Сила навыка до прокачки:', value = f"**{adata[1]}**" )
			emb.add_field( name = 'Сила навыка после прокачки:', value = f"**{int(adata[1]) + 2}**" )

			await ctx.send( embed = emb )

@client.command(aliases=["баланс"])
async def balance(ctx):
	with open(f"money/{ctx.message.author.id}.txt", 'r') as file:
		data = file.readlines()
		money = data[1]
	emb = nextcord.Embed( title = 'Баланс', colour = nextcord.Color.blue() )
	emb.add_field( name = 'Пользователь:', value = f"**{ctx.author.mention}**" )
	emb.add_field( name = 'Баланс счёта:', value = f"**{money}**" )

	await ctx.send( embed = emb )

@client.command(aliases=["перевести"])
async def pay(ctx, member: nextcord.Member, amount: int):
	with open(f"money/{ctx.message.author.id}.txt", 'r') as file:
		data = file.readlines()
		money = data[1]
	if int(money) < amount:
		emb = nextcord.Embed( title = 'Перевод средств', colour = nextcord.Color.red() )
		emb.add_field( name = 'Отправитель:', value = f"**{ctx.author.mention}**" )
		emb.add_field( name = 'Получатель:', value = f"**{member.mention}**" )
		emb.add_field( name = 'Сумма:', value = f"**{amount}**" )
		emb.add_field( name = 'Ошибка:', value = f"**Недостаточно средств**" )
		emb.add_field( name = 'Ваш баланс:', value = f"**{money}**" )
		await ctx.send( embed = emb )
	else:
		remaining_money = int(money) - amount
		with open(f"money/{ctx.message.author.id}.txt", 'w') as file:
			file.write(f"{str(ctx.message.author)}\n")
			file.write(str(remaining_money))
		with open(f"money/{member.id}.txt", 'r') as file:
			data = file.readlines()
			money = data[1]
			new_money = int(money) + amount
		with open(f"money/{member.id}.txt", 'w') as file:
			file.write(f"{str(member.name)}\n")
			file.write(str(new_money))
		emb = nextcord.Embed( title = 'Перевод средств', colour = nextcord.Color.blue() )
		emb.add_field( name = 'Отправитель:', value = f"**{ctx.author.mention}**" )
		emb.add_field( name = 'Получатель:', value = f"**{member.mention}**" )
		emb.add_field( name = 'Сумма:', value = f"**{amount}**" )

		await ctx.send( embed = emb )

@client.command(aliases=["счёт"])
@commands.has_permissions( administrator = True )
async def user_balance(ctx, member: nextcord.Member):
	with open(f"money/{member.id}.txt", 'r') as file:
		data = file.readlines()
		money = data[1]
	emb = nextcord.Embed( title = 'Баланс пользователя', colour = nextcord.Color.blue() )
	emb.add_field( name = 'Пользователь:', value = f"**{member.mention}**" )
	emb.add_field( name = 'Баланс счёта:', value = f"**{money}**" )

	await ctx.send( embed = emb )

@client.command(aliases=["помочь"])
@commands.has_permissions( administrator = True )
async def add_money(ctx, member: nextcord.Member, amount: int):
	with open(f"money/{member.id}.txt", 'r') as file:
		data = file.readlines()
		money = data[1]
		new_money = int(money) + amount
	with open(f"money/{member.id}.txt", 'w') as file:
		file.write(f"{str(member.name)}\n")
		file.write(str(new_money))
	emb = nextcord.Embed( title = 'Добавление средств', colour = nextcord.Color.blue() )
	emb.add_field( name = 'Админ:', value = f"**{ctx.message.author.mention}**" )
	emb.add_field( name = 'Получатель:', value = f"**{member.mention}**" )
	emb.add_field( name = 'Баланс:', value = f"**{money}**" )

	await ctx.send( embed = emb )

@client.command(aliases=["выебать"])
async def porno(ctx, member: nextcord.Member):
	emb = nextcord.Embed( title = 'Ах ах ах', colour = nextcord.Color.orange() )
	emb.add_field( name = 'Начальник:', value = f"**{ctx.message.author.mention}**" )
	emb.add_field( name = 'Получатель:', value = f"**{member.mention}**" )
	emb.set_image( url = waifu.nsfw(category='neko') )

	await ctx.send( embed = emb )

@client.command(aliases=["зарегистрировать", "регистрация"])
@commands.has_permissions( administrator = True )
async def register(ctx, member: nextcord.Member):
	with open(f"money/{member.id}.txt", 'a') as file:
		file.write(f"{member.name}\n")
		file.write("1000")
	with open(f"abilities/{member.id}.txt", 'a') as file:
		file.write(f"{member.name}\n")
		file.write("5")
	emb = nextcord.Embed( title = 'Регистрация пользователя', colour = nextcord.Color.green() )
	emb.add_field( name = 'Админ:', value = f"**{ctx.message.author.mention}**" )
	emb.add_field( name = 'Участник:', value = f"**{member.mention}**" )

	await ctx.send( embed = emb )

@client.command(aliases=["покедекс"])
async def pokedex(ctx, pokemon: str):
	api = f"https://pokeapi.co/api/v2/pokemon/{pokemon}"
	res = requests.get(api)
	poke = res.json()
	for i in poke['abilities']:
		ability = i['ability']['name']
	for i in poke['types']:
		tip = i['type']['name']
	emb = nextcord.Embed( title = 'Покедекс', colour = nextcord.Color.yellow() )
	emb.add_field( name = 'Способности:', value = f"**{ability}**" )
	emb.add_field( name = 'Тип:', value = f"**{tip}**" )
	emb.set_thumbnail( url = f"https://play.pokemonshowdown.com/sprites/ani/{pokemon}.gif" )

	await ctx.send( embed = emb )

client.run(botconfig.TOKEN)