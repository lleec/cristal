from core import *


class MissoesView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.pagina = 0
        self.periodos = PERIODOS_MISSAO
        self.atualizar_botoes()

    def atualizar_botoes(self):
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= len(self.periodos) - 1

    def gerar_texto(self):
        periodo = self.periodos[self.pagina]
        garantir_missao_usuario(self.user_id, periodo)
        chave = chave_periodo_atual(periodo)
        cursor.execute("""
            SELECT mission_id, progresso, coletada
            FROM missoes_jogador
            WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
        """, (self.user_id, periodo, chave))
        mission_id, progresso, coletada = cursor.fetchone()
        nomes = {"diaria": "Diária", "semanal": "Semanal", "mensal": "Mensal"}
        texto = (
            f"📜 **Missões da Cristal** — Página **{self.pagina + 1}/{len(self.periodos)}**\n"
            f"Período: **{nomes.get(periodo, periodo.title())}**\n\n"
            f"{texto_missao(periodo, mission_id, progresso, coletada)}\n\n"
            f"Use **/missao coletar {periodo}** para receber a recompensa.\n"
            f"Use **/missao reroll {periodo}** para trocar a missão. Cooldown: **24h**."
        )
        return texto

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa lista de missões não é sua.", ephemeral=True)
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
        if self.pagina < len(self.periodos) - 1:
            self.pagina += 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.gerar_texto(), view=self)


@bot.tree.command(name="missoes", description="Mostra suas missões diária, semanal e mensal.")
async def missoes(interaction: discord.Interaction):
    garantir_todas_missoes(interaction.user.id)
    view = MissoesView(interaction.user.id)
    await interaction.response.send_message(view.gerar_texto(), view=view)


missao_group = app_commands.Group(name="missao", description="Comandos de missões.")


@missao_group.command(name="progresso", description="Mostra o progresso das suas missões.")
async def missao_progresso(interaction: discord.Interaction):
    garantir_todas_missoes(interaction.user.id)
    textos = []
    for periodo, mission_id, progresso, coletada in obter_missoes_usuario(interaction.user.id):
        textos.append(texto_missao(periodo, mission_id, progresso, coletada))
    await interaction.response.send_message("📜 **Suas missões**\n\n" + "\n\n".join(textos))


@missao_group.command(name="coletar", description="Coleta a recompensa de uma missão concluída.")
@app_commands.choices(periodo=[
    app_commands.Choice(name="diaria", value="diaria"),
    app_commands.Choice(name="semanal", value="semanal"),
    app_commands.Choice(name="mensal", value="mensal"),
])
async def missao_coletar(interaction: discord.Interaction, periodo: app_commands.Choice[str]):
    ok, texto = coletar_missao_usuario(interaction.user.id, periodo.value)
    await interaction.response.send_message(texto)


@missao_group.command(name="reroll", description="Troca uma missão. Cooldown de 24 horas por período.")
@app_commands.choices(periodo=[
    app_commands.Choice(name="diaria", value="diaria"),
    app_commands.Choice(name="semanal", value="semanal"),
    app_commands.Choice(name="mensal", value="mensal"),
])
async def missao_reroll(interaction: discord.Interaction, periodo: app_commands.Choice[str]):
    ok, texto = reroll_missao_usuario(interaction.user.id, periodo.value)
    await interaction.response.send_message(texto)


bot.tree.add_command(missao_group)
