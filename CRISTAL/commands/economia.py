from core import *

async def comando_saldo(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    cristais, bilhetes, _, streak, semanas, slots, energia = obter_dados(usuario.id)
    slots_totais = obter_slots_totais(usuario) if isinstance(usuario, discord.Member) else slots
    bonus_slot = " (+1 booster)" if isinstance(usuario, discord.Member) and usuario_e_booster(usuario) else ""

    await interaction.response.send_message(
        f"💎 **Saldo de {usuario.display_name}**\n"
        f"Cristais: **{cristais:,} {SIGLA}**\n"
        f"🎟️ Bilhetes: **{bilhetes}**\n"
        f"⚡ Energia: **{energia}/{ENERGIA_MAXIMA}**\n"
        f"🔥 Sequência diária: **{streak} dia(s)**\n"
        f"📅 Semanas seguidas: **{semanas}**\n"
        f"🐾 Slots de pets: **{slots_totais}**{bonus_slot}",
        ephemeral=True
    )


@bot.tree.command(name="saldo", description="Mostra seu saldo ou o saldo de outro jogador.")
async def saldo(interaction: discord.Interaction, usuario: discord.Member = None):
    await comando_saldo(interaction, usuario)


@bot.tree.command(name="cs", description="Atalho para ver seus Cristais.")
async def cs(interaction: discord.Interaction, usuario: discord.Member = None):
    await comando_saldo(interaction, usuario)


@bot.tree.command(name="energia", description="Mostra sua energia atual.")
async def energia(interaction: discord.Interaction):
    energia_atual = atualizar_energia(interaction.user.id)

    await interaction.response.send_message(
        f"⚡ Sua energia atual é **{energia_atual}/{ENERGIA_MAXIMA}**.\n"
        f"Recuperação: **{ENERGIA_POR_MINUTO} por minuto**.",
        ephemeral=True
    )


async def comando_diario(interaction: discord.Interaction):
    user_id = interaction.user.id
    criar_usuario(user_id)

    cristais, bilhetes, ultimo_diario, streak, semanas, slots, energia_atual = obter_dados(user_id)

    agora = int(time.time())

    if ultimo_diario > 0:
        restante = COOLDOWN_DIARIO - (agora - ultimo_diario)

        if restante > 0:
            horas = restante // 3600
            minutos = (restante % 3600) // 60

            await interaction.response.send_message(
                f"⏳ Você já coletou seu diário. Volte em **{horas}h {minutos}min**.",
                ephemeral=True
            )
            return

    if ultimo_diario > 0 and agora - ultimo_diario > LIMITE_PERDA_STREAK:
        streak = 0
        semanas = 0

    novo_streak = streak + 1

    if novo_streak > 7:
        novo_streak = 1

    recompensa = RECOMPENSAS_DIA[novo_streak]
    bilhetes_ganhos = 0
    novas_semanas = semanas

    if novo_streak == 7:
        novas_semanas += 1
        bilhetes_ganhos = min(novas_semanas, MAX_BILHETES_SEMANAIS)

    cursor.execute("""
        UPDATE usuarios
        SET cristais = cristais + ?,
            bilhetes = bilhetes + ?,
            ultimo_diario = ?,
            streak_diario = ?,
            semanas_diario = ?
        WHERE user_id = ?
    """, (
        recompensa,
        bilhetes_ganhos,
        agora,
        novo_streak,
        novas_semanas,
        user_id
    ))

    conn.commit()

    texto = (
        f"🎁 Você recebeu **{recompensa:,} {SIGLA}**!\n"
        f"🔥 Sequência atual: **Dia {novo_streak}/7**"
    )

    if bilhetes_ganhos > 0:
        texto += f"\n🎟️ Bônus semanal: **{bilhetes_ganhos} bilhete(s)**!"

    registrar_missao_evento(interaction.user.id, "diario", 1)
    await interaction.response.send_message(texto, ephemeral=True)

    await enviar_log(
        interaction.guild,
        f"📥 **LOG DE ECONOMIA**\n"
        f"Jogador: {interaction.user.mention}\n"
        f"Ação: usou `/dia`\n"
        f"Ganhou: **{recompensa:,} {SIGLA}**\n"
        f"Bilhetes ganhos: **{bilhetes_ganhos}**\n"
        f"Sequência: **{novo_streak}/7**\n"
        f"Semanas: **{novas_semanas}**"
    )


@bot.tree.command(name="diario", description="Receba sua recompensa diária.")
async def diario(interaction: discord.Interaction):
    await comando_diario(interaction)


@bot.tree.command(name="dia", description="Atalho para receber sua recompensa diária.")
async def dia(interaction: discord.Interaction):
    await comando_diario(interaction)


@bot.tree.command(name="doar", description="Doe Cristais para outro jogador.")
async def doar(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    doador = interaction.user

    if usuario.id == doador.id:
        await interaction.response.send_message("❌ Você não pode doar para si mesmo.", ephemeral=True)
        return

    if valor <= 0:
        await interaction.response.send_message("❌ O valor precisa ser maior que zero.", ephemeral=True)
        return

    saldo_doador = obter_saldo(doador.id)

    if saldo_doador < valor:
        await interaction.response.send_message("❌ Você não tem Cristais suficientes.", ephemeral=True)
        return

    alterar_saldo(doador.id, -valor)
    alterar_saldo(usuario.id, valor)

    await interaction.response.send_message(
        f"💸 {doador.mention} doou **{valor:,} {SIGLA}** para {usuario.mention}."
    )

    await enviar_log(
        interaction.guild,
        f"💸 **LOG DE TRANSFERÊNCIA**\n"
        f"De: {doador.mention}\n"
        f"Para: {usuario.mention}\n"
        f"Valor: **{valor:,} {SIGLA}**"
    )


async def comando_ranking(interaction: discord.Interaction):
    cursor.execute(
        "SELECT user_id, cristais FROM usuarios ORDER BY cristais DESC LIMIT 10"
    )
    resultados = cursor.fetchall()

    if not resultados:
        await interaction.response.send_message("Ainda não existe ranking.")
        return

    texto = "🏆 **Ranking de Cristais**\n\n"

    for posicao, (user_id, cristais) in enumerate(resultados, start=1):
        texto += f"**{posicao}.** <@{user_id}> — **{cristais:,} {SIGLA}**\n"

    await interaction.response.send_message(texto)


@bot.tree.command(name="ranking", description="Mostra os jogadores com mais Cristais.")
async def ranking(interaction: discord.Interaction):
    await comando_ranking(interaction)


@bot.tree.command(name="top", description="Atalho para o ranking.")
async def top(interaction: discord.Interaction):
    await comando_ranking(interaction)


async def comando_inventario(interaction: discord.Interaction):
    cristais, bilhetes, _, streak, semanas, slots, energia_atual = obter_dados(interaction.user.id)
    total_pets = contar_pets(interaction.user.id)
    slots_totais = obter_slots_totais(interaction.user)
    bonus_slot = " (+1 booster)" if usuario_e_booster(interaction.user) else ""

    await interaction.response.send_message(
        f"🎒 **Inventário de {interaction.user.display_name}**\n"
        f"💎 Cristais: **{cristais:,} {SIGLA}**\n"
        f"🎟️ Bilhetes: **{bilhetes}**\n"
        f"⚡ Energia: **{energia_atual}/{ENERGIA_MAXIMA}**\n"
        f"🐾 Pets: **{total_pets}**\n"
        f"📌 Slots equipáveis: **{slots_totais}**{bonus_slot}\n\n"
        f"Use **/pets** para ver sua coleção. Use **/itens** para ver seus itens.",
        ephemeral=True
    )


@bot.tree.command(name="inventario", description="Mostra seu inventário.")
async def inventario(interaction: discord.Interaction):
    await comando_inventario(interaction)


@bot.tree.command(name="inv", description="Atalho para o inventário.")
async def inv(interaction: discord.Interaction):
    await comando_inventario(interaction)
