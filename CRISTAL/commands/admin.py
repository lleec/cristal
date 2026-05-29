from core import *
import asyncio
import re


admin = app_commands.Group(
    name="admin",
    description="Comandos administrativos da Cristal.",
    default_permissions=discord.Permissions(administrator=True)
)


@admin.command(name="adicionar", description="Adiciona Cristais a um jogador.")
async def admin_adicionar(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if valor <= 0:
        await interaction.response.send_message("❌ O valor precisa ser maior que zero.")
        return

    alterar_saldo(usuario.id, valor)

    await interaction.response.send_message(
        f"✅ Adicionados **{valor:,} {SIGLA}** para {usuario.mention}.",
        
    )

    await enviar_log(
        interaction.guild,
        f"👑 **LOG ADMIN**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Ação: adicionar Cristais\n"
        f"Jogador: {usuario.mention}\n"
        f"Valor: **{valor:,} {SIGLA}**"
    )


@admin.command(name="remover", description="Remove Cristais de um jogador.")
async def admin_remover(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if valor <= 0:
        await interaction.response.send_message("❌ O valor precisa ser maior que zero.")
        return

    saldo_atual = obter_saldo(usuario.id)
    novo_saldo = max(0, saldo_atual - valor)
    definir_saldo(usuario.id, novo_saldo)

    await interaction.response.send_message(
        f"✅ Removidos **{valor:,} {SIGLA}** de {usuario.mention}.",
        
    )

    await enviar_log(
        interaction.guild,
        f"👑 **LOG ADMIN**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Ação: remover Cristais\n"
        f"Jogador: {usuario.mention}\n"
        f"Valor solicitado: **{valor:,} {SIGLA}**\n"
        f"Saldo final: **{novo_saldo:,} {SIGLA}**"
    )


@admin.command(name="definir", description="Define o saldo de um jogador.")
async def admin_definir(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if valor < 0:
        await interaction.response.send_message("❌ O saldo não pode ser negativo.")
        return

    definir_saldo(usuario.id, valor)

    await interaction.response.send_message(
        f"✅ Saldo de {usuario.mention} definido para **{valor:,} {SIGLA}**.",
        
    )

    await enviar_log(
        interaction.guild,
        f"👑 **LOG ADMIN**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Ação: definir saldo\n"
        f"Jogador: {usuario.mention}\n"
        f"Novo saldo: **{valor:,} {SIGLA}**"
    )


@admin.command(name="bilhetes", description="Adiciona ou remove bilhetes de um jogador.")
async def admin_bilhetes(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    alterar_bilhetes(usuario.id, valor)

    await interaction.response.send_message(
        f"✅ Bilhetes de {usuario.mention} alterados em **{valor}**.",
        
    )

    await enviar_log(
        interaction.guild,
        f"👑 **LOG ADMIN**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Ação: alterar bilhetes\n"
        f"Jogador: {usuario.mention}\n"
        f"Alteração: **{valor}**"
    )


@admin.command(name="energia", description="Define a energia de um jogador.")
async def admin_energia(interaction: discord.Interaction, usuario: discord.Member, valor: int):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    valor = max(0, min(ENERGIA_MAXIMA, valor))
    criar_usuario(usuario.id)

    cursor.execute(
        "UPDATE usuarios SET energia = ?, ultima_energia = ? WHERE user_id = ?",
        (valor, int(time.time()), usuario.id)
    )
    conn.commit()

    await interaction.response.send_message(
        f"✅ Energia de {usuario.mention} definida para **{valor}/{ENERGIA_MAXIMA}**.",
        
    )

    await enviar_log(
        interaction.guild,
        f"👑 **LOG ADMIN**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Ação: definir energia\n"
        f"Jogador: {usuario.mention}\n"
        f"Nova energia: **{valor}/{ENERGIA_MAXIMA}**"
    )


# ============================================================
# COMANDOS DE TESTE — REMOVER OU RESTRINGIR ANTES DA VERSÃO OFICIAL
# ============================================================

@admin.command(name="darpet", description="TESTE: dá um pet específico para um jogador.")
async def admin_darpet(
    interaction: discord.Interaction,
    usuario: discord.Member,
    nome: str,
    mutacao: str = "Normal",
    evolucao: str = "Normal"
):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    pet = buscar_pet_base(nome)

    if not pet:
        nomes = ", ".join(p["nome"] for p in PETS[:10])
        await interaction.response.send_message(
            f"❌ Pet não encontrado. Confira o nome exato. Exemplo: {nomes}...",
            
        )
        return

    novo_id = criar_pet_manual(
        usuario.id,
        pet["nome"],
        pet["raridade"],
        pet["linha"],
        pet["emoji"],
        mutacao,
        evolucao
    )

    await interaction.response.send_message(
        f"✅ Pet criado para {usuario.mention}: {pet['emoji']} **{pet['nome']} #{novo_id}**\n"
        f"Raridade: **{pet['raridade']}** | Linha: **{pet['linha']}**\n"
        f"Mutação: **{mutacao}** | Evolução: **{evolucao}**",
        
    )

    await enviar_log(
        interaction.guild,
        f"🧪 **LOG ADMIN — DAR PET**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Jogador: {usuario.mention}\n"
        f"Pet: **{pet['nome']} #{novo_id}**\n"
        f"Mutação: **{mutacao}** | Evolução: **{evolucao}**"
    )


@admin.command(name="profissao", description="TESTE: define a profissão de um jogador sem cooldown.")
@app_commands.choices(tipo=[
    app_commands.Choice(name="nenhuma", value=""),
    app_commands.Choice(name="pesca", value="pesca"),
    app_commands.Choice(name="mineracao", value="mineracao"),
    app_commands.Choice(name="caca", value="caca"),
    app_commands.Choice(name="exploracao", value="exploracao"),
    app_commands.Choice(name="trabalho", value="trabalho"),
])
async def admin_profissao(interaction: discord.Interaction, usuario: discord.Member, tipo: app_commands.Choice[str]):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    criar_usuario(usuario.id)

    if isinstance(usuario, discord.Member):
        cargos_para_remover = []
        for dados in PROFISSOES.values():
            cargo = discord.utils.get(interaction.guild.roles, name=dados["cargo"])
            if cargo and cargo in usuario.roles:
                cargos_para_remover.append(cargo)

        if cargos_para_remover:
            await usuario.remove_roles(*cargos_para_remover, reason="Admin alterou profissão Cristal")

        if tipo.value:
            config = PROFISSOES[tipo.value]
            novo_cargo = discord.utils.get(interaction.guild.roles, name=config["cargo"])
            if novo_cargo:
                await usuario.add_roles(novo_cargo, reason="Admin alterou profissão Cristal")

    cursor.execute(
        "UPDATE usuarios SET profissao = ?, ultima_troca_profissao = 0 WHERE user_id = ?",
        (tipo.value, usuario.id)
    )
    conn.commit()

    nome_profissao = "Nenhuma" if not tipo.value else PROFISSOES[tipo.value]["nome"]

    await interaction.response.send_message(
        f"✅ Profissão de {usuario.mention} definida para **{nome_profissao}** sem cooldown.",
        
    )

    await enviar_log(
        interaction.guild,
        f"🧪 **LOG ADMIN — PROFISSÃO**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Jogador: {usuario.mention}\n"
        f"Profissão: **{nome_profissao}**"
    )


raid_admin_group = app_commands.Group(name="raid", description="Comandos administrativos de raid.")


@raid_admin_group.command(name="iniciar", description="Inicia uma raid manualmente.")
async def admin_raid_iniciar(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.")
        return

    raid_atual = obter_raid_ativa(interaction.guild.id)
    agora = int(time.time())

    if raid_atual and agora < raid_atual[7]:
        await interaction.response.send_message("❌ Já existe uma raid ativa.")
        return

    if raid_atual and agora >= raid_atual[7]:
        await finalizar_raid_por_id(interaction.guild, raid_atual[0])

    boss = escolher_boss_raid()
    inicio = agora
    fim = agora + RAID_DURACAO

    cursor.execute("""
        INSERT INTO raids
        (guild_id, boss_nome, boss_linha, boss_emoji, raridade, mutacao, inicio, fim, ativa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        interaction.guild.id,
        boss["nome"],
        boss["linha"],
        boss["emoji"],
        "Mítico",
        "Corrompido",
        inicio,
        fim
    ))
    conn.commit()

    await interaction.response.send_message(
        f"✅ Raid iniciada em **#{RAID_CANAL}**:\n"
        f"{boss['emoji']} **{boss['nome']} Corrompido** — **Mítico**\n"
        f"Duração: **2 horas**",
        
    )

    canal = canal_por_chave(interaction.guild, "raid")
    mensagem = (
        f"⚠️ **RAID INICIADA!**\n\n"
        f"{boss['emoji']} **{boss['nome']} Corrompido** apareceu!\n"
        f"Raridade: **Mítico**\n"
        f"⏳ Tempo: **2 horas**\n\n"
        f"Use **/raid** para atacar. Cada jogador pode atacar **1 vez**."
    )

    if canal:
        await canal.send(mensagem)
    else:
        await enviar_log(interaction.guild, mensagem)


@raid_admin_group.command(name="finalizar", description="Finaliza a raid ativa e entrega recompensas.")
async def admin_raid_finalizar(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.")
        return

    raid_atual = obter_raid_ativa(interaction.guild.id)

    if not raid_atual:
        await interaction.response.send_message("❌ Não existe raid ativa.")
        return

    texto = await finalizar_raid_por_id(interaction.guild, raid_atual[0])
    await interaction.response.send_message(texto)


admin.add_command(raid_admin_group)


# ============================================================
# COMANDO DE TESTE — REMOVER ANTES DA VERSÃO OFICIAL
# Reseta completamente os dados básicos de um jogador.
# Use apenas para testes da economia.
# ============================================================

@admin.command(name="resetar", description="TESTE: reseta os dados básicos de um jogador.")
@app_commands.describe(
    usuario="Jogador que será resetado.",
    confirmar="Digite CONFIRMAR para resetar."
)
async def admin_resetar(interaction: discord.Interaction, usuario: discord.Member, confirmar: str):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if confirmar != "CONFIRMAR":
        await interaction.response.send_message(
            "⚠️ Para resetar, use novamente e digite **CONFIRMAR** no campo de confirmação.",
            
        )
        return

    criar_usuario(usuario.id)

    cursor.execute("""
        UPDATE usuarios
        SET cristais = 0,
            bilhetes = 0,
            ultimo_diario = 0,
            streak_diario = 0,
            semanas_diario = 0,
            slots_pets = 1,
            energia = ?,
            ultima_energia = ?,
            profissao = '',
            ultima_troca_profissao = 0
        WHERE user_id = ?
    """, (ENERGIA_MAXIMA, int(time.time()), usuario.id))

    cursor.execute("DELETE FROM pets WHERE user_id = ?", (usuario.id,))

    conn.commit()

    await interaction.response.send_message(
        f"🧪 Dados de {usuario.mention} foram resetados.",
        
    )

    await enviar_log(
        interaction.guild,
        f"⚠️ **LOG ADMIN — RESET DE TESTE**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Jogador resetado: {usuario.mention}\n"
        f"Ação: reset completo da V2.3"
    )



# ============================================================
# COMANDOS DE MANUTENÇÃO — IMPORTANTES PARA PRODUÇÃO
# ============================================================

BOT_START_TIME = int(time.time())


def _formatar_tempo(segundos: int) -> str:
    segundos = max(0, int(segundos))
    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, _ = divmod(resto, 60)
    partes = []
    if dias:
        partes.append(f"{dias}d")
    if horas:
        partes.append(f"{horas}h")
    if minutos or not partes:
        partes.append(f"{minutos}min")
    return " ".join(partes)


def _contar_tabela(tabela: str, where: str = "", params: tuple = ()) -> int:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela} {where}", params)
        return cursor.fetchone()[0]
    except Exception:
        return 0


@admin.command(name="save", description="Força o salvamento imediato do banco de dados.")
async def admin_save(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    conn.commit()
    await interaction.response.send_message("✅ Save manual concluído. O banco foi salvo com sucesso.")

    await enviar_log(
        interaction.guild,
        f"💾 **LOG ADMIN — SAVE**\nAdmin: {interaction.user.mention}\nAção: save manual do banco."
    )


@admin.command(name="backup", description="Cria e envia um backup numerado do banco de dados.")
async def admin_backup(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    await interaction.response.defer()
    conn.commit()
    os.makedirs(BASE_BACKUPS_DIR, exist_ok=True)

    maior = 0
    for nome in os.listdir(BASE_BACKUPS_DIR):
        match = re.fullmatch(r"backup(\d+)\.db", nome)
        if match:
            maior = max(maior, int(match.group(1)))

    proximo = maior + 1
    backup_path = os.path.join(BASE_BACKUPS_DIR, f"backup{proximo}.db")
    shutil.copy2(DB_PATH, backup_path)

    await interaction.followup.send(
        f"✅ Backup criado com sucesso: **backup{proximo}.db**\n"
        f"Guarde esse arquivo antes de atualizar ou remover o app.",
        file=discord.File(backup_path)
    )

    await enviar_log(
        interaction.guild,
        f"💾 **LOG ADMIN — BACKUP**\nAdmin: {interaction.user.mention}\nArquivo: `backup{proximo}.db`"
    )


@admin.command(name="status", description="Mostra o status geral do bot e do banco.")
async def admin_status(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    conn.commit()
    uptime = _formatar_tempo(int(time.time()) - BOT_START_TIME)
    usuarios = _contar_tabela("usuarios")
    pets_total = _contar_tabela("pets")
    itens_total = _contar_tabela("inventario_itens", "WHERE quantidade > 0")
    raids_ativas = _contar_tabela("raids", "WHERE ativa = 1")
    eventos_ativos_qtd = _contar_tabela("eventos_ativos", "WHERE ativo = 1 AND fim > ?", (int(time.time()),))

    try:
        tamanho_db = os.path.getsize(DB_PATH) / 1024
        tamanho_txt = f"{tamanho_db:.1f} KB"
    except OSError:
        tamanho_txt = "desconhecido"

    await interaction.response.send_message(
        f"📊 **Status da Cristal**\n\n"
        f"⏱️ Uptime: **{uptime}**\n"
        f"👥 Usuários no banco: **{usuarios}**\n"
        f"🐾 Pets salvos: **{pets_total}**\n"
        f"🎒 Itens registrados: **{itens_total}**\n"
        f"⚔️ Raids ativas: **{raids_ativas}**\n"
        f"✨ Eventos ativos: **{eventos_ativos_qtd}**\n"
        f"💾 Banco: `{DB_PATH}`\n"
        f"📦 Tamanho do banco: **{tamanho_txt}**"
    )


@admin.command(name="giveitem", description="Dá um item da loja/inventário para um jogador.")
async def admin_giveitem(interaction: discord.Interaction, usuario: discord.Member, item_id: int, quantidade: int = 1):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if quantidade <= 0:
        await interaction.response.send_message("❌ A quantidade precisa ser maior que zero.")
        return

    item = item_info(item_id)
    if not item:
        await interaction.response.send_message(f"❌ Item **#{item_id}** não encontrado.")
        return

    adicionar_item(usuario.id, item_id, quantidade)

    await interaction.response.send_message(
        f"✅ {usuario.mention} recebeu **{quantidade}x {item['emoji']} {item['nome']} #{item_id}**."
    )

    await enviar_log(
        interaction.guild,
        f"🧪 **LOG ADMIN — GIVEITEM**\n"
        f"Admin: {interaction.user.mention}\n"
        f"Jogador: {usuario.mention}\n"
        f"Item: **{item['nome']} #{item_id}**\n"
        f"Quantidade: **{quantidade}**"
    )


@admin.command(name="forceraid", description="Inicia uma raid imediatamente.")
async def admin_forceraid(interaction: discord.Interaction):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if interaction.guild is None:
        await interaction.response.send_message("❌ Use em um servidor.")
        return

    raid_atual = obter_raid_ativa(interaction.guild.id)
    agora = int(time.time())

    if raid_atual and agora < raid_atual[7]:
        await interaction.response.send_message("❌ Já existe uma raid ativa.")
        return

    if raid_atual and agora >= raid_atual[7]:
        await finalizar_raid_por_id(interaction.guild, raid_atual[0])

    boss = escolher_boss_raid()
    inicio = agora
    fim = agora + RAID_DURACAO

    cursor.execute("""
        INSERT INTO raids
        (guild_id, boss_nome, boss_linha, boss_emoji, raridade, mutacao, inicio, fim, ativa)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        interaction.guild.id,
        boss["nome"],
        boss["linha"],
        boss["emoji"],
        "Mítico",
        "Corrompido",
        inicio,
        fim
    ))
    conn.commit()

    mensagem = (
        f"⚠️ **RAID INICIADA!**\n\n"
        f"{boss['emoji']} **{boss['nome']} Corrompido** apareceu!\n"
        f"Raridade: **Mítico**\n"
        f"⏳ Tempo: **2 horas**\n\n"
        f"Use **/raid** para atacar. Cada jogador pode atacar **1 vez**."
    )

    canal = canal_por_chave(interaction.guild, "raid")
    if canal:
        await canal.send(mensagem)

    await interaction.response.send_message(
        f"✅ Raid forçada iniciada com sucesso. Boss: {boss['emoji']} **{boss['nome']} Corrompido**."
    )

    await enviar_log(
        interaction.guild,
        f"⚔️ **LOG ADMIN — FORCERAID**\nAdmin: {interaction.user.mention}\nBoss: **{boss['nome']} Corrompido**"
    )


@admin.command(name="fixuser", description="Corrige dados quebrados de um jogador.")
async def admin_fixuser(interaction: discord.Interaction, usuario: discord.Member):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    criar_usuario(usuario.id)
    correcoes = []

    # Corrige campos básicos do usuário.
    cursor.execute("""
        SELECT cristais, bilhetes, slots_pets, energia, profissao, xpshare_pet_id
        FROM usuarios
        WHERE user_id = ?
    """, (usuario.id,))
    row = cursor.fetchone()

    if row:
        cristais, bilhetes, slots_pets, energia, profissao, xpshare_pet_id = row

        novo_cristais = max(0, cristais or 0)
        novo_bilhetes = max(0, bilhetes or 0)
        novo_slots = max(1, slots_pets or 1)
        nova_energia = max(0, min(ENERGIA_MAXIMA, energia if energia is not None else ENERGIA_MAXIMA))
        nova_profissao = profissao if profissao in PROFISSOES or profissao == "" else ""

        if novo_cristais != cristais:
            correcoes.append("saldo negativo corrigido")
        if novo_bilhetes != bilhetes:
            correcoes.append("bilhetes negativos corrigidos")
        if novo_slots != slots_pets:
            correcoes.append("slots inválidos corrigidos")
        if nova_energia != energia:
            correcoes.append("energia inválida corrigida")
        if nova_profissao != profissao:
            correcoes.append("profissão inválida removida")

        # XP Share precisa apontar para pet do próprio jogador.
        novo_xpshare = xpshare_pet_id or 0
        if novo_xpshare:
            cursor.execute("SELECT 1 FROM pets WHERE user_id = ? AND pet_id = ?", (usuario.id, novo_xpshare))
            if not cursor.fetchone():
                novo_xpshare = 0
                correcoes.append("XP Share inválido removido")

        cursor.execute("""
            UPDATE usuarios
            SET cristais = ?, bilhetes = ?, slots_pets = ?, energia = ?, profissao = ?, xpshare_pet_id = ?
            WHERE user_id = ?
        """, (novo_cristais, novo_bilhetes, novo_slots, nova_energia, nova_profissao, novo_xpshare, usuario.id))

    # Corrige pets com nível/XP inválidos.
    cursor.execute("""
        UPDATE pets
        SET nivel = CASE
                WHEN nivel < 1 THEN 1
                WHEN nivel > ? THEN ?
                ELSE nivel
            END,
            xp = CASE WHEN xp < 0 THEN 0 ELSE xp END,
            trancado = CASE WHEN trancado NOT IN (0, 1) THEN 0 ELSE trancado END,
            equipado = CASE WHEN equipado NOT IN (0, 1) THEN 0 ELSE equipado END,
            favoritado = CASE WHEN favoritado NOT IN (0, 1) THEN 0 ELSE favoritado END
        WHERE user_id = ?
    """, (NIVEL_MAXIMO_PET, NIVEL_MAXIMO_PET, usuario.id))
    if cursor.rowcount:
        correcoes.append("pets validados")

    # Remove itens com quantidade inválida.
    cursor.execute("DELETE FROM inventario_itens WHERE user_id = ? AND quantidade <= 0", (usuario.id,))
    if cursor.rowcount:
        correcoes.append("itens inválidos removidos")

    # Remove excesso de pets equipados acima do limite atual.
    slots_totais = obter_slots_totais(usuario)
    cursor.execute("""
        SELECT pet_id
        FROM pets
        WHERE user_id = ? AND equipado = 1
        ORDER BY
            CASE raridade
                WHEN 'Mítico' THEN 5
                WHEN 'Lendário' THEN 4
                WHEN 'Épico' THEN 3
                WHEN 'Raro' THEN 2
                ELSE 1
            END DESC,
            nivel DESC,
            pet_id DESC
    """, (usuario.id,))
    equipados = [linha[0] for linha in cursor.fetchall()]

    if len(equipados) > slots_totais:
        manter = set(equipados[:slots_totais])
        remover = [pet_id for pet_id in equipados if pet_id not in manter]
        cursor.executemany(
            "UPDATE pets SET equipado = 0 WHERE user_id = ? AND pet_id = ?",
            [(usuario.id, pet_id) for pet_id in remover]
        )
        correcoes.append(f"{len(remover)} pet(s) desequipado(s) por excesso de slots")

    conn.commit()

    if not correcoes:
        texto = f"✅ Nenhum problema encontrado em {usuario.mention}."
    else:
        texto = f"✅ Correções aplicadas em {usuario.mention}:\n" + "\n".join(f"• {c}" for c in correcoes)

    await interaction.response.send_message(texto)

    await enviar_log(
        interaction.guild,
        f"🛠️ **LOG ADMIN — FIXUSER**\nAdmin: {interaction.user.mention}\nJogador: {usuario.mention}\nResultado:\n" + ("\n".join(correcoes) if correcoes else "Nenhuma correção necessária.")
    )


@admin.command(name="manutencao", description="Liga ou desliga o modo manutenção da Cristal.")
@app_commands.choices(estado=[
    app_commands.Choice(name="on", value="on"),
    app_commands.Choice(name="off", value="off"),
])
async def admin_manutencao(interaction: discord.Interaction, estado: app_commands.Choice[str]):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    ativo = estado.value == "on"
    definir_modo_manutencao(ativo)

    if ativo:
        await interaction.response.send_message(
            "🛠️ **Modo manutenção ativado.** Comandos comuns ficarão bloqueados até ser desativado."
        )
    else:
        await interaction.response.send_message(
            "✅ **Modo manutenção desativado.** A Cristal voltou ao funcionamento normal."
        )

    await enviar_log(
        interaction.guild,
        f"🛠️ **LOG ADMIN — MANUTENÇÃO**\nAdmin: {interaction.user.mention}\nEstado: **{'ON' if ativo else 'OFF'}**"
    )


@admin.command(name="importarbackup", description="Importa um cristal.db enviado e encerra o bot para reinício seguro.")
@app_commands.describe(
    arquivo="Envie o arquivo renomeado exatamente como cristal.db.",
    confirmar="Digite CONFIRMAR para substituir o banco atual."
)
async def admin_importarbackup(interaction: discord.Interaction, arquivo: discord.Attachment, confirmar: str):
    if not tem_permissao_admin(interaction):
        await interaction.response.send_message("❌ Você não tem permissão.")
        return

    if confirmar != "CONFIRMAR":
        await interaction.response.send_message(
            "⚠️ Para importar backup, use novamente e digite **CONFIRMAR** no campo de confirmação."
        )
        return

    if arquivo.filename != "cristal.db":
        await interaction.response.send_message(
            "❌ O arquivo precisa se chamar exatamente **cristal.db**.\n"
            "Renomeie o backup antes de enviar."
        )
        return

    await interaction.response.defer()
    definir_modo_manutencao(True)
    os.makedirs(BASE_BACKUPS_DIR, exist_ok=True)
    os.makedirs(BASE_DADOS_DIR, exist_ok=True)

    temp_path = os.path.join(BASE_BACKUPS_DIR, "_importando_cristal.db")

    try:
        await arquivo.save(temp_path)

        # Verificação básica de SQLite: evita substituir o banco por arquivo errado.
        with open(temp_path, "rb") as f:
            assinatura = f.read(16)

        if assinatura != b"SQLite format 3\x00":
            definir_modo_manutencao(False)
            try:
                os.remove(temp_path)
            except OSError:
                pass
            await interaction.followup.send("❌ Esse arquivo não parece ser um banco SQLite válido.")
            return

        conn.commit()

        agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_atual = os.path.join(BASE_BACKUPS_DIR, f"antes_importar_{agora}.db")
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, backup_atual)

        # Fecha o SQLite antes de substituir o arquivo.
        conn.close()
        shutil.copy2(temp_path, DB_PATH)

        await interaction.followup.send(
            "✅ **Backup importado com sucesso.**\n"
            "🛠️ A Cristal entrou em manutenção e será encerrada agora para proteger o banco.\n"
            "Depois disso, clique em **Start** na Discloud para iniciar novamente."
        )

        await asyncio.sleep(2)
        os._exit(0)

    except Exception as erro:
        definir_modo_manutencao(False)
        try:
            conn.rollback()
        except Exception:
            pass
        await interaction.followup.send(f"❌ Falha ao importar backup: `{erro}`")



bot.tree.add_command(admin)
