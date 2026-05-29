from core import *

cassino_group = app_commands.Group(name="cassino", description="Jogos do cassino da Cristal.")


def validar_canal_cassino(interaction: discord.Interaction):
    return interaction.channel and interaction.channel.name == CASSINO_CANAL


async def checar_cassino_pago(interaction: discord.Interaction, valor: int, minimo: int, maximo: int):
    if not validar_canal_cassino(interaction):
        await interaction.response.send_message(f"❌ Use este comando no canal {nome_canal('cassino')}.")
        return False

    if valor < minimo or valor > maximo:
        await interaction.response.send_message("❌ Valor de aposta inválido.")
        return False

    restante = cooldown_cassino_pago_restante(interaction.user.id)
    if restante > 0:
        await interaction.response.send_message(f"⏳ Aguarde **{restante}s** para jogar novamente.")
        return False

    saldo = obter_saldo(interaction.user.id)
    if saldo < valor:
        await interaction.response.send_message("❌ Você não tem Cristais suficientes.")
        return False

    return True


def aplicar_bonus_sorte(user_id: int, premio: int):
    bonus, detalhes = calcular_bonus_linha(user_id, "Sorte")
    premio_final = int(premio * (1 + bonus))
    return premio_final, bonus, detalhes


@cassino_group.command(name="animal", description="Tente adivinhar o animal secreto.")
async def cassino_animal(interaction: discord.Interaction, palpite: str):
    if not validar_canal_cassino(interaction):
        await interaction.response.send_message(f"❌ Use este comando no canal {nome_canal('cassino')}.")
        return

    restante = cooldown_cassino_animal_restante(interaction.user.id)
    if restante > 0:
        await interaction.response.send_message(f"⏳ Tente novamente em **{restante}s**.")
        return

    if acertos_animal_hoje(interaction.user.id) >= CASSINO_ANIMAL_ACERTOS_DIA:
        await interaction.response.send_message("❌ Você já atingiu o limite de acertos de hoje nesse jogo.")
        return

    registrar_tentativa_animal(interaction.user.id)
    registrar_missao_evento(interaction.user.id, "cassino", 1)
    animal = escolher_animal_cassino()

    if normalizar_texto(palpite) == normalizar_texto(animal["nome"]):
        alterar_saldo(interaction.user.id, CASSINO_ANIMAL_RECOMPENSA)
        registrar_missao_evento(interaction.user.id, "cassino_win", 1)
        acertos = registrar_acerto_animal(interaction.user.id)
        await interaction.response.send_message(
            f"✅ Acertou! Era **{animal['nome']}**. Você ganhou **{CASSINO_ANIMAL_RECOMPENSA} {SIGLA}**.\n"
            f"Acertos hoje: **{acertos}/{CASSINO_ANIMAL_ACERTOS_DIA}**."
        )
    else:
        await interaction.response.send_message(
            f"❌ Errou! Era **{animal['nome']}**. Tente novamente em alguns segundos."
        )


@cassino_group.command(name="jackpot", description="Gire 3 animais e tente ganhar.")
async def cassino_jackpot(interaction: discord.Interaction, valor: int):
    if not await checar_cassino_pago(interaction, valor, CASSINO_JACKPOT_MINIMO, CASSINO_JACKPOT_MAXIMO):
        return

    alterar_saldo(interaction.user.id, -valor)
    registrar_cassino_pago(interaction.user.id)
    registrar_missao_evento(interaction.user.id, "cassino", 1)

    animais = [random.choice(PETS) for _ in range(3)]
    nomes = [a["nome"] for a in animais]
    exibicao = "  ".join([f"{a['emoji']} **{a['nome']}**" for a in animais])

    contagens = {nome: nomes.count(nome) for nome in set(nomes)}
    maior = max(contagens.values())

    if maior == 3:
        premio_base = valor * 8
        resultado = "🎉 Jackpot!"
        registrar_missao_evento(interaction.user.id, "jackpot", 1)
    elif maior == 2:
        premio_base = int(valor * 1.5)
        resultado = "✨ Dois iguais!"
    else:
        premio_base = 0
        resultado = "💀 Não foi dessa vez."

    if premio_base > 0:
        premio, bonus, _ = aplicar_bonus_sorte(interaction.user.id, premio_base)
        alterar_saldo(interaction.user.id, premio)
        registrar_missao_evento(interaction.user.id, "cassino_win", 1)
        await interaction.response.send_message(
            f"🎰 **Jackpot de Animais**\n\n{exibicao}\n\n{resultado}\nVocê recebeu **{premio:,} {SIGLA}**."
        )
    else:
        await interaction.response.send_message(
            f"🎰 **Jackpot de Animais**\n\n{exibicao}\n\n{resultado}"
        )


