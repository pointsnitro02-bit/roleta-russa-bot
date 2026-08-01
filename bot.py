import os
import discord
from discord.ext import commands
from discord import Intents, Embed, ButtonStyle
from discord.ui import Button, View
import random
import asyncio

intents = Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.slash_command(name='roletarussa', description='Iniciar um jogo de roleta russa')
async def roleta_russa(ctx, balas: int, jogadores: int):
    if jogadores > 6 or jogadores < 2:
        await ctx.respond("O número de jogadores deve ser entre 2 e 6.")
        return
    
    if balas > 5 or balas < 1:
        await ctx.respond("O número de balas deve ser entre 1 e 5.")
        return

    players = []
    embed = Embed(title="Roleta Russa", description="Clique para entrar no jogo!")
    embed.add_field(name="Balas", value=f"{balas}", inline=True)
    embed.add_field(name="Jogadores", value=f"0/{jogadores}", inline=True)
    
    view = View()

    join_button = Button(label="Entrar", style=ButtonStyle.primary)

    async def join_callback(interaction):
        if interaction.user not in players:
            if len(players) < jogadores:
                players.append(interaction.user)
                embed.set_field_at(1, name="Jogadores", value=f"{len(players)}/{jogadores}", inline=True)
                await interaction.response.edit_message(embed=embed)
                await interaction.followup.send(f"{interaction.user.mention} entrou no jogo!", ephemeral=True)
            else:
                await interaction.response.send_message("O jogo já está cheio!", ephemeral=True)
        else:
            await interaction.response.send_message("Você já entrou no jogo!", ephemeral=True)

    join_button.callback = join_callback
    view.add_item(join_button)

    await ctx.respond(embed=embed, view=view)
    await asyncio.sleep(60)

    if len(players) < 2:
        await ctx.channel.send("Não há jogadores suficientes para começar.")
        return

    await ctx.channel.send("O jogo vai começar!")

    roleta = [False] * len(players)
    for _ in range(balas):
        index = random.choice([i for i, v in enumerate(roleta) if not v])
        roleta[index] = True

    for i, (jogador, acertado) in enumerate(zip(players, roleta), start=1):
        pull_trigger_view = View()
        pull_button = Button(label=f"Puxar o Gatilho (Tiros restantes: {i}/{len(players)})", style=ButtonStyle.danger)

        async def pull_trigger(interaction):
            if interaction.user == jogador:
                await interaction.response.defer()
                if acertado:
                    await interaction.followup.send(f'{jogador.mention} levou uma bala! 🌟 Estás mutado por 10 minutos.')
                    await jogador.edit(mute=True)
                    await asyncio.sleep(600)
                    await jogador.edit(mute=False)
                else:
                    await interaction.followup.send(f'{jogador.mention} escapou desta vez! 🎉')
            else:
                await interaction.response.send_message("Não é sua vez!", ephemeral=True)

        pull_button.callback = pull_trigger
        pull_trigger_view.add_item(pull_button)

        await ctx.send(
            embed=Embed(
                title="Sua vez!",
                description=f"{jogador.mention}, pressione o botão para puxar o gatilho.",
                color=0xFF0000
            ),
            view=pull_trigger_view
        )

        await asyncio.sleep(60)  # Tempo de espera por jogador

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
