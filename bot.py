import os
import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Intents, Embed, ButtonStyle
from nextcord.ui import Button, View
import random

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
    if jogadores < 2 or jogadores > 6:
        await interaction.response.send_message("O número de jogadores deve ser entre 2 e 6.")
        return
    
    if balas != 1:
        await interaction.response.send_message("Deve haver apenas 1 bala. Será aleatoriamente distribuída no tambor de 6!")
        return
    
    players = []
    embed = Embed(
        title="🎯 **Russian Roulette**",
        description="> Test your luck. Only one survives.\n\n"
                    "⚙️ **Cylinder**\n`1 / 6` loaded\n\n"
                    f"👥 **Players**\n`0 / {jogadores}`\n\n"
                    "⚠️ *Players eliminated receive a **10-minute mute**.*",
        color=0xff6347
    )
    
    view = View()

    join_button = Button(label="Entrar", style=ButtonStyle.primary)

    async def join_callback(button_interaction: nextcord.Interaction):
        if button_interaction.user not in players:
            if len(players) < jogadores:
                players.append(button_interaction.user)
                embed.description = (
                    "> Test your luck. Only one survives.\n\n"
                    "⚙️ **Cylinder**\n`1 / 6` loaded\n\n"
                    f"👥 **Players**\n`{len(players)} / {jogadores}`\n\n"
                    "⚠️ *Players eliminated receive a **10-minute mute**.*"
                )
                await button_interaction.response.edit_message(embed=embed)

                if len(players) == jogadores:
                    # Adicione o botão para iniciar o jogo
                    start_button = Button(label="Iniciar Jogo", style=ButtonStyle.success)

                    async def start_game_callback(start_interaction: nextcord.Interaction):
                        await start_game(start_interaction, players)

                    start_button.callback = start_game_callback
                    view.clear_items()  # Limpa o botão existente
                    view.add_item(start_button)
                    await button_interaction.edit_original_response(view=view)

            else:
                await button_interaction.response.send_message("O jogo já está cheio!", ephemeral=True)
        else:
            await button_interaction.response.send_message("Você já entrou no jogo!", ephemeral=True)

    join_button.callback = join_callback
    view.add_item(join_button)

    await interaction.response.send_message(embed=embed, view=view)

    # Espera por 60 segundos para que outros jogadores possam entrar
    await asyncio.sleep(60)
    if len(players) >= 2 and len(players) < jogadores:
        await start_game(interaction, players)
    elif len(players) < 2:
        await interaction.edit_original_response(content="O jogo foi encerrado por falta de jogadores suficientes.", embed=None, view=None)

async def start_game(interaction: nextcord.Interaction, players):
    embed = Embed(
        title="🎯 **Russian Roulette**",
        description="O jogo começou! Boa sorte a todos!",
        color=0xff6347
    )

    await interaction.edit_original_response(embed=embed, view=None)

    roleta = [False] * 5 + [True]
    random.shuffle(roleta)

    for jogador, acertado in zip(players, roleta):
        pull_trigger_view = View()
        pull_button = Button(label="Puxar o Gatilho", style=ButtonStyle.danger)

        async def pull_trigger(button_interaction: nextcord.Interaction, current_jogador=jogador, current_acertado=acertado):
            if button_interaction.user == current_jogador:
                await button_interaction.response.edit_message(view=None)
                if current_acertado:
                    embed.description = f"{current_jogador.mention} levou uma bala! 🌟 Estás mutado por 10 minutos."
                    await button_interaction.edit_original_response(embed=embed)
                    await current_jogador.edit(mute=True)

                    await asyncio.sleep(600)
                    try:
                        await current_jogador.edit(mute=False)
                    except Exception as e:
                        print(f"Erro ao desmutar {current_jogador}: {e}")
                else:
                    embed.description = f"{current_jogador.mention} escapou desta vez! 🎉"
                    await button_interaction.edit_original_response(embed=embed)

                return
            else:
                await button_interaction.response.send_message("Não é sua vez!", ephemeral=True)

        pull_button.callback = pull_trigger
        pull_trigger_view.add_item(pull_button)

        embed.description = f"{jogador.mention}, pronto para testar sua sorte?"
        await interaction.edit_original_response(embed=embed, view=pull_trigger_view)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
