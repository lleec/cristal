from core import *

class PetsPaginadosView(discord.ui.View):
    def __init__(self, user_id: int, resultados: list, por_pagina: int = 10, dono_nome: str = "Seus pets"):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.resultados = resultados
        self.por_pagina = por_pagina
        self.pagina = 0
        self.dono_nome = dono_nome
        self.atualizar_botoes()

    def total_paginas(self):
        return max(1, (len(self.resultados) + self.por_pagina - 1) // self.por_pagina)

    def atualizar_botoes(self):
        total = self.total_paginas()
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= total - 1

    def gerar_texto(self):
        total = self.total_paginas()
        inicio = self.pagina * self.por_pagina
        fim = inicio + self.por_pagina
        pets_pagina = self.resultados[inicio:fim]

        texto = (
            f"🐾 **{self.dono_nome}** — Página **{self.pagina + 1}/{total}**\n"
            f"Mostrando **{inicio + 1}-{min(fim, len(self.resultados))}** de **{len(self.resultados)}** pet(s).\n\n"
        )

        for pet_id, nome, raridade, linha, emoji, mutacao, trancado, equipado, favoritado, evolucao in pets_pagina:
            cadeado = "🔒 " if trancado else ""
            ativo = "✅ " if equipado else ""
            favorito = "⭐ " if favoritado else ""
            mutacao_txt = "" if mutacao == "Normal" else f" | {mutacao}"
            evolucao_txt = "" if evolucao == "Normal" else f" | {evolucao}"
            texto += f"{ativo}{cadeado}{favorito}{emoji} **{nome} #{pet_id}** — {raridade} | {linha}{evolucao_txt}{mutacao_txt}\n"

        texto += "\nUse `/pet info id` para detalhes."
        return texto

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Só quem abriu essa lista pode usar esses botões.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Anterior", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina > 0:
            self.pagina -= 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.gerar_texto(), view=self)

    @discord.ui.button(label="Próxima", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def proxima(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina < self.total_paginas() - 1:
            self.pagina += 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.gerar_texto(), view=self)


@bot.tree.command(name="pets", description="Mostra seus pets ou os pets de outro jogador.")
async def pets(interaction: discord.Interaction, usuario: discord.Member = None):
    alvo = usuario or interaction.user

    cursor.execute("""
        SELECT pet_id, nome, raridade, linha, emoji, mutacao, trancado, equipado, favoritado, evolucao
        FROM pets
        WHERE user_id = ?
        ORDER BY
            favoritado DESC,
            equipado DESC,
            CASE raridade
                WHEN 'Mítico' THEN 5
                WHEN 'Lendário' THEN 4
                WHEN 'Épico' THEN 3
                WHEN 'Raro' THEN 2
                ELSE 1
            END DESC,
            pet_id DESC
    """, (alvo.id,))

    resultados = cursor.fetchall()

    if not resultados:
        if alvo.id == interaction.user.id:
            mensagem = "🐾 Você ainda não tem pets. Use `/gc`, `/gm` ou `/gp` para abrir gachas."
        else:
            mensagem = f"🐾 **{alvo.display_name}** ainda não tem pets."

        await interaction.response.send_message(mensagem, ephemeral=True)
        return

    titulo = "Seus pets" if alvo.id == interaction.user.id else f"Pets de {alvo.display_name}"
    view = PetsPaginadosView(interaction.user.id, resultados, dono_nome=titulo)

    await interaction.response.send_message(
        view.gerar_texto(),
        view=view,
        ephemeral=True
    )


@bot.tree.command(name="gc", description="Abre o Gacha Normal.")
async def gc(interaction: discord.Interaction):
    await iniciar_gacha(interaction, "normal")


@bot.tree.command(name="gm", description="Abre o Gacha Melhor.")
async def gm(interaction: discord.Interaction):
    await iniciar_gacha(interaction, "melhor")


@bot.tree.command(name="gp", description="Abre o Gacha Premium.")
async def gp(interaction: discord.Interaction):
    await iniciar_gacha(interaction, "premium")


@bot.tree.command(name="gacha", description="Abre um gacha.")
@app_commands.choices(tipo=[
    app_commands.Choice(name="normal", value="normal"),
    app_commands.Choice(name="melhor", value="melhor"),
    app_commands.Choice(name="premium", value="premium"),
])
async def gacha(interaction: discord.Interaction, tipo: app_commands.Choice[str]):
    await iniciar_gacha(interaction, tipo.value)


pet_group = app_commands.Group(name="pet", description="Comandos de pets.")


@pet_group.command(name="info", description="Mostra informações de um pet.")
async def pet_info(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado no seu inventário.", ephemeral=True)
        return

    pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em = pet

    await interaction.response.send_message(
        f"{emoji} **{nome} #{pet_id}**\n"
        f"Raridade: **{raridade}**\n"
        f"Linha: **{linha}**\n"
        f"Mutação: **{mutacao}**\n"
        f"Evolução/Fusão: **{evolucao}**\n"
        f"Nível: **{nivel}/{NIVEL_MAXIMO_PET}**\n"
        f"XP: **{xp}/{xp_necessario(nivel) if nivel < NIVEL_MAXIMO_PET else 0}**\n"
        f"Trancado: **{'Sim' if trancado else 'Não'}**\n"
        f"Equipado: **{'Sim' if equipado else 'Não'}**",
        ephemeral=True
    )


@pet_group.command(name="ver", description="Mostra informações de um pet de outro jogador.")
async def pet_ver(interaction: discord.Interaction, usuario: discord.Member, id: int):
    pet = obter_pet(usuario.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado no inventário desse jogador.", ephemeral=True)
        return

    pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em = pet

    await interaction.response.send_message(
        f"{emoji} **{nome} #{pet_id}** de **{usuario.display_name}**\n"
        f"Raridade: **{raridade}**\n"
        f"Linha: **{linha}**\n"
        f"Mutação: **{mutacao}**\n"
        f"Evolução/Fusão: **{evolucao}**\n"
        f"Nível: **{nivel}/{NIVEL_MAXIMO_PET}**\n"
        f"XP: **{xp}/{xp_necessario(nivel) if nivel < NIVEL_MAXIMO_PET else 0}**\n"
        f"Trancado: **{'Sim' if trancado else 'Não'}**\n"
        f"Equipado: **{'Sim' if equipado else 'Não'}**",
        ephemeral=True
    )


@pet_group.command(name="trancar", description="Tranca um pet para evitar venda/fusão/doação.")
async def pet_trancar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    cursor.execute(
        "UPDATE pets SET trancado = 1 WHERE user_id = ? AND pet_id = ?",
        (interaction.user.id, id)
    )
    conn.commit()

    await interaction.response.send_message(f"🔒 Pet **#{id}** trancado.", ephemeral=True)


@pet_group.command(name="destrancar", description="Destranca um pet.")
async def pet_destrancar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    cursor.execute(
        "UPDATE pets SET trancado = 0 WHERE user_id = ? AND pet_id = ?",
        (interaction.user.id, id)
    )
    conn.commit()

    await interaction.response.send_message(f"🔓 Pet **#{id}** destrancado.", ephemeral=True)


@pet_group.command(name="equipar", description="Equipa um pet em um slot disponível.")
async def pet_equipar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em = pet

    if equipado:
        await interaction.response.send_message("❌ Esse pet já está equipado.", ephemeral=True)
        return

    criar_usuario(interaction.user.id)
    slots = obter_slots_totais(interaction.user)

    cursor.execute("SELECT COUNT(*) FROM pets WHERE user_id = ? AND equipado = 1", (interaction.user.id,))
    equipados = cursor.fetchone()[0]

    if equipados >= slots:
        await interaction.response.send_message(
            f"❌ Você não tem slots livres. Slots usados: **{equipados}/{slots}**.",
            ephemeral=True
        )
        return

    cursor.execute("UPDATE pets SET equipado = 1 WHERE user_id = ? AND pet_id = ?", (interaction.user.id, id))
    conn.commit()
    if raridade == "Lendário":
        registrar_missao_evento(interaction.user.id, "equip_lendario", 1)
    if raridade == "Mítico":
        registrar_missao_evento(interaction.user.id, "equip_mitico", 1)

    await interaction.response.send_message(f"✅ Você equipou **{nome} #{id}**.", ephemeral=True)


@pet_group.command(name="desequipar", description="Desequipa um pet.")
async def pet_desequipar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    cursor.execute("UPDATE pets SET equipado = 0 WHERE user_id = ? AND pet_id = ?", (interaction.user.id, id))
    conn.commit()

    await interaction.response.send_message(f"✅ Pet **#{id}** desequipado.", ephemeral=True)


@pet_group.command(name="ativos", description="Mostra seus pets equipados.")
async def pet_ativos(interaction: discord.Interaction):
    cursor.execute("""
        SELECT pet_id, nome, raridade, linha, emoji, mutacao, evolucao
        FROM pets
        WHERE user_id = ? AND equipado = 1
        ORDER BY pet_id DESC
    """, (interaction.user.id,))
    resultados = cursor.fetchall()

    if not resultados:
        await interaction.response.send_message("🐾 Você não tem pets equipados.", ephemeral=True)
        return

    texto = "✅ **Pets equipados**\n\n"
    for pet_id, nome, raridade, linha, emoji, mutacao, evolucao in resultados:
        mutacao_txt = "" if mutacao == "Normal" else f" | {mutacao}"
        evolucao_txt = "" if evolucao == "Normal" else f" | {evolucao}"
        texto += f"{emoji} **{nome} #{pet_id}** — {raridade} | {linha}{evolucao_txt}{mutacao_txt}\n"

    await interaction.response.send_message(texto, ephemeral=True)


@pet_group.command(name="favoritar", description="Marca um pet como favorito.")
async def pet_favoritar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    cursor.execute("UPDATE pets SET favoritado = 1 WHERE user_id = ? AND pet_id = ?", (interaction.user.id, id))
    conn.commit()

    await interaction.response.send_message(f"⭐ Pet **#{id}** favoritado.", ephemeral=True)


@pet_group.command(name="desfavoritar", description="Remove um pet dos favoritos.")
async def pet_desfavoritar(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    cursor.execute("UPDATE pets SET favoritado = 0 WHERE user_id = ? AND pet_id = ?", (interaction.user.id, id))
    conn.commit()

    await interaction.response.send_message(f"⭐ Pet **#{id}** removido dos favoritos.", ephemeral=True)


@pet_group.command(name="vender", description="Vende um pet não trancado.")
async def pet_vender(interaction: discord.Interaction, id: int):
    pet = obter_pet(interaction.user.id, id)

    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado.", ephemeral=True)
        return

    pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em = pet

    if trancado:
        await interaction.response.send_message("❌ Esse pet está trancado.", ephemeral=True)
        return

    if equipado:
        await interaction.response.send_message("❌ Esse pet está equipado. Desequipe antes de vender.", ephemeral=True)
        return

    valor = VALOR_VENDA[raridade]

    cursor.execute(
        "DELETE FROM pets WHERE user_id = ? AND pet_id = ?",
        (interaction.user.id, id)
    )
    conn.commit()

    alterar_saldo(interaction.user.id, valor)

    await interaction.response.send_message(
        f"💰 Você vendeu **{nome} #{id}** por **{valor:,} {SIGLA}**.",
        ephemeral=True
    )

class ConfirmarVendaTodosView(discord.ui.View):
    def __init__(self, user_id: int, raridade: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.raridade = raridade
        self.usado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa confirmação não é sua.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirmar venda", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Essa venda já foi processada.", ephemeral=True)
            return

        self.usado = True
        cursor.execute("""
            SELECT pet_id
            FROM pets
            WHERE user_id = ? AND raridade = ? AND trancado = 0 AND equipado = 0
        """, (self.user_id, self.raridade))
        pets_para_vender = [linha[0] for linha in cursor.fetchall()]

        if not pets_para_vender:
            await interaction.response.edit_message(content="❌ Nenhum pet válido encontrado para vender.", view=None)
            return

        quantidade = len(pets_para_vender)
        valor_total = quantidade * VALOR_VENDA[self.raridade]

        cursor.executemany(
            "DELETE FROM pets WHERE user_id = ? AND pet_id = ?",
            [(self.user_id, pet_id) for pet_id in pets_para_vender]
        )
        conn.commit()
        alterar_saldo(self.user_id, valor_total)

        await interaction.response.edit_message(
            content=f"💰 Você vendeu **{quantidade} pet(s) {self.raridade}** por **{valor_total:,} {SIGLA}**.",
            view=None
        )

    @discord.ui.button(label="Cancelar", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.usado = True
        await interaction.response.edit_message(content="❌ Venda cancelada.", view=None)


@pet_group.command(name="vender-todos", description="Vende todos os pets de uma raridade, exceto trancados/equipados.")
@app_commands.choices(raridade=[
    app_commands.Choice(name="Comum", value="Comum"),
    app_commands.Choice(name="Raro", value="Raro"),
    app_commands.Choice(name="Épico", value="Épico"),
    app_commands.Choice(name="Lendário", value="Lendário"),
    app_commands.Choice(name="Mítico", value="Mítico"),
])
async def pet_vender_todos(interaction: discord.Interaction, raridade: app_commands.Choice[str]):
    cursor.execute("""
        SELECT COUNT(*)
        FROM pets
        WHERE user_id = ? AND raridade = ? AND trancado = 0 AND equipado = 0
    """, (interaction.user.id, raridade.value))
    quantidade = cursor.fetchone()[0]

    if quantidade <= 0:
        await interaction.response.send_message(
            f"❌ Você não tem pets **{raridade.value}** disponíveis para venda.",
            ephemeral=True
        )
        return

    valor_total = quantidade * VALOR_VENDA[raridade.value]
    view = ConfirmarVendaTodosView(interaction.user.id, raridade.value)

    await interaction.response.send_message(
        f"⚠️ Você está prestes a vender **{quantidade} pet(s) {raridade.value}**.\n"
        f"Pets trancados ou equipados não serão vendidos.\n"
        f"Valor total: **{valor_total:,} {SIGLA}**.\n\n"
        f"Confirmar?",
        view=view,
        ephemeral=True
    )


async def executar_fusao(interaction: discord.Interaction, nome: str):
    nome_busca = nome.strip().lower()

    cursor.execute("""
        SELECT pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em
        FROM pets
        WHERE user_id = ? AND LOWER(nome) = ? AND trancado = 0 AND equipado = 0
        ORDER BY
            CASE evolucao
                WHEN 'Diamante' THEN 5
                WHEN 'Esmeralda' THEN 4
                WHEN 'Ouro' THEN 3
                WHEN 'Prata' THEN 2
                WHEN 'Bronze' THEN 1
                ELSE 0
            END ASC,
            CASE mutacao WHEN 'Normal' THEN 0 ELSE 1 END DESC,
            pet_id ASC
    """, (interaction.user.id, nome_busca))

    candidatos = cursor.fetchall()

    if len(candidatos) < 5:
        await interaction.response.send_message(
            f"❌ Você precisa de **5 pets iguais** disponíveis para fundir. Encontrados: **{len(candidatos)}**.",
            ephemeral=True
        )
        return

    evolucao_base = candidatos[0][6]

    if evolucao_base == "Diamante":
        await interaction.response.send_message("❌ Esse pet já está na evolução máxima: **Diamante**.", ephemeral=True)
        return

    grupo = [pet for pet in candidatos if pet[6] == evolucao_base]

    if len(grupo) < 5:
        await interaction.response.send_message(
            f"❌ Você tem pets suficientes no total, mas precisa de **5 {nome} {evolucao_base}** para a próxima fusão.",
            ephemeral=True
        )
        return

    selecionados = grupo[:5]
    indice_atual = EVOLUCOES_FUSAO.index(evolucao_base)
    proxima_evolucao = EVOLUCOES_FUSAO[indice_atual + 1]
    custo = CUSTO_FUSAO[evolucao_base]
    saldo = obter_saldo(interaction.user.id)

    if saldo < custo:
        await interaction.response.send_message(
            f"❌ Você precisa de **{custo:,} {SIGLA}** para essa fusão.",
            ephemeral=True
        )
        return

    primeiro = selecionados[0]
    limite_mutacoes = LIMITE_MUTACOES_FUSAO[proxima_evolucao]
    mutacao_final = juntar_mutacoes(selecionados, limite_mutacoes)

    ids_usados = [pet[0] for pet in selecionados]
    placeholders = ",".join("?" for _ in ids_usados)

    alterar_saldo(interaction.user.id, -custo)
    cursor.execute(
        f"DELETE FROM pets WHERE user_id = ? AND pet_id IN ({placeholders})",
        [interaction.user.id] + ids_usados
    )
    conn.commit()

    novo_id = criar_pet_manual(
        interaction.user.id,
        primeiro[1],
        primeiro[2],
        primeiro[3],
        primeiro[4],
        mutacao_final,
        proxima_evolucao
    )
    registrar_missao_evento(interaction.user.id, "fundir", 1)

    await interaction.response.send_message(
        f"✨ **Fusão concluída!**\n\n"
        f"Você usou: **5x {primeiro[1]} {evolucao_base}**\n"
        f"Custo: **{custo:,} {SIGLA}**\n"
        f"Resultado: {primeiro[4]} **{primeiro[1]} #{novo_id} {proxima_evolucao}**\n"
        f"Mutação final: **{mutacao_final}**",
        ephemeral=True
    )

    await enviar_log(
        interaction.guild,
        f"✨ **LOG DE FUSÃO**\n"
        f"Jogador: {interaction.user.mention}\n"
        f"Resultado: **{primeiro[1]} #{novo_id} {proxima_evolucao}**\n"
        f"Mutação: **{mutacao_final}**\n"
        f"Custo: **{custo:,} {SIGLA}**"
    )


@pet_group.command(name="fundir", description="Funde 5 pets iguais da mesma evolução.")
async def pet_fundir(interaction: discord.Interaction, nome: str):
    await executar_fusao(interaction, nome)


@bot.tree.command(name="fundir", description="Atalho para fundir 5 pets iguais.")
async def fundir(interaction: discord.Interaction, nome: str):
    await executar_fusao(interaction, nome)



bot.tree.add_command(pet_group)
