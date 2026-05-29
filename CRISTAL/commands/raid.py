from core import *
from discord.ext import tasks

# ============================================================
# RAID — ataque público, top 5 editável e spawn automático
# ============================================================

RAID_AUTO_HORARIOS = [0, 6, 12, 18]
_raid_auto_iniciada = False
_ultimo_spawn_auto = None

# Garante colunas novas sem quebrar bancos antigos.
try:
    adicionar_coluna_se_nao_existir("raids", "top_message_id", "INTEGER", 0)
    adicionar_coluna_se_nao_existir("raids", "canal_id", "INTEGER", 0)
    conn.commit()
except Exception:
    pass


def texto_top_raid(raid_id: int, boss_nome: str, mutacao: str):
    cursor.execute(
        """
        SELECT user_id, dano
        FROM raid_participantes
        WHERE raid_id = ?
        ORDER BY dano DESC
        LIMIT 5
        """,
        (raid_id,)
    )
    resultados = cursor.fetchall()

    if not resultados:
        return (
            f"🏆 **Top 5 da Raid — {boss_nome} {mutacao}**\n"
            f"Ainda ninguém atacou."
        )

    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    linhas = []

    for posicao, (user_id, dano) in enumerate(resultados):
        linhas.append(f"{medalhas[posicao]} <@{user_id}> — **{dano:,} dano**")

    return (
        f"🏆 **Top 5 da Raid — {boss_nome} {mutacao}**\n"
        + "\n".join(linhas)
    )


async def atualizar_top_raid(channel: discord.TextChannel, raid_id: int, boss_nome: str, mutacao: str):
    """Edita uma mensagem fixa de top 5; se não existir, cria."""
    texto = texto_top_raid(raid_id, boss_nome, mutacao)

    cursor.execute("SELECT top_message_id FROM raids WHERE raid_id = ?", (raid_id,))
    row = cursor.fetchone()
    top_message_id = row[0] if row else 0

    if top_message_id:
        try:
            msg = await channel.fetch_message(top_message_id)
            await msg.edit(content=texto)
            return
        except Exception:
            pass

    msg = await channel.send(texto)
    cursor.execute(
        "UPDATE raids SET top_message_id = ?, canal_id = ? WHERE raid_id = ?",
        (msg.id, channel.id, raid_id)
    )
    conn.commit()


async def criar_raid_automatica(guild: discord.Guild):
    if guild is None:
        return None

    raid_atual = obter_raid_ativa(guild.id)
    agora = int(time.time())

    if raid_atual and agora < raid_atual[7]:
        return None

    if raid_atual and agora >= raid_atual[7]:
        await finalizar_raid_por_id(guild, raid_atual[0])

    boss = escolher_boss_raid()
    inicio = agora
    fim = agora + RAID_DURACAO

    canal = canal_por_chave(guild, "raid")
    canal_id = canal.id if canal else 0

    cursor.execute("""
        INSERT INTO raids
        (guild_id, boss_nome, boss_linha, boss_emoji, raridade, mutacao, inicio, fim, ativa, canal_id, top_message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 0)
    """, (
        guild.id,
        boss["nome"],
        boss["linha"],
        boss["emoji"],
        "Mítico",
        "Corrompido",
        inicio,
        fim,
        canal_id
    ))
    conn.commit()

    raid_id = cursor.lastrowid

    mensagem = (
        f"⚠️ **RAID INICIADA AUTOMATICAMENTE!**\n\n"
        f"{boss['emoji']} **{boss['nome']} Corrompido** apareceu!\n"
        f"Raridade: **Mítico**\n"
        f"⏳ Tempo: **2 horas**\n\n"
        f"Use **/raid** para atacar. Cada jogador pode atacar **1 vez**."
    )

    if canal:
        await canal.send(mensagem)
        await atualizar_top_raid(canal, raid_id, boss["nome"], "Corrompido")
    else:
        await enviar_log(guild, mensagem)

    await enviar_log(
        guild,
        f"⚔️ **LOG RAID AUTO**\nRaid automática iniciada.\nBoss: **{boss['nome']} Corrompido**"
    )

    return raid_id


