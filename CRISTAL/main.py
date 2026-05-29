from core import bot, TOKEN

# Importa os módulos de comandos para registrar slash commands no bot.
import commands.economia
import commands.pets
import commands.profissoes
import commands.raid
import commands.admin
import commands.loja
import commands.cassino
import commands.eventos
import commands.ajuda
import commands.perfil
import commands.missoes


@bot.event
async def on_ready():
    commands.eventos.iniciar_tarefas_eventos()
    commands.raid.iniciar_tarefa_raid_automatica()
    await bot.tree.sync()
    print(f"Bot Cristal inicializado como {bot.user}")


if __name__ == "__main__":
    bot.run(TOKEN)
