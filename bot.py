import os
import nextcord
from nextcord.ext import commands
from nextcord import Intents, Embed, ButtonStyle
from nextcord.ui import Button, View
import random
import asyncio

intents = Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')

@bot.slash_command(name='roletarussa', description='Iniciar um jogo de roleta russa')
async def roleta_russa(interaction: nextcord.Interaction, balas: int, jogadores: int):
    if jogadores > 6 or jogadores < 2:
        await interaction.response.send_message("O número de jogadores deve ser entre 2 e 6.")
        return
    
    if balas > 1:
        await interaction.response.send_message("Apenas 1 bala deve ser escolhida. Será aleatoriamente distribuída no pente de 6!")
        return
    
    players = []
    embed = Embed(
        title="🔫 Roleta Russa",
        description="Clique para entrar no jogo!",
        color=0xff6347
    )
    embed.add_field(name="Balas no cilindro", value="1 em 6", inline=True)
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

    await interaction.response.send_message(embed=embed, view=view)
    await asyncio.sleep(60)

    if len(players) < 2:
        await interaction.channel.send("Não há jogadores suficientes para começar.")
        return

    await interaction.channel.send("O jogo vai começar!")

    roleta = [False] * 5 + [True]  # Um pente de 6 no qual uma posição é verdade para simular uma bala
    random.shuffle(roleta)  # Mistura o cilindro para aumentar a aleatoriedade

    for jogador, acertado in zip(players, roleta):
        pull_trigger_view = View()
        pull_button = Button(label="Puxar o Gatilho", style=ButtonStyle.danger)

        async def pull_trigger(interaction):
            if interaction.user == jogador:
                await interaction.response.defer()
                if acertado:
                    await interaction.followup.send(f"{jogador.mention} levou uma bala! 🌟 Estás mutado por 10 minutos.")
                    await jogador.edit(mute=True)
                    await asyncio.sleep(600)
                    await jogador.edit(mute=False)
                else:
                    await interaction.followup.send(f"{jogador.mention} escapou desta vez! 🎉")
            else:
                await interaction.response.send_message("Não é sua vez!", ephemeral=True)

        pull_button.callback = pull_trigger
        pull_trigger_view.add_item(pull_button)

        await interaction.channel.send(
            embed=Embed(
                title="Sua vez!",
                description=f"{jogador.mention}, pressione o botão para puxar o gatilho.",
                color=0xff4500
            ),
            view=pull_trigger_view
        )

        await asyncio.sleep(60)  # Tempo de espera por jogador

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