@tasks.loop(minutes=1)
async def tarefa_raid_automatica():
    global _ultimo_spawn_auto

    agora_local = time.localtime()
    hora = agora_local.tm_hour
    minuto = agora_local.tm_min
    chave = time.strftime("%Y-%m-%d_%H", agora_local)

    if minuto != 0 or hora not in RAID_AUTO_HORARIOS:
        return

    if _ultimo_spawn_auto == chave:
        return

    _ultimo_spawn_auto = chave

    for guild in bot.guilds:
        try:
            await criar_raid_automatica(guild)
        except Exception as erro:
            await enviar_log(guild, f"❌ Erro ao iniciar raid automática: `{erro}`")


def iniciar_tarefa_raid_automatica():
    global _raid_auto_iniciada

    if _raid_auto_iniciada:
        return

    if not tarefa_raid_automatica.is_running():
        tarefa_raid_automatica.start()
        _raid_auto_iniciada = True


@bot.tree.command(name="raid", description="Participa da raid ativa.")
async def raid(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("❌ Raid só funciona em servidor.", ephemeral=True)
        return

    if not canal_correto(interaction, RAID_CANAL):
        await interaction.response.send_message(f"❌ Use este comando no canal {nome_canal('raid')}.", ephemeral=True)
        return

    raid_atual = obter_raid_ativa(interaction.guild.id)

    if not raid_atual:
        await interaction.response.send_message("❌ Não existe raid ativa no momento.", ephemeral=True)
        return

    raid_id, boss_nome, boss_linha, boss_emoji, raridade, mutacao, inicio, fim = raid_atual
    agora = int(time.time())

    if agora >= fim:
        texto = await finalizar_raid_por_id(interaction.guild, raid_id)
        await interaction.response.send_message(texto)
        return

    cursor.execute(
        "SELECT dano FROM raid_participantes WHERE raid_id = ? AND user_id = ?",
        (raid_id, interaction.user.id)
    )
    ja_participou = cursor.fetchone()

    if ja_participou:
        await interaction.response.send_message(
            f"❌ Você já atacou esta raid.\n"
            f"Seu dano: **{ja_participou[0]:,}**",
            ephemeral=True
        )
        return

    bonus, detalhes = calcular_bonus_linha(interaction.user.id, "Raid")
    bonus_forca = bonus_forca_raid(interaction.user.id)
    bonus_total = bonus + bonus_forca
    dano_base = random.randint(700, 1600)
    variacao = random.uniform(0.9, 1.15)
    dano_final = int(dano_base * (1 + bonus_total) * variacao)

    if bonus_forca > 0:
        consumir_buff(interaction.user.id, "forca")

    cursor.execute(
        "INSERT INTO raid_participantes (raid_id, user_id, dano) VALUES (?, ?, ?)",
        (raid_id, interaction.user.id, dano_final)
    )
    conn.commit()
    registrar_missao_evento(interaction.user.id, "raid", 1)
    registrar_missao_evento(interaction.user.id, "raid_dano", dano_final)

    levelups = adicionar_xp_pets_equipados(interaction.user.id, "Raid", XP_RAID)

    restante = fim - agora
    minutos = restante // 60
    detalhes_txt = "\n".join(detalhes) if detalhes else "Nenhum pet equipado da linha **Raid**."
    if bonus_forca > 0:
        detalhes_txt += f"\n💪 Poção de Força ({bonus_forca * 100:.1f}%)"
    xp_txt = "\n".join(levelups) if levelups else f"Pets equipados ganharam XP de raid."

    await interaction.response.send_message(
        f"⚔️ {interaction.user.mention} atacou {boss_emoji} **{boss_nome} {mutacao}**!\n\n"
        f"💥 Dano final: **{dano_final:,}**\n"
        f"⏳ Tempo restante: **{minutos} min**\n\n"
        f"Bônus total: **{bonus_total * 100:.1f}%**\n"
        f"Pets considerados:\n{detalhes_txt}\n\n"
        f"XP:\n{xp_txt}"
    )

    await atualizar_top_raid(interaction.channel, raid_id, boss_nome, mutacao)

    await enviar_log(
        interaction.guild,
        f"⚔️ **LOG DE RAID**\n"
        f"Jogador: {interaction.user.mention}\n"
        f"Boss: **{boss_nome} {mutacao}**\n"
        f"Dano: **{dano_final:,}**"
    )
