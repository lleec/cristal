from core import *
from discord.ext import tasks


evento_group = app_commands.Group(name="evento", description="Comandos administrativos de eventos.")


@evento_group.command(name="iniciar", description="Inicia um mini-evento em uma profissão.")
@app_commands.choices(tipo=[
    app_commands.Choice(name="pesca", value="pesca"),
    app_commands.Choice(name="mineracao", value="mineracao"),
    app_commands.Choice(name="caca", value="caca"),
    app_commands.Choice(name="exploracao", value="exploracao"),
    app_commands.Choice(name="trabalho", value="trabalho"),
])
async def evento_iniciar(interaction: discord.Interaction, tipo: app_commands.Choice[str], minutos: int = 30):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.", ephemeral=True)
        return

    minutos = max(5, min(180, minutos))
    fim = await anunciar_evento_profissao(interaction.guild, tipo.value, minutos * 60)
    dados = EVENTOS_PROFISSAO[tipo.value]

    await interaction.response.send_message(
        f"✅ Evento iniciado: **{dados['nome']}**\n"
        f"Canal: {nome_canal(PROFISSOES[tipo.value]['canal'])}\n"
        f"Duração: **{minutos} minutos**.",
        ephemeral=True
    )

    await enviar_log(
        interaction.guild,
        f"✨ **LOG EVENTO**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Evento: **{dados['nome']}**\n"
        f"Duração: **{minutos} min**"
    )


@evento_group.command(name="parar", description="Encerra um mini-evento de profissão.")
@app_commands.choices(tipo=[
    app_commands.Choice(name="pesca", value="pesca"),
    app_commands.Choice(name="mineracao", value="mineracao"),
    app_commands.Choice(name="caca", value="caca"),
    app_commands.Choice(name="exploracao", value="exploracao"),
    app_commands.Choice(name="trabalho", value="trabalho"),
])
async def evento_parar(interaction: discord.Interaction, tipo: app_commands.Choice[str]):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.", ephemeral=True)
        return

    encerrar_evento_profissao(interaction.guild.id, tipo.value)
    await interaction.response.send_message(
        f"✅ Evento de **{PROFISSOES[tipo.value]['nome']}** encerrado.",
        ephemeral=True
    )


@evento_group.command(name="listar", description="Lista eventos ativos.")
async def evento_listar(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.", ephemeral=True)
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.", ephemeral=True)
        return

    eventos = listar_eventos_ativos(interaction.guild.id)

    if not eventos:
        await interaction.response.send_message("Nenhum evento ativo no momento.", ephemeral=True)
        return

    agora = int(time.time())
    texto = "✨ **Eventos ativos**\n\n"
    for nome, chave_profissao, fim in eventos:
        restante = max(0, fim - agora)
        minutos = restante // 60
        canal = nome_canal(PROFISSOES[chave_profissao]["canal"])
        texto += f"• **{nome}** em {canal} — **{minutos} min** restantes\n"

    await interaction.response.send_message(texto, ephemeral=True)


bot.tree.add_command(evento_group)


@tasks.loop(minutes=MINI_EVENTO_CHECK_MINUTOS)
async def mini_eventos_loop():
    for guild in bot.guilds:
        if random.random() * 100 >= MINI_EVENTO_CHANCE:
            continue

        opcoes = []
        for chave in PROFISSOES.keys():
            if not evento_ativo(guild.id, chave):
                opcoes.append(chave)

        if not opcoes:
            continue

        chave = random.choice(opcoes)
        await anunciar_evento_profissao(guild, chave, MINI_EVENTO_DURACAO)
        await enviar_log(
            guild,
            f"✨ **LOG EVENTO AUTOMÁTICO**\n"
            f"Evento: **{EVENTOS_PROFISSAO[chave]['nome']}**\n"
            f"Canal: {nome_canal(PROFISSOES[chave]['canal'])}\n"
            f"Duração: **{MINI_EVENTO_DURACAO // 60} min**"
        )


@mini_eventos_loop.before_loop
async def antes_mini_eventos_loop():
    await bot.wait_until_ready()


def iniciar_tarefas_eventos():
    if not mini_eventos_loop.is_running():
        mini_eventos_loop.start()
