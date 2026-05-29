from core import *


class LojaView(discord.ui.View):
    def __init__(self, user_id: int, pagina: int = 0):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.pagina = pagina
        self.atualizar_botoes()

    def atualizar_botoes(self):
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= len(CATEGORIAS_LOJA) - 1

    def gerar_texto(self):
        categoria = CATEGORIAS_LOJA[self.pagina]
        itens = [(item_id, item) for item_id, item in ITENS_LOJA.items() if item["categoria"] == categoria]

        texto = f"🏪 **Loja Cristal** — {categoria} ({self.pagina + 1}/{len(CATEGORIAS_LOJA)})\n\n"

        if categoria == "Tesouros":
            texto += "Esses itens normalmente vêm de drops e servem para venda.\n\n"

        for item_id, item in itens:
            preco = item.get("preco", 0)
            preco_txt = "Não comprável" if preco <= 0 else f"{preco:,} {SIGLA}"
            limite = item.get("limite_diario")
            limite_txt = f" | Limite diário: {limite}" if limite else ""
            venda = item.get("valor_venda")
            venda_txt = f" | Venda: {venda:,} {SIGLA}" if venda else ""
            texto += (
                f"{item['emoji']} **#{item_id} — {item['nome']}**\n"
                f"Preço: **{preco_txt}**{limite_txt}{venda_txt}\n"
                f"{item['descricao']}\n\n"
            )

        texto += "Use `/comprar id quantidade`, `/usar id`, `/venderitem id quantidade`."
        return texto

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa loja não é sua.", ephemeral=True)
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
        if self.pagina < len(CATEGORIAS_LOJA) - 1:
            self.pagina += 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.gerar_texto(), view=self)