@cassino_group.command(name="moeda", description="Aposte em cara ou coroa.")
@app_commands.choices(escolha=[
    app_commands.Choice(name="cara", value="cara"),
    app_commands.Choice(name="coroa", value="coroa"),
])
async def cassino_moeda(interaction: discord.Interaction, valor: int, escolha: app_commands.Choice[str]):
    if not await checar_cassino_pago(interaction, valor, CASSINO_APOSTA_MINIMA, CASSINO_APOSTA_MAXIMA):
        return

    alterar_saldo(interaction.user.id, -valor)
    registrar_cassino_pago(interaction.user.id)
    registrar_missao_evento(interaction.user.id, "cassino", 1)

    resultado = random.choice(["cara", "coroa"])
    if escolha.value == resultado:
        premio_base = int(valor * 1.9)
        premio, _, _ = aplicar_bonus_sorte(interaction.user.id, premio_base)
        alterar_saldo(interaction.user.id, premio)
        registrar_missao_evento(interaction.user.id, "cassino_win", 1)
        await interaction.response.send_message(
            f"🪙 Deu **{resultado}**. Você ganhou **{premio:,} {SIGLA}**."
        )
    else:
        await interaction.response.send_message(
            f"🪙 Deu **{resultado}**. Você perdeu a aposta."
        )


@cassino_group.command(name="numero", description="Tente acertar o número sorteado.")
async def cassino_numero(interaction: discord.Interaction, valor: int, numero: int):
    if numero < 1 or numero > 10:
        await interaction.response.send_message("❌ Escolha um número de 1 a 10.")
        return

    if not await checar_cassino_pago(interaction, valor, CASSINO_APOSTA_MINIMA, CASSINO_APOSTA_MAXIMA):
        return

    alterar_saldo(interaction.user.id, -valor)
    registrar_cassino_pago(interaction.user.id)
    registrar_missao_evento(interaction.user.id, "cassino", 1)

    sorteado = random.randint(1, 10)
    if numero == sorteado:
        premio_base = valor * 8
        premio, _, _ = aplicar_bonus_sorte(interaction.user.id, premio_base)
        alterar_saldo(interaction.user.id, premio)
        registrar_missao_evento(interaction.user.id, "cassino_win", 1)
        await interaction.response.send_message(
            f"🔢 O número era **{sorteado}**. Você ganhou **{premio:,} {SIGLA}**."
        )
    else:
        await interaction.response.send_message(
            f"🔢 O número era **{sorteado}**. Você perdeu a aposta."
        )


@cassino_group.command(name="roleta", description="Aposte na roleta.")
@app_commands.choices(escolha=[
    app_commands.Choice(name="vermelho", value="vermelho"),
    app_commands.Choice(name="preto", value="preto"),
    app_commands.Choice(name="verde", value="verde"),
])
async def cassino_roleta(interaction: discord.Interaction, valor: int, escolha: app_commands.Choice[str]):
    if not await checar_cassino_pago(interaction, valor, CASSINO_APOSTA_MINIMA, CASSINO_APOSTA_MAXIMA):
        return

    alterar_saldo(interaction.user.id, -valor)
    registrar_cassino_pago(interaction.user.id)
    registrar_missao_evento(interaction.user.id, "cassino", 1)

    resultado = random.choices(["vermelho", "preto", "verde"], weights=[47, 47, 6], k=1)[0]
    emoji = {"vermelho": "🔴", "preto": "⚫", "verde": "🟢"}[resultado]

    if escolha.value == resultado:
        multiplicador = 10 if resultado == "verde" else 1.9
        premio_base = int(valor * multiplicador)
        premio, _, _ = aplicar_bonus_sorte(interaction.user.id, premio_base)
        alterar_saldo(interaction.user.id, premio)
        registrar_missao_evento(interaction.user.id, "cassino_win", 1)
        await interaction.response.send_message(
            f"🎡 A roleta caiu em {emoji} **{resultado}**. Você ganhou **{premio:,} {SIGLA}**."
        )
    else:
        await interaction.response.send_message(
            f"🎡 A roleta caiu em {emoji} **{resultado}**. Você perdeu a aposta."
        )


bot.tree.add_command(cassino_group)
