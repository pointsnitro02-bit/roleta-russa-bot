import os
import discord
from discord.ext import commands
from discord import ButtonStyle, Embed, Interaction, Message
import random

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

    embed = Embed(title="Roleta Russa", description="Clique para entrar no jogo!")
    embed.add_field(name="Balas", value=f"{balas}", inline=True)
    embed.add_field(name="Participantes", value=f"{' '.join([member.mention for member in jogadores])}", inline=True)

    message = await ctx.send(embed=embed, components=[Button(style=ButtonStyle.primary, label='Entrar')])

    players = []
    def check(interaction):
        return interaction.message.id == message.id
    
    for _ in range(len(jogadores)):
        try:
            interaction = await bot.wait_for('button_click', check=check, timeout=60.0)
            await interaction.respond("Você entrou no jogo!")
            players.append(interaction.user)
        except asyncio.TimeoutError:
            break
    
    if len(players) < len(jogadores):
        await ctx.send("Nem todos os jogadores entraram no jogo.")
        return
    
    await ctx.send("Todos os jogadores estão prontos! O jogo vai começar!")
    
    roleta = [False] * len(players)
    for _ in range(balas):
        index = random.choice([i for i, ocupado in enumerate(roleta) if not ocupado])
        roleta[index] = True

    for i, (jogador, acertado) in enumerate(zip(players, roleta), start=1):
        button_message = await ctx.send(
            embed=Embed(
                title="Sua vez!",
                description=f"{jogador.mention}, pressione o botão para puxar o gatilho.",
                color=0xFF0000
            ),
            components=[Button(style=ButtonStyle.danger, label=f"Puxar o Gatilho (Tiros restantes: {i}/{len(players)})")]
        )
        
        interaction = await bot.wait_for('button_click', check=lambda i: i.user.id == jogador.id)
        await interaction.respond("Puxando o gatilho...")

        if acertado:
            await ctx.send(f'{jogador.mention} levou uma bala! 🌟 Estás mutado por 10 minutos.')
            await jogador.edit(mute=True)
            await asyncio.sleep(600)
            await jogador.edit(mute=False)
        else:
            await ctx.send(f'{jogador.mention} escapou desta vez! 🎉')

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
