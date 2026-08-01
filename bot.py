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
    if jogadores > 6 or jogadores < 2:
        await interaction.response.send_message("O número de jogadores deve ser entre 2 e 6.")
        return
    
    if balas != 1:
        await interaction.response.send_message("Deve haver apenas 1 bala. Será aleatoriamente distribuída no tambor de 6!")
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

    async def join_callback(button_interaction: nextcord.Interaction):
        if button_interaction.user not in players:
            if len(players) < jogadores:
                players.append(button_interaction.user)
                embed.set_field_at(1, name="Jogadores", value=f"{len(players)}/{jogadores}", inline=True)
                await button_interaction.response.edit_message(embed=embed)
                await button_interaction.followup.send(f"{button_interaction.user.mention} entrou no jogo!", ephemeral=True)
            else:
                await button_interaction.response.send_message("O jogo já está cheio!", ephemeral=True)
        else:
            await button_interaction.response.send_message("Você já entrou no jogo!", ephemeral=True)

    join_button.callback = join_callback
    view.add_item(join_button)

    await interaction.response.send_message(embed=embed, view=view)

    await asyncio.sleep(60)  # Aguarda 1 minuto para o jogo começar/permitir que os jogadores entrem

    if len(players) < 2:
        await interaction.edit_original_response(content="Não há jogadores suficientes para começar.", embed=embed, view=None)
        return

    embed.description = "O jogo começou! Boa sorte a todos!"
    await interaction.edit_original_response(embed=embed, view=None)

    roleta = [False] * 5 + [True]  # Um tambor de 6 onde uma posição é verdadeira para simular uma bala
    random.shuffle(roleta)  # Mistura o cilindro para intensificar a aleatoriedade

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

                    # Mantenha o jogador mutado por 10 minutos
                    await asyncio.sleep(600)
                    try:
                        await current_jogador.edit(mute=False)
                    except Exception as e:
                        print(f"Erro ao desmutar {current_jogador}: {e}")
                else:
                    embed.description = f"{current_jogador.mention} escapou desta vez! 🎉"
                    await button_interaction.edit_original_response(embed=embed)

                # Ao fim de interação, independente de acertado ou não
                return
            else:
                await button_interaction.response.send_message("Não é sua vez!", ephemeral=True)

        pull_button.callback = pull_trigger
        pull_trigger_view.add_item(pull_button)

        # Aguarda a interação com o botão de puxar o gatilho
        embed.description = f"{jogador.mention}, pressione o botão para puxar o gatilho."
        await interaction.edit_original_response(embed=embed, view=pull_trigger_view)

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