class ItensView(discord.ui.View):
    def __init__(self, user_id: int, resultados: list, pagina: int = 0, por_pagina: int = 10):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.resultados = resultados
        self.pagina = pagina
        self.por_pagina = por_pagina
        self.atualizar_botoes()

    def total_paginas(self):
        return max(1, (len(self.resultados) + self.por_pagina - 1) // self.por_pagina)

    def atualizar_botoes(self):
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= self.total_paginas() - 1

    def gerar_texto(self):
        total = self.total_paginas()
        inicio = self.pagina * self.por_pagina
        fim = inicio + self.por_pagina
        itens = self.resultados[inicio:fim]

        texto = f"🎒 **Seus itens** — Página {self.pagina + 1}/{total}\n\n"
        for item_id, quantidade in itens:
            item = ITENS_LOJA.get(item_id)
            if not item:
                continue
            venda = item.get("valor_venda", 0)
            venda_txt = f" | Venda: {venda:,} {SIGLA}" if venda else ""
            texto += f"{item['emoji']} **#{item_id} — {item['nome']}** x**{quantidade}**{venda_txt}\n"

        texto += "\nUse `/usar id` ou `/venderitem id quantidade`."
        return texto

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esse inventário não é seu.", ephemeral=True)
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


@bot.tree.command(name="loja", description="Mostra a loja da Cristal.")
async def loja(interaction: discord.Interaction):
    view = LojaView(interaction.user.id)
    await interaction.response.send_message(view.gerar_texto(), view=view, ephemeral=True)


@bot.tree.command(name="itens", description="Mostra seus itens.")
async def itens(interaction: discord.Interaction):
    cursor.execute("""
        SELECT item_id, quantidade
        FROM inventario_itens
        WHERE user_id = ? AND quantidade > 0
        ORDER BY item_id ASC
    """, (interaction.user.id,))
    resultados = cursor.fetchall()

    if not resultados:
        await interaction.response.send_message("🎒 Você ainda não tem itens.", ephemeral=True)
        return

    view = ItensView(interaction.user.id, resultados)
    await interaction.response.send_message(view.gerar_texto(), view=view, ephemeral=True)


@bot.tree.command(name="comprar", description="Compra um item da loja pelo ID.")
async def comprar(interaction: discord.Interaction, id: int, quantidade: int = 1):
    item = ITENS_LOJA.get(id)

    if not item:
        await interaction.response.send_message("❌ Item não encontrado.", ephemeral=True)
        return

    if quantidade <= 0:
        await interaction.response.send_message("❌ A quantidade precisa ser maior que zero.", ephemeral=True)
        return

    if item.get("preco", 0) <= 0:
        await interaction.response.send_message("❌ Esse item não pode ser comprado diretamente.", ephemeral=True)
        return

    if item["tipo"] in ["unico", "acessorio"]:
        quantidade = 1
        if possui_item(interaction.user.id, id):
            await interaction.response.send_message("❌ Você já possui esse item permanente.", ephemeral=True)
            return

    limite = item.get("limite_diario")
    if limite:
        ja_comprou = compras_diarias_item(interaction.user.id, id)
        if ja_comprou + quantidade > limite:
            await interaction.response.send_message(
                f"❌ Limite diário excedido. Você já comprou **{ja_comprou}/{limite}** hoje.",
                ephemeral=True
            )
            return

    total = item["preco"] * quantidade
    saldo = obter_saldo(interaction.user.id)
    if saldo < total:
        await interaction.response.send_message(
            f"❌ Você precisa de **{total:,} {SIGLA}**. Seu saldo: **{saldo:,} {SIGLA}**.",
            ephemeral=True
        )
        return

    alterar_saldo(interaction.user.id, -total)

    if id == 20:
        alterar_bilhetes(interaction.user.id, quantidade)
        registrar_compra_diaria(interaction.user.id, id, quantidade)
        await interaction.response.send_message(
            f"✅ Você comprou **{quantidade}x {item['emoji']} {item['nome']} #{id}** por **{total:,} {SIGLA}**.\n"
            f"🎟️ Bilhetes adicionados diretamente ao seu saldo.",
            ephemeral=True
        )
        return

    if item["tipo"] in ["unico", "acessorio", "pocao", "tesouro"]:
        adicionar_item(interaction.user.id, id, quantidade)

    if item["tipo"] == "diario":
        adicionar_item(interaction.user.id, id, quantidade)
        registrar_compra_diaria(interaction.user.id, id, quantidade)

    if id == 2:
        cursor.execute("UPDATE usuarios SET slots_pets = slots_pets + 1 WHERE user_id = ?", (interaction.user.id,))
        conn.commit()

    msg_extra = ""
    if id == 1:
        msg_extra = "\nUse `/xpshare id` para escolher o pet reserva."
    elif id == 2:
        msg_extra = "\n🐾 Slot extra liberado automaticamente."
    elif item["tipo"] == "acessorio":
        msg_extra = "\n✅ Acessório ativado automaticamente."

    await interaction.response.send_message(
        f"✅ Você comprou **{quantidade}x {item['emoji']} {item['nome']} #{id}** por **{total:,} {SIGLA}**.{msg_extra}",
        ephemeral=True
    )


@bot.tree.command(name="usar", description="Usa um item consumível pelo ID.")
async def usar(interaction: discord.Interaction, id: int):
    item = ITENS_LOJA.get(id)

    if not item:
        await interaction.response.send_message("❌ Item não encontrado.", ephemeral=True)
        return

    if not possui_item(interaction.user.id, id):
        await interaction.response.send_message("❌ Você não possui esse item.", ephemeral=True)
        return

    if id == 20:
        remover_item(interaction.user.id, id, 1)
        alterar_bilhetes(interaction.user.id, 1)
        await interaction.response.send_message("🎟️ Você usou **Bilhete Premium #20** e recebeu **1 bilhete**.", ephemeral=True)
        return

    if id == 21:
        remover_item(interaction.user.id, id, 1)
        energia_atual = atualizar_energia(interaction.user.id)
        nova_energia = min(ENERGIA_MAXIMA, energia_atual + ENERGETICO_VALOR)
        cursor.execute("UPDATE usuarios SET energia = ?, ultima_energia = ? WHERE user_id = ?", (nova_energia, int(time.time()), interaction.user.id))
        conn.commit()
        await interaction.response.send_message(f"⚡ Você recuperou energia. Energia atual: **{nova_energia}/{ENERGIA_MAXIMA}**.", ephemeral=True)
        return

    if item["tipo"] != "pocao":
        await interaction.response.send_message("❌ Esse item não é usável.", ephemeral=True)
        return

    restante_cd = cooldown_pocao_restante(interaction.user.id)
    if restante_cd > 0:
        horas = restante_cd // 3600
        minutos = (restante_cd % 3600) // 60
        await interaction.response.send_message(f"⏳ Você só pode usar outra poção em **{horas}h {minutos}min**.", ephemeral=True)
        return

    buff = item["buff"]
    if buff_ativo(interaction.user.id, buff):
        await interaction.response.send_message("❌ Você já tem essa poção ativa.", ephemeral=True)
        return

    remover_item(interaction.user.id, id, 1)
    ativar_buff(interaction.user.id, buff, item.get("duracao", 0))

    duracao = item.get("duracao", 0)
    if duracao > 0:
        tempo_txt = f"por **{duracao // 60} minutos**"
    else:
        tempo_txt = "até ser consumida pelo próximo uso válido"

    await interaction.response.send_message(
        f"🧪 Você usou **{item['nome']} #{id}**. Efeito ativo {tempo_txt}.",
        ephemeral=True
    )


@bot.tree.command(name="buffs", description="Mostra seus buffs ativos.")
async def buffs(interaction: discord.Interaction):
    linhas = []
    for item_id, item in ITENS_LOJA.items():
        if item.get("tipo") != "pocao":
            continue
        buff = item["buff"]
        if buff_ativo(interaction.user.id, buff):
            restante = tempo_buff_restante(interaction.user.id, buff)
            if restante == -1:
                tempo = "próximo uso válido"
            else:
                tempo = f"{restante // 60}min"
            linhas.append(f"{item['emoji']} **{item['nome']}** — {tempo}")

    cd = cooldown_pocao_restante(interaction.user.id)
    cd_txt = "Livre" if cd <= 0 else f"{cd // 3600}h {(cd % 3600) // 60}min"

    if not linhas:
        linhas.append("Nenhum buff ativo.")

    await interaction.response.send_message(
        "🧪 **Seus buffs**\n\n" + "\n".join(linhas) + f"\n\nCooldown de poções: **{cd_txt}**",
        ephemeral=True
    )


@bot.tree.command(name="xpshare", description="Define ou remove o pet que receberá 50% do XP.")
async def xpshare(interaction: discord.Interaction, id: int = 0):
    if not possui_item(interaction.user.id, 1):
        await interaction.response.send_message("❌ Você precisa comprar o **XP Share #1** na loja.", ephemeral=True)
        return

    if id <= 0:
        cursor.execute("UPDATE usuarios SET xpshare_pet_id = 0 WHERE user_id = ?", (interaction.user.id,))
        conn.commit()
        await interaction.response.send_message("✅ XP Share removido.", ephemeral=True)
        return

    pet = obter_pet(interaction.user.id, id)
    if not pet:
        await interaction.response.send_message("❌ Pet não encontrado no seu inventário.", ephemeral=True)
        return

    pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em = pet
    cursor.execute("UPDATE usuarios SET xpshare_pet_id = ? WHERE user_id = ?", (id, interaction.user.id))
    conn.commit()
    await interaction.response.send_message(f"📘 XP Share definido para {emoji} **{nome} #{id}**.", ephemeral=True)


@bot.tree.command(name="venderitem", description="Vende um item de tesouro pelo ID.")
async def venderitem(interaction: discord.Interaction, id: int, quantidade: int = 1):
    item = ITENS_LOJA.get(id)

    if not item:
        await interaction.response.send_message("❌ Item não encontrado.", ephemeral=True)
        return

    if item.get("tipo") != "tesouro":
        await interaction.response.send_message("❌ Só tesouros podem ser vendidos por esse comando.", ephemeral=True)
        return

    if quantidade <= 0:
        await interaction.response.send_message("❌ A quantidade precisa ser maior que zero.", ephemeral=True)
        return

    if not remover_item(interaction.user.id, id, quantidade):
        await interaction.response.send_message("❌ Você não tem quantidade suficiente desse item.", ephemeral=True)
        return

    total = item.get("valor_venda", 0) * quantidade
    alterar_saldo(interaction.user.id, total)

    await interaction.response.send_message(
        f"💰 Você vendeu **{quantidade}x {item['nome']} #{id}** por **{total:,} {SIGLA}**.",
        ephemeral=True
    )
