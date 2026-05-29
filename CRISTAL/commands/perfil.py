from core import *

# ============================================================
# PERFIL, TÍTULOS E CONQUISTAS
# Conquistas são cosméticas: não dão bônus de poder.
# ============================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS conquistas_usuario (
    user_id INTEGER NOT NULL,
    conquista_id TEXT NOT NULL,
    desbloqueado_em INTEGER NOT NULL,
    PRIMARY KEY (user_id, conquista_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS perfil_usuario (
    user_id INTEGER PRIMARY KEY,
    titulo TEXT DEFAULT ''
)
""")

conn.commit()


CONQUISTAS = [
    {
        "id": "primeiros_cristais",
        "nome": "Primeiros Cristais",
        "descricao": "Tenha pelo menos 1.000 CS.",
        "titulo": "Iniciante de Cristal",
        "emoji": "💎",
        "categoria": "Economia",
    },
    {
        "id": "rico",
        "nome": "Rico",
        "descricao": "Tenha pelo menos 100.000 CS.",
        "titulo": "Rico",
        "emoji": "💰",
        "categoria": "Economia",
    },
    {
        "id": "milionario",
        "nome": "Milionário",
        "descricao": "Tenha pelo menos 1.000.000 CS.",
        "titulo": "Milionário de Cristal",
        "emoji": "👑",
        "categoria": "Economia",
    },
    {
        "id": "primeiro_pet",
        "nome": "Primeiro Companheiro",
        "descricao": "Tenha pelo menos 1 pet.",
        "titulo": "Treinador Iniciante",
        "emoji": "🐾",
        "categoria": "Pets",
    },
    {
        "id": "colecionador",
        "nome": "Colecionador",
        "descricao": "Tenha pelo menos 25 pets.",
        "titulo": "Colecionador",
        "emoji": "📦",
        "categoria": "Pets",
    },
    {
        "id": "lendario",
        "nome": "Toque Lendário",
        "descricao": "Tenha pelo menos 1 pet Lendário.",
        "titulo": "Domador Lendário",
        "emoji": "🟡",
        "categoria": "Pets",
    },
    {
        "id": "mitico",
        "nome": "Sorte Mítica",
        "descricao": "Tenha pelo menos 1 pet Mítico.",
        "titulo": "Domador Mítico",
        "emoji": "🔴",
        "categoria": "Pets",
    },
    {
        "id": "shiny",
        "nome": "Brilho Raro",
        "descricao": "Tenha pelo menos 1 pet Shiny.",
        "titulo": "Caçador de Shiny",
        "emoji": "✨",
        "categoria": "Pets",
    },
    {
        "id": "podre",
        "nome": "Azar de Luxo",
        "descricao": "Tenha pelo menos 1 pet Podre.",
        "titulo": "Sobrevivente do Azar",
        "emoji": "🧪",
        "categoria": "Pets",
    },
    {
        "id": "fusao_bronze",
        "nome": "Primeira Fusão",
        "descricao": "Tenha pelo menos 1 pet Bronze ou melhor.",
        "titulo": "Ferreiro de Pets",
        "emoji": "🥉",
        "categoria": "Pets",
    },
    {
        "id": "profissional",
        "nome": "Profissional",
        "descricao": "Escolha uma profissão.",
        "titulo": "Trabalhador da Cristal",
        "emoji": "💼",
        "categoria": "Profissões",
    },
    {
        "id": "raider",
        "nome": "Primeira Raid",
        "descricao": "Participe de pelo menos 1 raid.",
        "titulo": "Raider Iniciante",
        "emoji": "⚔️",
        "categoria": "Raid",
    },
    {
        "id": "dano_raid",
        "nome": "Golpe Pesado",
        "descricao": "Cause pelo menos 10.000 de dano total em raids.",
        "titulo": "Golpe Pesado",
        "emoji": "🐉",
        "categoria": "Raid",
    },
    {
        "id": "xpshare",
        "nome": "Treinador Estratégico",
        "descricao": "Tenha o item XP Share.",
        "titulo": "Treinador Estratégico",
        "emoji": "📘",
        "categoria": "Loja",
    },
    {
        "id": "acessorio",
        "nome": "Bem Equipado",
        "descricao": "Tenha pelo menos 1 acessório.",
        "titulo": "Bem Equipado",
        "emoji": "🧰",
        "categoria": "Loja",
    },
    {
        "id": "tesouro",
        "nome": "Achado Raro",
        "descricao": "Tenha pelo menos 1 tesouro no inventário.",
        "titulo": "Caçador de Tesouros",
        "emoji": "🏺",
        "categoria": "Drops",
    },
]


def obter_conquistas_desbloqueadas(user_id: int):
    cursor.execute(
        "SELECT conquista_id FROM conquistas_usuario WHERE user_id = ?",
        (user_id,),
    )
    return {linha[0] for linha in cursor.fetchall()}


def obter_titulo_atual(user_id: int):
    cursor.execute("SELECT titulo FROM perfil_usuario WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row and row[0] else ""


def definir_titulo(user_id: int, titulo: str):
    cursor.execute(
        "INSERT OR IGNORE INTO perfil_usuario (user_id, titulo) VALUES (?, '')",
        (user_id,),
    )
    cursor.execute(
        "UPDATE perfil_usuario SET titulo = ? WHERE user_id = ?",
        (titulo, user_id),
    )
    conn.commit()


def contar_pets_raridade(user_id: int, raridade: str):
    cursor.execute(
        "SELECT COUNT(*) FROM pets WHERE user_id = ? AND raridade = ?",
        (user_id, raridade),
    )
    return cursor.fetchone()[0]


def contar_pets_mutacao(user_id: int, mutacao: str):
    cursor.execute(
        "SELECT COUNT(*) FROM pets WHERE user_id = ? AND mutacao LIKE ?",
        (user_id, f"%{mutacao}%"),
    )
    return cursor.fetchone()[0]


def tem_fusao(user_id: int):
    cursor.execute(
        """
        SELECT COUNT(*) FROM pets
        WHERE user_id = ? AND evolucao != 'Normal'
        """,
        (user_id,),
    )
    return cursor.fetchone()[0] > 0


def raid_info(user_id: int):
    cursor.execute(
        "SELECT COUNT(*), COALESCE(SUM(dano), 0) FROM raid_participantes WHERE user_id = ?",
        (user_id,),
    )
    return cursor.fetchone()


def tem_item(user_id: int, item_id: int):
    cursor.execute(
        "SELECT quantidade FROM inventario_itens WHERE user_id = ? AND item_id = ?",
        (user_id, item_id),
    )
    row = cursor.fetchone()
    return bool(row and row[0] > 0)


def tem_algum_item(user_id: int, ids: list[int]):
    if not ids:
        return False
    placeholders = ",".join("?" for _ in ids)
    cursor.execute(
        f"""
        SELECT COUNT(*) FROM inventario_itens
        WHERE user_id = ? AND item_id IN ({placeholders}) AND quantidade > 0
        """,
        [user_id] + ids,
    )
    return cursor.fetchone()[0] > 0


def conquista_cumprida(user_id: int, conquista_id: str):
    saldo = obter_saldo(user_id)
    total_pets = contar_pets(user_id)
    profissao_atual, _ = obter_profissao(user_id)
    raids, dano_total = raid_info(user_id)

    if conquista_id == "primeiros_cristais":
        return saldo >= 1_000
    if conquista_id == "rico":
        return saldo >= 100_000
    if conquista_id == "milionario":
        return saldo >= 1_000_000
    if conquista_id == "primeiro_pet":
        return total_pets >= 1
    if conquista_id == "colecionador":
        return total_pets >= 25
    if conquista_id == "lendario":
        return contar_pets_raridade(user_id, "Lendário") >= 1
    if conquista_id == "mitico":
        return contar_pets_raridade(user_id, "Mítico") >= 1
    if conquista_id == "shiny":
        return contar_pets_mutacao(user_id, "Shiny") >= 1
    if conquista_id == "podre":
        return contar_pets_mutacao(user_id, "Podre") >= 1
    if conquista_id == "fusao_bronze":
        return tem_fusao(user_id)
    if conquista_id == "profissional":
        return bool(profissao_atual)
    if conquista_id == "raider":
        return raids >= 1
    if conquista_id == "dano_raid":
        return dano_total >= 10_000
    if conquista_id == "xpshare":
        return tem_item(user_id, 1)
    if conquista_id == "acessorio":
        return tem_algum_item(user_id, [10, 11, 12, 13, 14])
    if conquista_id == "tesouro":
        return tem_algum_item(user_id, [100, 101, 102, 103, 104])

    return False


def atualizar_conquistas(user_id: int):
    criar_usuario(user_id)
    desbloqueadas = obter_conquistas_desbloqueadas(user_id)
    novas = []
    agora = int(time.time())

    for conquista in CONQUISTAS:
        if conquista["id"] in desbloqueadas:
            continue
        if conquista_cumprida(user_id, conquista["id"]):
            cursor.execute(
                """
                INSERT OR IGNORE INTO conquistas_usuario
                (user_id, conquista_id, desbloqueado_em)
                VALUES (?, ?, ?)
                """,
                (user_id, conquista["id"], agora),
            )
            novas.append(conquista)

    conn.commit()
    return novas


def titulos_desbloqueados(user_id: int):
    atualizar_conquistas(user_id)
    desbloqueadas = obter_conquistas_desbloqueadas(user_id)
    titulos = []

    for conquista in CONQUISTAS:
        titulo = conquista.get("titulo")
        if titulo and conquista["id"] in desbloqueadas:
            titulos.append(titulo)

    return titulos


class ConquistasView(discord.ui.View):
    def __init__(self, user_id: int, paginas: list[str]):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.paginas = paginas
        self.pagina = 0
        self.atualizar_botoes()

    def atualizar_botoes(self):
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= len(self.paginas) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa lista não é sua.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Anterior", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina > 0:
            self.pagina -= 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.paginas[self.pagina], view=self)

    @discord.ui.button(label="Próxima", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def proxima(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina < len(self.paginas) - 1:
            self.pagina += 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.paginas[self.pagina], view=self)


def montar_paginas_conquistas(user_id: int):
    atualizar_conquistas(user_id)
    desbloqueadas = obter_conquistas_desbloqueadas(user_id)
    por_pagina = 6
    paginas = []

    for inicio in range(0, len(CONQUISTAS), por_pagina):
        parte = CONQUISTAS[inicio:inicio + por_pagina]
        numero = len(paginas) + 1
        total = max(1, (len(CONQUISTAS) + por_pagina - 1) // por_pagina)
        texto = f"🏆 **Conquistas** — Página **{numero}/{total}**\n"
        texto += f"Desbloqueadas: **{len(desbloqueadas)}/{len(CONQUISTAS)}**\n\n"

        for conquista in parte:
            ok = conquista["id"] in desbloqueadas
            status = "✅" if ok else "🔒"
            titulo = conquista.get("titulo", "")
            titulo_txt = f"\nTítulo: **{titulo}**" if titulo else ""
            texto += (
                f"{status} {conquista['emoji']} **{conquista['nome']}**\n"
                f"Categoria: **{conquista['categoria']}**\n"
                f"{conquista['descricao']}"
                f"{titulo_txt}\n\n"
            )

        paginas.append(texto)

    return paginas


@bot.tree.command(name="perfil", description="Mostra seu perfil ou o perfil de outro jogador.")
async def perfil(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    atualizar_conquistas(usuario.id)

    cristais, bilhetes, _, streak, semanas, slots_base, energia = obter_dados(usuario.id)
    total_pets = contar_pets(usuario.id)
    titulo = obter_titulo_atual(usuario.id)
    profissao_atual, _ = obter_profissao(usuario.id)
    raids, dano_total = raid_info(usuario.id)
    desbloqueadas = obter_conquistas_desbloqueadas(usuario.id)

    profissao_nome = "Nenhuma"
    if profissao_atual and profissao_atual in PROFISSOES:
        profissao_nome = PROFISSOES[profissao_atual]["nome"]

    titulo_linha = f"\nTítulo: **{titulo}**" if titulo else "\nTítulo: **Nenhum**"

    await interaction.response.send_message(
        f"👤 **Perfil de {usuario.display_name}**"
        f"{titulo_linha}\n\n"
        f"💎 Cristais: **{cristais:,} {SIGLA}**\n"
        f"🎟️ Bilhetes: **{bilhetes}**\n"
        f"⚡ Energia: **{energia}/{ENERGIA_MAXIMA}**\n"
        f"💼 Profissão: **{profissao_nome}**\n"
        f"🔥 Sequência diária: **{streak} dia(s)**\n"
        f"📅 Semanas seguidas: **{semanas}**\n"
        f"🐾 Pets: **{total_pets}**\n"
        f"📌 Slots base: **{slots_base}**\n"
        f"⚔️ Raids: **{raids}**\n"
        f"🐉 Dano total em raids: **{dano_total:,}**\n"
        f"🏆 Conquistas: **{len(desbloqueadas)}/{len(CONQUISTAS)}**",
        ephemeral=True,
    )


@bot.tree.command(name="conquistas", description="Mostra suas conquistas.")
async def conquistas(interaction: discord.Interaction):
    paginas = montar_paginas_conquistas(interaction.user.id)
    view = ConquistasView(interaction.user.id, paginas)
    await interaction.response.send_message(paginas[0], view=view, ephemeral=True)


titulo_group = app_commands.Group(name="titulo", description="Comandos de títulos cosméticos.")


@titulo_group.command(name="usar", description="Usa um título desbloqueado.")
async def titulo_usar(interaction: discord.Interaction, titulo: str):
    disponiveis = titulos_desbloqueados(interaction.user.id)
    titulo_limpo = titulo.strip()

    escolhido = None
    for item in disponiveis:
        if item.lower() == titulo_limpo.lower():
            escolhido = item
            break

    if not escolhido:
        await interaction.response.send_message(
            "❌ Você não possui esse título. Use `/titulo meus` para ver seus títulos.",
            ephemeral=True,
        )
        return

    definir_titulo(interaction.user.id, escolhido)
    await interaction.response.send_message(f"✅ Título equipado: **{escolhido}**.", ephemeral=True)


@titulo_group.command(name="remover", description="Remove seu título atual.")
async def titulo_remover(interaction: discord.Interaction):
    definir_titulo(interaction.user.id, "")
    await interaction.response.send_message("✅ Título removido.", ephemeral=True)


@titulo_group.command(name="meus", description="Mostra seus títulos desbloqueados.")
async def titulo_meus(interaction: discord.Interaction):
    disponiveis = titulos_desbloqueados(interaction.user.id)

    if not disponiveis:
        await interaction.response.send_message("Você ainda não desbloqueou títulos.", ephemeral=True)
        return

    texto = "🏷️ **Seus títulos**\n\n"
    for titulo in disponiveis:
        texto += f"• {titulo}\n"
    texto += "\nUse `/titulo usar titulo:<nome>` para equipar."

    await interaction.response.send_message(texto, ephemeral=True)


bot.tree.add_command(titulo_group)
