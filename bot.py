import os
import discord
import random
from discord.ext import commands
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.command(name='roletarussa')
async def roleta_russa(ctx, balas: int, *jogadores: discord.Member):
    if len(jogadores) > 6:
        await ctx.send("O número máximo de jogadores é 6.")
        return

    if balas >= len(jogadores):
        await ctx.send("Número de balas deve ser menor do que o número de jogadores.")
        return

    roleta = [False] * len(jogadores)
    for _ in range(balas):
        index = random.choice(
            [i for i, ocupado in enumerate(roleta) if not ocupado]
        )
        roleta[index] = True

    for jogador, acertado in zip(jogadores, roleta):
        if acertado:
            await ctx.send(f'{jogador.mention} levou uma bala! 🌟')
            try:
                await jogador.edit(mute=True)
                await asyncio.sleep(600)  # 10 minutos
                await jogador.edit(mute=False)
                await ctx.send(f'{jogador.mention} está desmutado!')
            except discord.Forbidden:
                await ctx.send(f"Não tenho permissão para mutar {jogador.mention}.")
        else:
            await ctx.send(f'{jogador.mention} escapou desta vez! 🎉')

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
