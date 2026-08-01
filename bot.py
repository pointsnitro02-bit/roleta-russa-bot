import os
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

    await asyncio.sleep(60)  # Aguarda 1 minuto para o jogo começar/permitir que os jogadores entrem

    if len(players) < 2:
        await interaction.edit_original_response(content="Não há jogadores suficientes para começar.", embed=embed, view=None)
        return

    embed.description = "O jogo começou! Boa sorte a todos!"
    await interaction.edit_original_response(embed=embed, view=None)

    roleta = [False] * 5 + [True]  # Um pente de 6 no qual uma posição é verdade para simular uma bala
    random.shuffle(roleta)  # Mistura o cilindro para intensificar a aleatoriedade

    for jogador, acertado in zip(players, roleta):
        pull_trigger_view = View()
        pull_button = Button(label="Puxar o Gatilho", style=ButtonStyle.danger)
        
        async def pull_trigger(interaction, jogador=jogador, acertado=acertado):
            if interaction.user == jogador:
                await interaction.response.edit_message(view=None)
                if acertado:
                    embed.description = f"{jogador.mention} levou uma bala! 🌟 Estás mutado por 10 minutos."
                    await interaction.edit_original_response(embed=embed)
                    await jogador.edit(mute=True)
                else:
                    embed.description = f"{jogador.mention} escapou desta vez! 🎉"
                    await interaction.edit_original_response(embed=embed)
            else:
                await interaction.response.send_message("Não é sua vez!", ephemeral=True)

        pull_button.callback = pull_trigger
        pull_trigger_view.add_item(pull_button)

        embed.description = f"{jogador.mention}, pressione o botão para puxar o gatilho."
        await interaction.edit_original_response(embed=embed, view=pull_trigger_view)

    # Caso um jogador leve um tiro, este seria o loop breaking, e a mute execução por 10 minutos
    await asyncio.sleep(600)  # 10 minutos de mudo para o jogador que levou o tiro
    try:
        await jogador.edit(mute=False)  # Excluído do específico usuário
    except:
        pass

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
