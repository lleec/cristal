from core import *

profissao_group = app_commands.Group(name="profissao", description="Comandos de profissão.")


@profissao_group.command(name="escolher", description="Escolhe sua profissão.")
@app_commands.choices(tipo=[
    app_commands.Choice(name="pesca", value="pesca"),
    app_commands.Choice(name="mineracao", value="mineracao"),
    app_commands.Choice(name="caca", value="caca"),
    app_commands.Choice(name="exploracao", value="exploracao"),
    app_commands.Choice(name="trabalho", value="trabalho"),
])
async def profissao_escolher(interaction: discord.Interaction, tipo: app_commands.Choice[str]):
    criar_usuario(interaction.user.id)
    nova = tipo.value
    config = PROFISSOES[nova]
    profissao_atual, ultima_troca = obter_profissao(interaction.user.id)
    agora = int(time.time())

    if profissao_atual == nova:
        await interaction.response.send_message(
            f"❌ Você já está na profissão **{config['nome']}**.",
            ephemeral=True
        )
        return

    if ultima_troca > 0 and agora - ultima_troca < COOLDOWN_TROCA_PROFISSAO:
        restante = COOLDOWN_TROCA_PROFISSAO - (agora - ultima_troca)
        horas = restante // 3600
        minutos = (restante % 3600) // 60
        await interaction.response.send_message(
            f"⏳ Você só pode trocar de profissão em **{horas}h {minutos}min**.",
            ephemeral=True
        )
        return

    # Remove cargos antigos e adiciona o novo, se os cargos existirem.
    if isinstance(interaction.user, discord.Member):
        cargos_para_remover = []
        for dados in PROFISSOES.values():
            cargo = discord.utils.get(interaction.guild.roles, name=dados["cargo"])
            if cargo and cargo in interaction.user.roles:
                cargos_para_remover.append(cargo)

        if cargos_para_remover:
            await interaction.user.remove_roles(*cargos_para_remover, reason="Troca de profissão Cristal")

        novo_cargo = discord.utils.get(interaction.guild.roles, name=config["cargo"])
        if novo_cargo:
            await interaction.user.add_roles(novo_cargo, reason="Escolha de profissão Cristal")

    cursor.execute(
        "UPDATE usuarios SET profissao = ?, ultima_troca_profissao = ? WHERE user_id = ?",
        (nova, agora, interaction.user.id)
    )
    conn.commit()

    await interaction.response.send_message(
        f"{config['emoji']} Você escolheu a profissão **{config['nome']}**.\n"
        f"Canal correto: **#{config['canal']}**\n"
        f"Comando: **/{config['comando']}**",
        ephemeral=True
    )


@profissao_group.command(name="minha", description="Mostra sua profissão atual.")
async def profissao_minha(interaction: discord.Interaction):
    profissao_atual, ultima_troca = obter_profissao(interaction.user.id)

    if not profissao_atual:
        await interaction.response.send_message(
            "Você ainda não escolheu profissão. Use `/profissao escolher`.",
            ephemeral=True
        )
        return

    config = PROFISSOES[profissao_atual]
    await interaction.response.send_message(
        f"{config['emoji']} Sua profissão atual é **{config['nome']}**.\n"
        f"Canal: **#{config['canal']}**\n"
        f"Comando: **/{config['comando']}**",
        ephemeral=True
    )


@profissao_group.command(name="sair", description="Sai da profissão atual.")
async def profissao_sair(interaction: discord.Interaction):
    profissao_atual, _ = obter_profissao(interaction.user.id)

    if not profissao_atual:
        await interaction.response.send_message("Você não tem profissão ativa.", ephemeral=True)
        return

    if isinstance(interaction.user, discord.Member):
        config = PROFISSOES.get(profissao_atual)
        if config:
            cargo = discord.utils.get(interaction.guild.roles, name=config["cargo"])
            if cargo and cargo in interaction.user.roles:
                await interaction.user.remove_roles(cargo, reason="Saiu da profissão Cristal")

    cursor.execute(
        "UPDATE usuarios SET profissao = '', ultima_troca_profissao = ? WHERE user_id = ?",
        (int(time.time()), interaction.user.id)
    )
    conn.commit()

    await interaction.response.send_message("✅ Você saiu da sua profissão atual.", ephemeral=True)


bot.tree.add_command(profissao_group)


@bot.tree.command(name="pescar", description="Trabalha como Pescador no canal #pesca.")
async def pescar(interaction: discord.Interaction):
    await executar_atividade(interaction, "pesca")


@bot.tree.command(name="minerar", description="Trabalha como Minerador no canal #mineracao.")
async def minerar(interaction: discord.Interaction):
    await executar_atividade(interaction, "mineracao")


@bot.tree.command(name="cacar", description="Trabalha como Caçador no canal #caca.")
async def cacar(interaction: discord.Interaction):
    await executar_atividade(interaction, "caca")


@bot.tree.command(name="explorar", description="Trabalha como Explorador no canal #exploracao.")
async def explorar(interaction: discord.Interaction):
    await executar_atividade(interaction, "exploracao")


@bot.tree.command(name="trabalhar", description="Trabalha como Trabalhador no canal #trabalho.")
async def trabalhar(interaction: discord.Interaction):
    await executar_atividade(interaction, "trabalho")
