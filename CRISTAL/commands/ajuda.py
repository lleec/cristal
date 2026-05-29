from core import *

# ============================================================
# AJUDA PAGINADA
# Resumo simples dos comandos principais.
# ============================================================

AJUDA_PAGINAS = [
    (
        "📘 **Ajuda — Economia**\n\n"
        "`/saldo` — mostra seu saldo ou o saldo de outro jogador.\n"
        "`/cs` — atalho para saldo.\n"
        "`/dia` — recebe sua recompensa diária.\n"
        "`/diario` — igual ao /dia.\n"
        "`/doar` — doa Cristais para outro jogador.\n"
        "`/ranking` — mostra o ranking de Cristais.\n"
        "`/top` — atalho para ranking.\n"
        "`/energia` — mostra sua energia atual."
    ),
    (
        "🐾 **Ajuda — Pets e Gacha**\n\n"
        "`/gc` — abre o Gacha Normal.\n"
        "`/gm` — abre o Gacha Melhor.\n"
        "`/gp` — abre o Gacha Premium.\n"
        "`/gacha` — escolhe o tipo de gacha.\n"
        "`/pets` — mostra seus pets.\n"
        "`/pet info` — mostra detalhes de um pet seu.\n"
        "`/pet ver` — vê um pet de outro jogador.\n"
        "`/pet equipar` — equipa um pet.\n"
        "`/pet desequipar` — desequipa um pet.\n"
        "`/pet ativos` — mostra pets equipados."
    ),
    (
        "🔒 **Ajuda — Gestão de Pets**\n\n"
        "`/pet trancar` — protege um pet contra venda/fusão.\n"
        "`/pet destrancar` — remove a proteção.\n"
        "`/pet favoritar` — marca um pet como favorito.\n"
        "`/pet desfavoritar` — remove favorito.\n"
        "`/pet vender` — vende um pet.\n"
        "`/pet vender-todos` — vende pets de uma raridade.\n"
        "`/pet fundir` — funde 5 pets iguais.\n"
        "`/fundir` — atalho para fusão."
    ),
    (
        "💼 **Ajuda — Profissões**\n\n"
        "`/profissao escolher` — escolhe uma profissão.\n"
        "`/profissao minha` — mostra sua profissão atual.\n"
        "`/profissao sair` — sai da profissão atual.\n"
        "`/pescar` — atividade de pesca.\n"
        "`/minerar` — atividade de mineração.\n"
        "`/cacar` — atividade de caça.\n"
        "`/explorar` — atividade de exploração.\n"
        "`/trabalhar` — atividade de trabalho."
    ),
    (
        "🏪 **Ajuda — Loja e Itens**\n\n"
        "`/loja` — mostra a loja em páginas.\n"
        "`/comprar` — compra um item pelo ID.\n"
        "`/itens` — mostra seus itens.\n"
        "`/usar` — usa um item consumível.\n"
        "`/buffs` — mostra buffs ativos.\n"
        "`/xpshare` — define o pet que recebe XP compartilhado.\n"
        "`/venderitem` — vende tesouros do inventário."
    ),
    (
        "🎰 **Ajuda — Cassino**\n\n"
        "`/cassino animal` — tenta adivinhar o animal secreto.\n"
        "`/cassino jackpot` — gira 3 animais.\n"
        "`/cassino moeda` — aposta em cara ou coroa.\n"
        "`/cassino numero` — tenta acertar um número.\n"
        "`/cassino roleta` — aposta na roleta."
    ),
    (
        "⚔️ **Ajuda — Raid, Eventos e Perfil**\n\n"
        "`/raid` — participa da raid ativa.\n"
        "`/evento listar` — mostra eventos ativos.\n"
        "`/perfil` — mostra seu perfil.\n"
        "`/conquistas` — mostra suas conquistas.\n"
        "`/titulo meus` — mostra títulos desbloqueados.\n"
        "`/titulo usar` — equipa um título.\n"
        "`/titulo remover` — remove seu título."
    ),
]


class AjudaView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.pagina = 0
        self.atualizar_botoes()

    def texto_atual(self):
        return f"{AJUDA_PAGINAS[self.pagina]}\n\nPágina **{self.pagina + 1}/{len(AJUDA_PAGINAS)}**"

    def atualizar_botoes(self):
        self.anterior.disabled = self.pagina <= 0
        self.proxima.disabled = self.pagina >= len(AJUDA_PAGINAS) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Essa ajuda não é sua.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Anterior", emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def anterior(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina > 0:
            self.pagina -= 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.texto_atual(), view=self)

    @discord.ui.button(label="Próxima", emoji="➡️", style=discord.ButtonStyle.secondary)
    async def proxima(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.pagina < len(AJUDA_PAGINAS) - 1:
            self.pagina += 1
        self.atualizar_botoes()
        await interaction.response.edit_message(content=self.texto_atual(), view=self)


@bot.tree.command(name="ajuda", description="Mostra um resumo dos comandos da Cristal.")
async def ajuda(interaction: discord.Interaction):
    view = AjudaView(interaction.user.id)
    await interaction.response.send_message(view.texto_atual(), view=view, ephemeral=True)
