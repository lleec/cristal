import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import time
import os
import random
import shutil
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

NOME_MOEDA = "Cristais"
SIGLA = "CS"

CARGO_ADMIN_BOT = "Administrador do Bot"
CANAL_LOGS = "logs-cristal"

# IDs fixos dos canais do servidor. Usar ID é mais seguro que nome,
# porque o bot continua funcionando mesmo se você renomear os canais.
CANAIS = {
    "pesca": 1509071882287054878,
    "mineracao": 1509071839362547892,
    "caca": 1509071813462986772,
    "exploracao": 1509071782194319470,
    "trabalho": 1509071693061292162,
    "raid": 1509071601923264573,
    "raids": 1509071601923264573,
    "cassino": 1509071655132074046,
    "logs": 1509058816225050634,
}

COOLDOWN_DIARIO = 24 * 60 * 60
LIMITE_PERDA_STREAK = 48 * 60 * 60
MAX_BILHETES_SEMANAIS = 4

ENERGIA_MAXIMA = 100
ENERGIA_POR_MINUTO = 1

GACHA_NORMAL_CUSTO = 50
GACHA_MELHOR_CUSTO = 500
GACHA_PREMIUM_CUSTO = 1000

COOLDOWN_TROCA_PROFISSAO = 24 * 60 * 60

XP_ATIVIDADE = 8
XP_RAID = 20
NIVEL_MAXIMO_PET = 50

RAID_DURACAO = 2 * 60 * 60
RAID_CANAL = "raids"
CASSINO_CANAL = "cassino"
CASSINO_ANIMAL_COOLDOWN = 10
CASSINO_ANIMAL_RECOMPENSA = 20
CASSINO_ANIMAL_ACERTOS_DIA = 10
CASSINO_APOSTA_MINIMA = 10
CASSINO_APOSTA_MAXIMA = 5000
CASSINO_JACKPOT_MINIMO = 25
CASSINO_JACKPOT_MAXIMO = 1000
CASSINO_COOLDOWN_PAGO = 5

MINI_EVENTO_DURACAO = 30 * 60
MINI_EVENTO_CHECK_MINUTOS = 30
MINI_EVENTO_CHANCE = 20  # porcentagem a cada verificação
MINI_EVENTO_DROP_MULT = 2.0
MINI_EVENTO_GANHO_MULT = 1.20

PROFISSOES = {
    "pesca": {
        "nome": "Pesca",
        "cargo": "Pescador",
        "canal": "pesca",
        "comando": "pescar",
        "linha_bonus": "Pesca",
        "energia": 5,
        "ganho_min": 35,
        "ganho_max": 85,
        "emoji": "🎣"
    },
    "mineracao": {
        "nome": "Mineração",
        "cargo": "Minerador",
        "canal": "mineracao",
        "comando": "minerar",
        "linha_bonus": "Mineração",
        "energia": 8,
        "ganho_min": 55,
        "ganho_max": 120,
        "emoji": "⛏️"
    },
    "caca": {
        "nome": "Caça",
        "cargo": "Caçador",
        "canal": "caca",
        "comando": "cacar",
        "linha_bonus": "Caça",
        "energia": 7,
        "ganho_min": 45,
        "ganho_max": 110,
        "emoji": "🐺"
    },
    "exploracao": {
        "nome": "Exploração",
        "cargo": "Explorador",
        "canal": "exploracao",
        "comando": "explorar",
        "linha_bonus": "Exploração",
        "energia": 10,
        "ganho_min": 70,
        "ganho_max": 150,
        "emoji": "🦅"
    },
    "trabalho": {
        "nome": "Trabalho",
        "cargo": "Trabalhador",
        "canal": "trabalho",
        "comando": "trabalhar",
        "linha_bonus": "Trabalho",
        "energia": 6,
        "ganho_min": 40,
        "ganho_max": 95,
        "emoji": "💼"
    }
}

MULTIPLICADOR_RARIDADE_BONUS = {
    "Comum": 0.03,
    "Raro": 0.06,
    "Épico": 0.10,
    "Lendário": 0.16,
    "Mítico": 0.25
}

MULTIPLICADOR_EVOLUCAO_BONUS = {
    "Normal": 1.0,
    "Bronze": 1.08,
    "Prata": 1.16,
    "Ouro": 1.25,
    "Esmeralda": 1.35,
    "Diamante": 1.50
}

MULTIPLICADOR_MUTACAO_BONUS = {
    "Shiny": 0.05,
    "Anjo": 0.04,
    "Demônio": 0.04,
    "Podre": -0.08,
    "Corrompido": 0.08
}

RECOMPENSAS_DIA = {
    1: 100,
    2: 125,
    3: 150,
    4: 175,
    5: 200,
    6: 225,
    7: 250
}

RARIDADE_PESO = {
    "Comum": 1,
    "Raro": 2,
    "Épico": 3,
    "Lendário": 4,
    "Mítico": 5
}

VALOR_VENDA = {
    "Comum": 5,
    "Raro": 20,
    "Épico": 75,
    "Lendário": 250,
    "Mítico": 1000
}

EVOLUCOES_FUSAO = ["Normal", "Bronze", "Prata", "Ouro", "Esmeralda", "Diamante"]
CUSTO_FUSAO = {
    "Normal": 100,
    "Bronze": 250,
    "Prata": 500,
    "Ouro": 1000,
    "Esmeralda": 2500
}
LIMITE_MUTACOES_FUSAO = {
    "Bronze": 2,
    "Prata": 3,
    "Ouro": 4,
    "Esmeralda": 5,
    "Diamante": 6
}

PETS = [
    # Diário/Eventos - Felinos
    {"nome": "Gato", "raridade": "Comum", "linha": "Diário/Eventos", "emoji": "🐱"},
    {"nome": "Leão", "raridade": "Raro", "linha": "Diário/Eventos", "emoji": "🦁"},
    {"nome": "Tigre", "raridade": "Épico", "linha": "Diário/Eventos", "emoji": "🐯"},
    {"nome": "Tigre Dente de Sabre", "raridade": "Lendário", "linha": "Diário/Eventos", "emoji": "🦷"},
    {"nome": "Quimera", "raridade": "Mítico", "linha": "Diário/Eventos", "emoji": "✨"},

    # Pesca
    {"nome": "Peixe-Palhaço", "raridade": "Comum", "linha": "Pesca", "emoji": "🐠"},
    {"nome": "Tubarão", "raridade": "Raro", "linha": "Pesca", "emoji": "🦈"},
    {"nome": "Orca", "raridade": "Épico", "linha": "Pesca", "emoji": "🐋"},
    {"nome": "Megalodonte", "raridade": "Lendário", "linha": "Pesca", "emoji": "🦈"},
    {"nome": "Kraken", "raridade": "Mítico", "linha": "Pesca", "emoji": "🐙"},

    # Raid / Dano
    {"nome": "Iguana", "raridade": "Comum", "linha": "Raid", "emoji": "🦎"},
    {"nome": "Crocodilo", "raridade": "Raro", "linha": "Raid", "emoji": "🐊"},
    {"nome": "Dragão de Komodo", "raridade": "Épico", "linha": "Raid", "emoji": "🦎"},
    {"nome": "T-Rex", "raridade": "Lendário", "linha": "Raid", "emoji": "🦖"},
    {"nome": "Dragão", "raridade": "Mítico", "linha": "Raid", "emoji": "🐉"},

    # Exploração
    {"nome": "Galinha", "raridade": "Comum", "linha": "Exploração", "emoji": "🐔"},
    {"nome": "Águia", "raridade": "Raro", "linha": "Exploração", "emoji": "🦅"},
    {"nome": "Pterodáctilo", "raridade": "Épico", "linha": "Exploração", "emoji": "🦕"},
    {"nome": "Grifo", "raridade": "Lendário", "linha": "Exploração", "emoji": "🪽"},
    {"nome": "Fênix", "raridade": "Mítico", "linha": "Exploração", "emoji": "🔥"},

    # Caça
    {"nome": "Cachorro", "raridade": "Comum", "linha": "Caça", "emoji": "🐶"},
    {"nome": "Lobo", "raridade": "Raro", "linha": "Caça", "emoji": "🐺"},
    {"nome": "Lobo-Terrível", "raridade": "Épico", "linha": "Caça", "emoji": "🐺"},
    {"nome": "Cerberus", "raridade": "Lendário", "linha": "Caça", "emoji": "🐕"},
    {"nome": "Fenrir", "raridade": "Mítico", "linha": "Caça", "emoji": "🌑"},

    # Mineração
    {"nome": "Coelho", "raridade": "Comum", "linha": "Mineração", "emoji": "🐰"},
    {"nome": "Urso Negro", "raridade": "Raro", "linha": "Mineração", "emoji": "🐻"},
    {"nome": "Urso Polar", "raridade": "Épico", "linha": "Mineração", "emoji": "🐻‍❄️"},
    {"nome": "Golem", "raridade": "Lendário", "linha": "Mineração", "emoji": "🪨"},
    {"nome": "Titã de Cristal", "raridade": "Mítico", "linha": "Mineração", "emoji": "💎"},

    # Sorte/Cassino
    {"nome": "Cobra", "raridade": "Comum", "linha": "Sorte", "emoji": "🐍"},
    {"nome": "Píton", "raridade": "Raro", "linha": "Sorte", "emoji": "🐍"},
    {"nome": "Anaconda", "raridade": "Épico", "linha": "Sorte", "emoji": "🐍"},
    {"nome": "Titanoboa", "raridade": "Lendário", "linha": "Sorte", "emoji": "🐍"},
    {"nome": "Hydra", "raridade": "Mítico", "linha": "Sorte", "emoji": "🐉"},

    # Trabalho
    {"nome": "Cavalo", "raridade": "Comum", "linha": "Trabalho", "emoji": "🐴"},
    {"nome": "Boi", "raridade": "Raro", "linha": "Trabalho", "emoji": "🐂"},
    {"nome": "Búfalo", "raridade": "Épico", "linha": "Trabalho", "emoji": "🐃"},
    {"nome": "Mamute", "raridade": "Lendário", "linha": "Trabalho", "emoji": "🦣"},
    {"nome": "Unicórnio", "raridade": "Mítico", "linha": "Trabalho", "emoji": "🦄"},
]

GACHAS = {
    "normal": {
        "nome": "Gacha Normal",
        "custo": GACHA_NORMAL_CUSTO,
        "usa_bilhete": False,
        "chances": {"Comum": 80, "Raro": 17, "Épico": 3, "Lendário": 0, "Mítico": 0}
    },
    "melhor": {
        "nome": "Gacha Melhor",
        "custo": GACHA_MELHOR_CUSTO,
        "usa_bilhete": False,
        "chances": {"Comum": 30, "Raro": 45, "Épico": 20, "Lendário": 5, "Mítico": 0}
    },
    "premium": {
        "nome": "Gacha Premium",
        "custo": GACHA_PREMIUM_CUSTO,
        "usa_bilhete": True,
        "chances": {"Comum": 0, "Raro": 60, "Épico": 30, "Lendário": 9, "Mítico": 1}
    }
}


# =========================
# LOJA / ITENS / BUFFS
# =========================
COOLDOWN_USO_POCAO = 2 * 60 * 60
ENERGETICO_VALOR = 25

# Itens compráveis e itens de drop usam o mesmo ID.
# tipo: unico, acessorio, diario, pocao, tesouro
ITENS_LOJA = {
    1: {"nome": "XP Share", "emoji": "📘", "categoria": "Únicos", "tipo": "unico", "preco": 500_000,
        "descricao": "Permite definir um pet reserva para receber 50% do XP."},
    2: {"nome": "Slot Extra", "emoji": "🐾", "categoria": "Únicos", "tipo": "unico", "preco": 1_000_000,
        "descricao": "Libera +1 slot de pet equipado. Compra única."},

    10: {"nome": "Picareta", "emoji": "⛏️", "categoria": "Acessórios", "tipo": "acessorio", "preco": 350_000,
         "linhas": ["Mineração"], "bonus": 0.10, "descricao": "+10% em mineração."},
    11: {"nome": "Vara de Pesca", "emoji": "🎣", "categoria": "Acessórios", "tipo": "acessorio", "preco": 350_000,
         "linhas": ["Pesca"], "bonus": 0.10, "descricao": "+10% em pesca."},
    12: {"nome": "Espada", "emoji": "⚔️", "categoria": "Acessórios", "tipo": "acessorio", "preco": 350_000,
         "linhas": ["Caça", "Raid"], "bonus": 0.10, "descricao": "+10% em caça e raid."},
    13: {"nome": "Lupa", "emoji": "🔎", "categoria": "Acessórios", "tipo": "acessorio", "preco": 350_000,
         "linhas": ["Exploração"], "bonus": 0.10, "descricao": "+10% em exploração."},
    14: {"nome": "Maleta", "emoji": "💼", "categoria": "Acessórios", "tipo": "acessorio", "preco": 350_000,
         "linhas": ["Trabalho"], "bonus": 0.10, "descricao": "+10% em trabalho."},

    20: {"nome": "Bilhete Premium", "emoji": "🎟️", "categoria": "Diários", "tipo": "diario", "preco": 900,
         "limite_diario": 2, "descricao": "Adiciona 1 bilhete premium."},
    21: {"nome": "Energético", "emoji": "⚡", "categoria": "Diários", "tipo": "diario", "preco": 1_500,
         "limite_diario": 2, "descricao": f"Recupera {ENERGETICO_VALOR} energia."},

    30: {"nome": "Poção de XP", "emoji": "🧪", "categoria": "Poções", "tipo": "pocao", "preco": 15_000,
         "buff": "xp", "duracao": 30 * 60, "descricao": "+50% XP por 30 minutos."},
    31: {"nome": "Poção de Sorte", "emoji": "🍀", "categoria": "Poções", "tipo": "pocao", "preco": 25_000,
         "buff": "sorte", "duracao": 20 * 60, "descricao": "+10% recompensa por 20 minutos."},
    32: {"nome": "Poção Shiny", "emoji": "✨", "categoria": "Poções", "tipo": "pocao", "preco": 75_000,
         "buff": "shiny", "duracao": 0, "descricao": "+5% de chance Shiny no próximo gacha."},
    33: {"nome": "Anti-Podre", "emoji": "🛡️", "categoria": "Poções", "tipo": "pocao", "preco": 35_000,
         "buff": "anti_podre", "duracao": 0, "descricao": "Impede Podre no próximo gacha."},
    34: {"nome": "Poção de Força", "emoji": "💪", "categoria": "Poções", "tipo": "pocao", "preco": 40_000,
         "buff": "forca", "duracao": 0, "descricao": "+15% dano na próxima raid."},

    100: {"nome": "Pedra Brilhante", "emoji": "🔹", "categoria": "Tesouros", "tipo": "tesouro", "preco": 0,
          "valor_venda": 250, "descricao": "Tesouro de venda."},
    101: {"nome": "Cristal Raro", "emoji": "💎", "categoria": "Tesouros", "tipo": "tesouro", "preco": 0,
          "valor_venda": 700, "descricao": "Tesouro de venda."},
    102: {"nome": "Pérola Negra", "emoji": "⚫", "categoria": "Tesouros", "tipo": "tesouro", "preco": 0,
          "valor_venda": 900, "descricao": "Tesouro de venda."},
    103: {"nome": "Relíquia Perdida", "emoji": "🏺", "categoria": "Tesouros", "tipo": "tesouro", "preco": 0,
          "valor_venda": 1_500, "descricao": "Tesouro de venda."},
    104: {"nome": "Escama Dourada", "emoji": "🟡", "categoria": "Tesouros", "tipo": "tesouro", "preco": 0,
          "valor_venda": 1_200, "descricao": "Tesouro de venda."},
}

CATEGORIAS_LOJA = ["Únicos", "Acessórios", "Diários", "Poções", "Tesouros"]

ACESSORIOS_POR_LINHA = {
    "Mineração": [10],
    "Pesca": [11],
    "Caça": [12],
    "Raid": [12],
    "Exploração": [13],
    "Trabalho": [14],
}

DROPS_ATIVIDADES = {
    "pesca": [(100, 1.20), (102, 0.35), (104, 0.45), (20, 0.25), (21, 0.45), (31, 0.15)],
    "mineracao": [(100, 1.50), (101, 0.60), (103, 0.20), (21, 0.35), (30, 0.15)],
    "caca": [(21, 0.35), (34, 0.18), (103, 0.20), (100, 0.70)],
    "exploracao": [(20, 0.35), (30, 0.20), (31, 0.25), (32, 0.04), (33, 0.08), (103, 0.45)],
    "trabalho": [(100, 0.60), (21, 0.25), (20, 0.10)],
}

DROPS_RAID = [(20, 3.0), (21, 4.0), (30, 2.0), (31, 2.0), (32, 0.5), (33, 0.8), (34, 2.0), (101, 4.0), (103, 2.0), (104, 2.0)]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ============================================================
# MODO MANUTENÇÃO
# ============================================================
# Quando ativo, comandos comuns ficam bloqueados para evitar uso
# durante restaurações de backup ou manutenção do banco.
MODO_MANUTENCAO = False

def modo_manutencao_ativo() -> bool:
    return MODO_MANUTENCAO

def definir_modo_manutencao(valor: bool):
    global MODO_MANUTENCAO
    MODO_MANUTENCAO = bool(valor)


# ============================================================
# BANCO DE DADOS PERSISTENTE E BACKUP AUTOMÁTICO
# ============================================================
# IMPORTANTE:
# O banco agora fica fora da pasta do código.
# Assim, quando você baixar uma versão nova do bot ou fechar o VSCode,
# os pets, Cristais, itens e progresso dos jogadores NÃO somem.

BASE_DADOS_DIR = r"C:\Users\zdani\Documents\Cristal\CristalBackup\dados"
BASE_BACKUPS_DIR = r"C:\Users\zdani\Documents\Cristal\CristalBackup\backups"
DB_PATH = os.path.join(BASE_DADOS_DIR, "cristal.db")

os.makedirs(BASE_DADOS_DIR, exist_ok=True)
os.makedirs(BASE_BACKUPS_DIR, exist_ok=True)


def migrar_banco_local_se_precisar():
    """
    Se existir um cristal.db antigo na pasta do bot e ainda não existir
    o banco fixo em CristalBackup/dados, copia o antigo automaticamente.
    Isso evita perder dados na primeira atualização com banco fixo.
    """
    banco_local = os.path.abspath("cristal.db")

    if os.path.exists(DB_PATH):
        return

    if os.path.exists(banco_local):
        shutil.copy2(banco_local, DB_PATH)
        print(f"Banco antigo copiado para: {DB_PATH}")


def criar_backup_banco():
    """
    Cria backup automático do banco ao iniciar o bot.
    Mantém os 20 backups mais recentes para não encher a pasta.
    """
    if not os.path.exists(DB_PATH):
        return

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = os.path.join(BASE_BACKUPS_DIR, f"cristal_backup_{agora}.db")
    shutil.copy2(DB_PATH, destino)

    backups = sorted(
        [os.path.join(BASE_BACKUPS_DIR, nome) for nome in os.listdir(BASE_BACKUPS_DIR) if nome.endswith(".db")],
        key=os.path.getmtime,
        reverse=True
    )

    for antigo in backups[20:]:
        try:
            os.remove(antigo)
        except OSError:
            pass


migrar_banco_local_se_precisar()
criar_backup_banco()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,
    cristais INTEGER DEFAULT 0,
    bilhetes INTEGER DEFAULT 0,
    ultimo_diario INTEGER DEFAULT 0,
    streak_diario INTEGER DEFAULT 0,
    semanas_diario INTEGER DEFAULT 0,
    slots_pets INTEGER DEFAULT 1,
    energia INTEGER DEFAULT 100,
    ultima_energia INTEGER DEFAULT 0,
    profissao TEXT DEFAULT '',
    ultima_troca_profissao INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    raridade TEXT NOT NULL,
    linha TEXT NOT NULL,
    emoji TEXT DEFAULT '🐾',
    mutacao TEXT DEFAULT 'Normal',
    evolucao TEXT DEFAULT 'Normal',
    nivel INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    trancado INTEGER DEFAULT 0,
    equipado INTEGER DEFAULT 0,
    favoritado INTEGER DEFAULT 0,
    criado_em INTEGER NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS raids (
    raid_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    boss_nome TEXT NOT NULL,
    boss_linha TEXT NOT NULL,
    boss_emoji TEXT DEFAULT '👹',
    raridade TEXT DEFAULT 'Mítico',
    mutacao TEXT DEFAULT 'Corrompido',
    inicio INTEGER NOT NULL,
    fim INTEGER NOT NULL,
    ativa INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS raid_participantes (
    raid_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    dano INTEGER DEFAULT 0,
    recompensa INTEGER DEFAULT 0,
    PRIMARY KEY (raid_id, user_id)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS inventario_itens (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantidade INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS compras_diarias (
    user_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    data TEXT NOT NULL,
    quantidade INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, item_id, data)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS buffs_ativos (
    user_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    fim INTEGER DEFAULT 0,
    criado_em INTEGER NOT NULL,
    PRIMARY KEY (user_id, tipo)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS eventos_ativos (
    guild_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    nome TEXT NOT NULL,
    chave_profissao TEXT DEFAULT '',
    inicio INTEGER NOT NULL,
    fim INTEGER NOT NULL,
    ativo INTEGER DEFAULT 1,
    PRIMARY KEY (guild_id, tipo, chave_profissao)
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS missoes_jogador (
    user_id INTEGER NOT NULL,
    periodo TEXT NOT NULL,
    chave_periodo TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    progresso INTEGER DEFAULT 0,
    coletada INTEGER DEFAULT 0,
    criado_em INTEGER NOT NULL,
    PRIMARY KEY (user_id, periodo, chave_periodo)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS missoes_reroll (
    user_id INTEGER NOT NULL,
    periodo TEXT NOT NULL,
    ultimo_reroll INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, periodo)
)
""")


def adicionar_coluna_se_nao_existir(tabela: str, nome_coluna: str, tipo_coluna: str, valor_padrao):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    if nome_coluna not in colunas:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {nome_coluna} {tipo_coluna} DEFAULT {valor_padrao}"
        )


adicionar_coluna_se_nao_existir("usuarios", "bilhetes", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "streak_diario", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "semanas_diario", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "slots_pets", "INTEGER", 1)
adicionar_coluna_se_nao_existir("usuarios", "energia", "INTEGER", ENERGIA_MAXIMA)
adicionar_coluna_se_nao_existir("usuarios", "ultima_energia", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "profissao", "TEXT", "''")
adicionar_coluna_se_nao_existir("usuarios", "ultima_troca_profissao", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "xpshare_pet_id", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "ultimo_uso_pocao", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "cassino_animal_ultimo", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "cassino_animal_data", "TEXT", "''")
adicionar_coluna_se_nao_existir("usuarios", "cassino_animal_acertos", "INTEGER", 0)
adicionar_coluna_se_nao_existir("usuarios", "cassino_pago_ultimo", "INTEGER", 0)
adicionar_coluna_se_nao_existir("pets", "favoritado", "INTEGER", 0)

conn.commit()


def criar_usuario(user_id: int):
    agora = int(time.time())
    cursor.execute(
        """
        INSERT OR IGNORE INTO usuarios
        (user_id, energia, ultima_energia)
        VALUES (?, ?, ?)
        """,
        (user_id, ENERGIA_MAXIMA, agora)
    )
    conn.commit()


def atualizar_energia(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT energia, ultima_energia FROM usuarios WHERE user_id = ?", (user_id,))
    energia, ultima_energia = cursor.fetchone()

    agora = int(time.time())

    if ultima_energia == 0:
        cursor.execute(
            "UPDATE usuarios SET ultima_energia = ? WHERE user_id = ?",
            (agora, user_id)
        )
        conn.commit()
        return energia

    minutos = (agora - ultima_energia) // 60

    if minutos <= 0:
        return energia

    nova_energia = min(ENERGIA_MAXIMA, energia + minutos * ENERGIA_POR_MINUTO)

    cursor.execute(
        "UPDATE usuarios SET energia = ?, ultima_energia = ? WHERE user_id = ?",
        (nova_energia, agora, user_id)
    )
    conn.commit()

    return nova_energia


def gastar_energia(user_id: int, quantidade: int):
    energia = atualizar_energia(user_id)

    if energia < quantidade:
        return False, energia

    cursor.execute(
        "UPDATE usuarios SET energia = energia - ? WHERE user_id = ?",
        (quantidade, user_id)
    )
    conn.commit()

    return True, energia - quantidade


def obter_dados(user_id: int):
    criar_usuario(user_id)
    atualizar_energia(user_id)
    cursor.execute("""
        SELECT cristais, bilhetes, ultimo_diario, streak_diario, semanas_diario, slots_pets, energia
        FROM usuarios
        WHERE user_id = ?
    """, (user_id,))
    return cursor.fetchone()


def obter_saldo(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT cristais FROM usuarios WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]


def usuario_e_booster(membro) -> bool:
    """Retorna True se o membro estiver dando boost no servidor."""
    return bool(getattr(membro, "premium_since", None))


def obter_slots_base(user_id: int) -> int:
    criar_usuario(user_id)
    cursor.execute("SELECT slots_pets FROM usuarios WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return 1
    return row[0]


def obter_slots_totais(membro) -> int:
    """Slots comprados/base + 1 slot temporário para Server Booster."""
    base_slots = obter_slots_base(membro.id)
    bonus_booster = 1 if usuario_e_booster(membro) else 0
    return base_slots + bonus_booster


def alterar_saldo(user_id: int, valor: int):
    criar_usuario(user_id)
    cursor.execute(
        "UPDATE usuarios SET cristais = MAX(0, cristais + ?) WHERE user_id = ?",
        (valor, user_id)
    )
    conn.commit()


def definir_saldo(user_id: int, valor: int):
    criar_usuario(user_id)
    cursor.execute(
        "UPDATE usuarios SET cristais = ? WHERE user_id = ?",
        (max(0, valor), user_id)
    )
    conn.commit()


def alterar_bilhetes(user_id: int, valor: int):
    criar_usuario(user_id)
    cursor.execute(
        "UPDATE usuarios SET bilhetes = MAX(0, bilhetes + ?) WHERE user_id = ?",
        (valor, user_id)
    )
    conn.commit()


def contar_pets(user_id: int):
    cursor.execute("SELECT COUNT(*) FROM pets WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0]


def obter_pet(user_id: int, pet_id: int):
    cursor.execute("""
        SELECT pet_id, nome, raridade, linha, emoji, mutacao, evolucao, nivel, xp, trancado, equipado, favoritado, criado_em
        FROM pets
        WHERE user_id = ? AND pet_id = ?
    """, (user_id, pet_id))
    return cursor.fetchone()


def criar_pet(user_id: int, pet: dict, mutacao: str):
    agora = int(time.time())

    cursor.execute("""
        INSERT INTO pets
        (user_id, nome, raridade, linha, emoji, mutacao, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        pet["nome"],
        pet["raridade"],
        pet["linha"],
        pet["emoji"],
        mutacao,
        agora
    ))

    conn.commit()
    return cursor.lastrowid


def criar_pet_manual(user_id: int, nome: str, raridade: str, linha: str, emoji: str, mutacao: str, evolucao: str):
    agora = int(time.time())
    cursor.execute("""
        INSERT INTO pets
        (user_id, nome, raridade, linha, emoji, mutacao, evolucao, criado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, nome, raridade, linha, emoji, mutacao, evolucao, agora))
    conn.commit()
    return cursor.lastrowid


def mutacoes_lista(mutacao_texto: str):
    if not mutacao_texto or mutacao_texto == "Normal":
        return []
    return [m.strip() for m in mutacao_texto.split(",") if m.strip() and m.strip() != "Normal"]


def juntar_mutacoes(pets_selecionados, limite: int):
    prioridade = ["Shiny", "Anjo", "Demônio", "Podre"]
    encontradas = []

    for pet in pets_selecionados:
        mutacao = pet[5]
        for item in mutacoes_lista(mutacao):
            if item not in encontradas:
                encontradas.append(item)

    ordenadas = sorted(encontradas, key=lambda m: prioridade.index(m) if m in prioridade else 999)
    finais = ordenadas[:limite]
    return ", ".join(finais) if finais else "Normal"


def escolher_raridade(chances: dict):
    raridades = list(chances.keys())
    pesos = list(chances.values())
    return random.choices(raridades, weights=pesos, k=1)[0]


def escolher_pet_por_raridade(raridade: str):
    opcoes = [pet for pet in PETS if pet["raridade"] == raridade]
    return random.choice(opcoes)


def escolher_mutacao(user_id: int | None = None):
    # Chance total inicial de mutação: 10%.
    # Poções de gacha são consumidas no próximo gacha.
    mutacoes = ["Normal", "Shiny", "Anjo", "Demônio", "Podre"]
    pesos = [90, 3, 2, 2, 3]

    if user_id is not None:
        if buff_ativo(user_id, "anti_podre"):
            # Remove Podre e redistribui para Normal.
            pesos = [93, 3, 2, 2, 0]
        if buff_ativo(user_id, "shiny"):
            # +5% Shiny no próximo gacha.
            pesos = [85, 8, 2, 2, 3 if not buff_ativo(user_id, "anti_podre") else 0]

    resultado = random.choices(mutacoes, weights=pesos, k=1)[0]

    if user_id is not None:
        consumir_buff(user_id, "shiny")
        consumir_buff(user_id, "anti_podre")

    return resultado



def item_info(item_id: int):
    return ITENS_LOJA.get(item_id)


def quantidade_item(user_id: int, item_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT quantidade FROM inventario_itens WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    row = cursor.fetchone()
    return row[0] if row else 0


def adicionar_item(user_id: int, item_id: int, quantidade: int = 1):
    if quantidade <= 0:
        return
    criar_usuario(user_id)
    cursor.execute("""
        INSERT INTO inventario_itens (user_id, item_id, quantidade)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_id)
        DO UPDATE SET quantidade = quantidade + excluded.quantidade
    """, (user_id, item_id, quantidade))
    conn.commit()


def remover_item(user_id: int, item_id: int, quantidade: int = 1):
    atual = quantidade_item(user_id, item_id)
    if atual < quantidade:
        return False
    novo = atual - quantidade
    if novo <= 0:
        cursor.execute("DELETE FROM inventario_itens WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    else:
        cursor.execute("UPDATE inventario_itens SET quantidade = ? WHERE user_id = ? AND item_id = ?", (novo, user_id, item_id))
    conn.commit()
    return True


def possui_item(user_id: int, item_id: int):
    return quantidade_item(user_id, item_id) > 0


def hoje_str():
    return time.strftime("%Y-%m-%d", time.localtime())


def compras_diarias_item(user_id: int, item_id: int):
    cursor.execute("""
        SELECT quantidade FROM compras_diarias
        WHERE user_id = ? AND item_id = ? AND data = ?
    """, (user_id, item_id, hoje_str()))
    row = cursor.fetchone()
    return row[0] if row else 0


def registrar_compra_diaria(user_id: int, item_id: int, quantidade: int):
    cursor.execute("""
        INSERT INTO compras_diarias (user_id, item_id, data, quantidade)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, item_id, data)
        DO UPDATE SET quantidade = quantidade + excluded.quantidade
    """, (user_id, item_id, hoje_str(), quantidade))
    conn.commit()


def buff_ativo(user_id: int, tipo: str):
    agora = int(time.time())
    cursor.execute("SELECT fim FROM buffs_ativos WHERE user_id = ? AND tipo = ?", (user_id, tipo))
    row = cursor.fetchone()
    if not row:
        return False
    fim = row[0]
    if fim == 0:
        return True
    if fim > agora:
        return True
    cursor.execute("DELETE FROM buffs_ativos WHERE user_id = ? AND tipo = ?", (user_id, tipo))
    conn.commit()
    return False


def tempo_buff_restante(user_id: int, tipo: str):
    agora = int(time.time())
    cursor.execute("SELECT fim FROM buffs_ativos WHERE user_id = ? AND tipo = ?", (user_id, tipo))
    row = cursor.fetchone()
    if not row:
        return 0
    fim = row[0]
    if fim == 0:
        return -1
    return max(0, fim - agora)


def ativar_buff(user_id: int, tipo: str, duracao: int = 0):
    agora = int(time.time())
    fim = 0 if duracao <= 0 else agora + duracao
    cursor.execute("""
        INSERT INTO buffs_ativos (user_id, tipo, fim, criado_em)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, tipo)
        DO UPDATE SET fim = excluded.fim, criado_em = excluded.criado_em
    """, (user_id, tipo, fim, agora))
    cursor.execute("UPDATE usuarios SET ultimo_uso_pocao = ? WHERE user_id = ?", (agora, user_id))
    conn.commit()


def consumir_buff(user_id: int, tipo: str):
    cursor.execute("DELETE FROM buffs_ativos WHERE user_id = ? AND tipo = ?", (user_id, tipo))
    conn.commit()


def cooldown_pocao_restante(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT ultimo_uso_pocao FROM usuarios WHERE user_id = ?", (user_id,))
    ultimo = cursor.fetchone()[0]
    restante = COOLDOWN_USO_POCAO - (int(time.time()) - ultimo)
    return max(0, restante)


def bonus_acessorio_linha(user_id: int, linha_bonus: str):
    total = 0.0
    detalhes = []
    for item_id in ACESSORIOS_POR_LINHA.get(linha_bonus, []):
        if possui_item(user_id, item_id):
            item = ITENS_LOJA[item_id]
            bonus = item.get("bonus", 0)
            total += bonus
            detalhes.append(f"{item['emoji']} {item['nome']} ({bonus * 100:.1f}%)")
    return total, detalhes


def bonus_recompensa_sorte(user_id: int):
    return 0.10 if buff_ativo(user_id, "sorte") else 0.0


def cooldown_cassino_pago_restante(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT cassino_pago_ultimo FROM usuarios WHERE user_id = ?", (user_id,))
    ultimo = cursor.fetchone()[0]
    restante = CASSINO_COOLDOWN_PAGO - (int(time.time()) - ultimo)
    return max(0, restante)


def registrar_cassino_pago(user_id: int):
    criar_usuario(user_id)
    cursor.execute("UPDATE usuarios SET cassino_pago_ultimo = ? WHERE user_id = ?", (int(time.time()), user_id))
    conn.commit()


def cooldown_cassino_animal_restante(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT cassino_animal_ultimo FROM usuarios WHERE user_id = ?", (user_id,))
    ultimo = cursor.fetchone()[0]
    restante = CASSINO_ANIMAL_COOLDOWN - (int(time.time()) - ultimo)
    return max(0, restante)


def registrar_tentativa_animal(user_id: int):
    criar_usuario(user_id)
    cursor.execute("UPDATE usuarios SET cassino_animal_ultimo = ? WHERE user_id = ?", (int(time.time()), user_id))
    conn.commit()


def acertos_animal_hoje(user_id: int):
    criar_usuario(user_id)
    hoje = hoje_str()
    cursor.execute("SELECT cassino_animal_data, cassino_animal_acertos FROM usuarios WHERE user_id = ?", (user_id,))
    data, acertos = cursor.fetchone()
    if data != hoje:
        cursor.execute("UPDATE usuarios SET cassino_animal_data = ?, cassino_animal_acertos = 0 WHERE user_id = ?", (hoje, user_id))
        conn.commit()
        return 0
    return acertos


def registrar_acerto_animal(user_id: int):
    criar_usuario(user_id)
    hoje = hoje_str()
    acertos = acertos_animal_hoje(user_id) + 1
    cursor.execute("UPDATE usuarios SET cassino_animal_data = ?, cassino_animal_acertos = ? WHERE user_id = ?", (hoje, acertos, user_id))
    conn.commit()
    return acertos


def normalizar_texto(valor: str):
    import unicodedata
    valor = valor.lower().strip()
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(ch for ch in valor if not unicodedata.combining(ch))
    valor = valor.replace("-", " ")
    return " ".join(valor.split())


def escolher_animal_cassino():
    return random.choice(PETS)


def bonus_xp_pocao(user_id: int):
    return 0.50 if buff_ativo(user_id, "xp") else 0.0


def bonus_forca_raid(user_id: int):
    return 0.15 if buff_ativo(user_id, "forca") else 0.0


def escolher_drop(lista_drops):
    # Cada entrada possui chance independente em porcentagem.
    encontrados = []
    for item_id, chance in lista_drops:
        if random.random() * 100 < chance:
            encontrados.append(item_id)
    return encontrados


def gerar_drops_atividade(user_id: int, chave_profissao: str, multiplicador: float = 1.0):
    drops_base = DROPS_ATIVIDADES.get(chave_profissao, [])
    drops_ajustados = [(item_id, chance * multiplicador) for item_id, chance in drops_base]
    encontrados = escolher_drop(drops_ajustados)
    mensagens = []
    for item_id in encontrados:
        adicionar_item(user_id, item_id, 1)
        item = ITENS_LOJA[item_id]
        mensagens.append(f"{item['emoji']} **{item['nome']} #{item_id}**")
    return mensagens


def gerar_drops_raid(user_id: int):
    encontrados = escolher_drop(DROPS_RAID)
    mensagens = []
    for item_id in encontrados:
        adicionar_item(user_id, item_id, 1)
        item = ITENS_LOJA[item_id]
        mensagens.append(f"{item['emoji']} **{item['nome']} #{item_id}**")
    return mensagens


def canal_por_chave(guild: discord.Guild, chave: str):
    if guild is None:
        return None

    canal_id = CANAIS.get(chave)
    if canal_id:
        canal = guild.get_channel(canal_id)
        if canal:
            return canal

    # Fallback por nome, útil durante testes em outro servidor.
    return discord.utils.get(guild.text_channels, name=chave)


def nome_canal(chave: str):
    canal_id = CANAIS.get(chave)
    if canal_id:
        return f"<#{canal_id}>"
    return f"#{chave}"


def chave_canal_profissao(chave_profissao: str):
    if chave_profissao == "raid":
        return "raid"
    config = PROFISSOES.get(chave_profissao)
    return config["canal"] if config else chave_profissao


def evento_ativo(guild_id: int, chave_profissao: str):
    agora = int(time.time())
    cursor.execute("""
        SELECT nome, fim
        FROM eventos_ativos
        WHERE guild_id = ? AND chave_profissao = ? AND ativo = 1
        ORDER BY fim DESC
        LIMIT 1
    """, (guild_id, chave_profissao))
    row = cursor.fetchone()

    if not row:
        return None

    nome, fim = row
    if fim <= agora:
        cursor.execute(
            "UPDATE eventos_ativos SET ativo = 0 WHERE guild_id = ? AND chave_profissao = ?",
            (guild_id, chave_profissao)
        )
        conn.commit()
        return None

    return {"nome": nome, "fim": fim}


def iniciar_evento_profissao(guild_id: int, chave_profissao: str, nome: str, duracao: int = MINI_EVENTO_DURACAO):
    agora = int(time.time())
    fim = agora + duracao
    cursor.execute("""
        INSERT INTO eventos_ativos (guild_id, tipo, nome, chave_profissao, inicio, fim, ativo)
        VALUES (?, 'profissao', ?, ?, ?, ?, 1)
        ON CONFLICT(guild_id, tipo, chave_profissao)
        DO UPDATE SET nome = excluded.nome,
                      inicio = excluded.inicio,
                      fim = excluded.fim,
                      ativo = 1
    """, (guild_id, nome, chave_profissao, agora, fim))
    conn.commit()
    return fim


def encerrar_evento_profissao(guild_id: int, chave_profissao: str):
    cursor.execute("""
        UPDATE eventos_ativos
        SET ativo = 0
        WHERE guild_id = ? AND tipo = 'profissao' AND chave_profissao = ?
    """, (guild_id, chave_profissao))
    conn.commit()


def listar_eventos_ativos(guild_id: int):
    agora = int(time.time())
    cursor.execute("""
        SELECT nome, chave_profissao, fim
        FROM eventos_ativos
        WHERE guild_id = ? AND ativo = 1 AND fim > ?
        ORDER BY fim ASC
    """, (guild_id, agora))
    return cursor.fetchall()


EVENTOS_PROFISSAO = {
    "pesca": {
        "nome": "Abundância de Peixes",
        "mensagem": "🐟 **Abundância de peixes!**\nDurante um tempo, a pesca terá mais Cristais e maior chance de drops.\nUse **/pescar** aqui para aproveitar.",
    },
    "mineracao": {
        "nome": "Rocha Cristalizada",
        "mensagem": "💎 **Uma rocha cristalizada surgiu!**\nMineração está rendendo mais e com drops melhores por tempo limitado.\nUse **/minerar** aqui.",
    },
    "caca": {
        "nome": "Criaturas Agitadas",
        "mensagem": "🐺 **Criaturas raras apareceram!**\nCaça está com melhores recompensas por tempo limitado.\nUse **/cacar** aqui.",
    },
    "exploracao": {
        "nome": "Portal Misterioso",
        "mensagem": "🗺️ **Um portal misterioso foi encontrado!**\nExploração está com melhores drops por tempo limitado.\nUse **/explorar** aqui.",
    },
    "trabalho": {
        "nome": "Oportunidade Especial",
        "mensagem": "💼 **Uma oportunidade rara de trabalho surgiu!**\nTrabalho está pagando melhor por tempo limitado.\nUse **/trabalhar** aqui.",
    },
}


async def anunciar_evento_profissao(guild: discord.Guild, chave_profissao: str, duracao: int = MINI_EVENTO_DURACAO):
    dados = EVENTOS_PROFISSAO.get(chave_profissao)
    config = PROFISSOES.get(chave_profissao)

    if not dados or not config:
        return None

    fim = iniciar_evento_profissao(guild.id, chave_profissao, dados["nome"], duracao)
    canal = canal_por_chave(guild, config["canal"])
    minutos = duracao // 60
    texto = f"{dados['mensagem']}\n\n⏳ Duração: **{minutos} minutos**."

    if canal:
        await canal.send(texto)
    else:
        await enviar_log(guild, f"⚠️ Não achei o canal público do evento **{dados['nome']}**.\n{texto}")

    return fim



# =========================
# MISSÕES
# =========================
COOLDOWN_REROLL_MISSAO = 24 * 60 * 60

MISSOES = {
    # Diárias - simples
    "d_msg_50": {"periodo": "diaria", "tipo": "mensagem", "nome": "Conversador", "descricao": "Envie 50 mensagens no servidor.", "objetivo": 50, "cs": 800, "bilhetes": 0, "raridade": "Comum"},
    "d_atividade_5": {"periodo": "diaria", "tipo": "atividade", "nome": "Rotina Produtiva", "descricao": "Conclua 5 atividades de profissão.", "objetivo": 5, "cs": 700, "bilhetes": 0, "raridade": "Comum"},
    "d_pesca_3": {"periodo": "diaria", "tipo": "pesca", "nome": "Pescaria Rápida", "descricao": "Use /pescar 3 vezes.", "objetivo": 3, "cs": 650, "bilhetes": 0, "raridade": "Comum"},
    "d_gacha_2": {"periodo": "diaria", "tipo": "gacha", "nome": "Invocador Iniciante", "descricao": "Abra 2 gachas.", "objetivo": 2, "cs": 900, "bilhetes": 0, "raridade": "Raro"},
    "d_cassino_5": {"periodo": "diaria", "tipo": "cassino", "nome": "Noite de Sorte", "descricao": "Jogue 5 vezes no cassino.", "objetivo": 5, "cs": 800, "bilhetes": 0, "raridade": "Comum"},
    "d_drop_1": {"periodo": "diaria", "tipo": "drop", "nome": "Achado do Dia", "descricao": "Consiga 1 drop raro em atividades.", "objetivo": 1, "cs": 1000, "bilhetes": 0, "raridade": "Raro"},
    "d_diario_1": {"periodo": "diaria", "tipo": "diario", "nome": "Presença Garantida", "descricao": "Colete sua recompensa diária.", "objetivo": 1, "cs": 500, "bilhetes": 0, "raridade": "Comum"},

    # Semanais - medianas
    "s_msg_500": {"periodo": "semanal", "tipo": "mensagem", "nome": "Ativo da Semana", "descricao": "Envie 500 mensagens no servidor.", "objetivo": 500, "cs": 6500, "bilhetes": 1, "raridade": "Épico"},
    "s_atividade_50": {"periodo": "semanal", "tipo": "atividade", "nome": "Trabalhador Constante", "descricao": "Conclua 50 atividades de profissão.", "objetivo": 50, "cs": 7000, "bilhetes": 1, "raridade": "Épico"},
    "s_raid_3": {"periodo": "semanal", "tipo": "raid", "nome": "Participante de Raids", "descricao": "Participe de 3 raids.", "objetivo": 3, "cs": 7500, "bilhetes": 1, "raridade": "Épico"},
    "s_gacha_20": {"periodo": "semanal", "tipo": "gacha", "nome": "Colecionador Semanal", "descricao": "Abra 20 gachas.", "objetivo": 20, "cs": 8000, "bilhetes": 1, "raridade": "Épico"},
    "s_cassino_win_10": {"periodo": "semanal", "tipo": "cassino_win", "nome": "Sorte Persistente", "descricao": "Ganhe 10 apostas no cassino.", "objetivo": 10, "cs": 7500, "bilhetes": 1, "raridade": "Épico"},
    "s_drops_10": {"periodo": "semanal", "tipo": "drop", "nome": "Caçador de Tesouros", "descricao": "Consiga 10 drops raros.", "objetivo": 10, "cs": 9000, "bilhetes": 1, "raridade": "Épico"},

    # Mensais - difíceis
    "m_msg_2000": {"periodo": "mensal", "tipo": "mensagem", "nome": "Lenda do Chat", "descricao": "Envie 2000 mensagens no servidor.", "objetivo": 2000, "cs": 40000, "bilhetes": 3, "raridade": "Lendário"},
    "m_equip_lendario": {"periodo": "mensal", "tipo": "equip_lendario", "nome": "Poder Lendário", "descricao": "Equipe um pet Lendário.", "objetivo": 1, "cs": 35000, "bilhetes": 2, "raridade": "Lendário"},
    "m_equip_mitico": {"periodo": "mensal", "tipo": "equip_mitico", "nome": "Força Mítica", "descricao": "Equipe um pet Mítico.", "objetivo": 1, "cs": 60000, "bilhetes": 4, "raridade": "Mítico"},
    "m_fundir_5": {"periodo": "mensal", "tipo": "fundir", "nome": "Alquimista de Pets", "descricao": "Faça 5 fusões de pets.", "objetivo": 5, "cs": 45000, "bilhetes": 3, "raridade": "Lendário"},
    "m_raid_dano_50000": {"periodo": "mensal", "tipo": "raid_dano", "nome": "Destruidor de Bosses", "descricao": "Cause 50.000 de dano total em raids.", "objetivo": 50000, "cs": 50000, "bilhetes": 3, "raridade": "Lendário"},
    "m_jackpot_1": {"periodo": "mensal", "tipo": "jackpot", "nome": "Jackpot Supremo", "descricao": "Acerte 1 jackpot de três animais iguais.", "objetivo": 1, "cs": 50000, "bilhetes": 3, "raridade": "Lendário"},
}

PERIODOS_MISSAO = ["diaria", "semanal", "mensal"]


def chave_periodo_atual(periodo: str):
    agora = datetime.now()
    if periodo == "diaria":
        return agora.strftime("%Y-%m-%d")
    if periodo == "semanal":
        ano, semana, _ = agora.isocalendar()
        return f"{ano}-W{semana:02d}"
    if periodo == "mensal":
        return agora.strftime("%Y-%m")
    return agora.strftime("%Y-%m-%d")


def missoes_por_periodo(periodo: str):
    return [mid for mid, dados in MISSOES.items() if dados["periodo"] == periodo]


def garantir_missao_usuario(user_id: int, periodo: str):
    criar_usuario(user_id)
    chave = chave_periodo_atual(periodo)
    cursor.execute("""
        SELECT mission_id, progresso, coletada
        FROM missoes_jogador
        WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
    """, (user_id, periodo, chave))
    row = cursor.fetchone()
    if row:
        return row

    mission_id = random.choice(missoes_por_periodo(periodo))
    cursor.execute("""
        INSERT INTO missoes_jogador (user_id, periodo, chave_periodo, mission_id, progresso, coletada, criado_em)
        VALUES (?, ?, ?, ?, 0, 0, ?)
    """, (user_id, periodo, chave, mission_id, int(time.time())))
    conn.commit()
    return (mission_id, 0, 0)


def garantir_todas_missoes(user_id: int):
    return {periodo: garantir_missao_usuario(user_id, periodo) for periodo in PERIODOS_MISSAO}


def obter_missoes_usuario(user_id: int):
    garantir_todas_missoes(user_id)
    resultado = []
    for periodo in PERIODOS_MISSAO:
        chave = chave_periodo_atual(periodo)
        cursor.execute("""
            SELECT mission_id, progresso, coletada
            FROM missoes_jogador
            WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
        """, (user_id, periodo, chave))
        row = cursor.fetchone()
        if row:
            resultado.append((periodo, *row))
    return resultado


def registrar_missao_evento(user_id: int, tipo: str, quantidade: int = 1):
    if not user_id or quantidade <= 0:
        return
    garantir_todas_missoes(user_id)
    for periodo in PERIODOS_MISSAO:
        chave = chave_periodo_atual(periodo)
        cursor.execute("""
            SELECT mission_id, progresso, coletada
            FROM missoes_jogador
            WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
        """, (user_id, periodo, chave))
        row = cursor.fetchone()
        if not row:
            continue
        mission_id, progresso, coletada = row
        missao = MISSOES.get(mission_id)
        if not missao or missao["tipo"] != tipo or coletada:
            continue
        novo = min(missao["objetivo"], progresso + quantidade)
        cursor.execute("""
            UPDATE missoes_jogador
            SET progresso = ?
            WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
        """, (novo, user_id, periodo, chave))
    conn.commit()


def coletar_missao_usuario(user_id: int, periodo: str):
    if periodo not in PERIODOS_MISSAO:
        return False, "❌ Período inválido."
    garantir_missao_usuario(user_id, periodo)
    chave = chave_periodo_atual(periodo)
    cursor.execute("""
        SELECT mission_id, progresso, coletada
        FROM missoes_jogador
        WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
    """, (user_id, periodo, chave))
    row = cursor.fetchone()
    if not row:
        return False, "❌ Missão não encontrada."
    mission_id, progresso, coletada = row
    missao = MISSOES[mission_id]
    if coletada:
        return False, "❌ Você já coletou essa missão."
    if progresso < missao["objetivo"]:
        return False, f"❌ Missão incompleta: **{progresso}/{missao['objetivo']}**."

    alterar_saldo(user_id, missao["cs"])
    if missao.get("bilhetes", 0) > 0:
        alterar_bilhetes(user_id, missao["bilhetes"])
    cursor.execute("""
        UPDATE missoes_jogador
        SET coletada = 1
        WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
    """, (user_id, periodo, chave))
    conn.commit()
    extra = f" e **{missao['bilhetes']} bilhete(s)**" if missao.get("bilhetes", 0) else ""
    return True, f"✅ Missão **{missao['nome']}** coletada! Você recebeu **{missao['cs']:,} {SIGLA}**{extra}."


def reroll_missao_usuario(user_id: int, periodo: str):
    if periodo not in PERIODOS_MISSAO:
        return False, "❌ Período inválido."
    garantir_missao_usuario(user_id, periodo)
    agora = int(time.time())
    cursor.execute("SELECT ultimo_reroll FROM missoes_reroll WHERE user_id = ? AND periodo = ?", (user_id, periodo))
    row = cursor.fetchone()
    ultimo = row[0] if row else 0
    restante = COOLDOWN_REROLL_MISSAO - (agora - ultimo)
    if restante > 0:
        horas = restante // 3600
        minutos = (restante % 3600) // 60
        return False, f"⏳ Você só pode trocar essa missão em **{horas}h {minutos}min**."

    chave = chave_periodo_atual(periodo)
    cursor.execute("""
        SELECT mission_id, coletada
        FROM missoes_jogador
        WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
    """, (user_id, periodo, chave))
    atual = cursor.fetchone()
    if atual and atual[1]:
        return False, "❌ Você já coletou essa missão. Espere o próximo período."
    atual_id = atual[0] if atual else None
    opcoes = [mid for mid in missoes_por_periodo(periodo) if mid != atual_id]
    novo_id = random.choice(opcoes or missoes_por_periodo(periodo))
    cursor.execute("""
        UPDATE missoes_jogador
        SET mission_id = ?, progresso = 0, coletada = 0, criado_em = ?
        WHERE user_id = ? AND periodo = ? AND chave_periodo = ?
    """, (novo_id, agora, user_id, periodo, chave))
    cursor.execute("""
        INSERT INTO missoes_reroll (user_id, periodo, ultimo_reroll)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, periodo)
        DO UPDATE SET ultimo_reroll = excluded.ultimo_reroll
    """, (user_id, periodo, agora))
    conn.commit()
    missao = MISSOES[novo_id]
    return True, f"🔁 Missão trocada! Nova missão: **{missao['nome']}** — {missao['descricao']}"


def texto_missao(periodo: str, mission_id: str, progresso: int, coletada: int):
    missao = MISSOES[mission_id]
    status = "✅ Coletada" if coletada else "🎁 Pronta" if progresso >= missao["objetivo"] else "⏳ Em progresso"
    extra = f" + {missao['bilhetes']} bilhete(s)" if missao.get("bilhetes", 0) else ""
    nomes_periodo = {"diaria": "Diária", "semanal": "Semanal", "mensal": "Mensal"}
    return (
        f"**{nomes_periodo.get(periodo, periodo.title())} — {missao['raridade']}**\n"
        f"**{missao['nome']}**\n"
        f"{missao['descricao']}\n"
        f"Progresso: **{progresso}/{missao['objetivo']}**\n"
        f"Recompensa: **{missao['cs']:,} {SIGLA}**{extra}\n"
        f"Status: {status}"
    )


def tem_permissao_admin(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        return True

    if hasattr(interaction.user, "roles"):
        for cargo in interaction.user.roles:
            if cargo.name == CARGO_ADMIN_BOT:
                return True

    return False


async def enviar_log(guild: discord.Guild, mensagem: str):
    if guild is None:
        return

    canal = canal_por_chave(guild, "logs") or discord.utils.get(guild.text_channels, name=CANAL_LOGS)

    if canal:
        await canal.send(mensagem)


def xp_necessario(nivel: int):
    return nivel * 100


def adicionar_xp_pets_equipados(user_id: int, linha_bonus: str, quantidade: int):
    """
    Dá XP aos pets equipados.
    - Pet da linha ideal ganha 100% do XP.
    - Pet equipado de outra linha ganha 75% do XP.
    - XP Share, se comprado e definido, dá 50% do XP final ao pet reserva.
    Retorna mensagens para mostrar ao jogador.
    """
    bonus_xp = bonus_xp_pocao(user_id)
    quantidade_final = max(1, int(quantidade * (1 + bonus_xp)))
    quantidade_parcial = max(1, int(quantidade_final * 0.75))

    cursor.execute("""
        SELECT pet_id, nome, emoji, nivel, xp, linha
        FROM pets
        WHERE user_id = ? AND equipado = 1
    """, (user_id,))
    pets = cursor.fetchall()

    mensagens = []
    pets_que_receberam = set()
    ideais = 0
    parciais = 0

    def aplicar_xp(pet_id: int, nome: str, emoji: str, nivel: int, xp: int, qtd: int):
        if nivel >= NIVEL_MAXIMO_PET:
            return
        novo_xp = xp + qtd
        novo_nivel = nivel
        while novo_nivel < NIVEL_MAXIMO_PET and novo_xp >= xp_necessario(novo_nivel):
            novo_xp -= xp_necessario(novo_nivel)
            novo_nivel += 1
            mensagens.append(f"🎉 {emoji} **{nome} #{pet_id}** subiu para o nível **{novo_nivel}**!")
        if novo_nivel >= NIVEL_MAXIMO_PET:
            novo_xp = 0
        cursor.execute(
            "UPDATE pets SET nivel = ?, xp = ? WHERE pet_id = ? AND user_id = ?",
            (novo_nivel, novo_xp, pet_id, user_id)
        )

    for pet_id, nome, emoji, nivel, xp, linha in pets:
        pets_que_receberam.add(pet_id)
        if linha == linha_bonus:
            ideais += 1
            aplicar_xp(pet_id, nome, emoji, nivel, xp, quantidade_final)
        else:
            parciais += 1
            aplicar_xp(pet_id, nome, emoji, nivel, xp, quantidade_parcial)

    # XP Share: pet reserva recebe 50% do XP final, se não recebeu XP por estar equipado.
    if possui_item(user_id, 1):
        cursor.execute("SELECT xpshare_pet_id FROM usuarios WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        xpshare_pet_id = row[0] if row else 0
        if xpshare_pet_id and xpshare_pet_id not in pets_que_receberam:
            cursor.execute("""
                SELECT pet_id, nome, emoji, nivel, xp
                FROM pets
                WHERE user_id = ? AND pet_id = ?
            """, (user_id, xpshare_pet_id))
            reserva = cursor.fetchone()
            if reserva:
                pet_id, nome, emoji, nivel, xp = reserva
                aplicar_xp(pet_id, nome, emoji, nivel, xp, max(1, quantidade_final // 2))
                mensagens.append(f"🔗 XP Share: {emoji} **{nome} #{pet_id}** recebeu **{max(1, quantidade_final // 2)} XP**.")

    conn.commit()

    resumo = []
    if ideais > 0:
        resumo.append(f"Pets da linha **{linha_bonus}** ganharam **{quantidade_final} XP**.")
    if parciais > 0:
        resumo.append(f"Pets de outras linhas ganharam **{quantidade_parcial} XP** (75%).")
    if bonus_xp > 0:
        resumo.append(f"🧪 Poção de XP ativa: XP base aumentado em **{bonus_xp * 100:.0f}%**.")

    return resumo + mensagens

def buscar_pet_base(nome: str):
    nome_busca = nome.strip().lower()
    for pet in PETS:
        if pet["nome"].lower() == nome_busca:
            return pet
    return None


def obter_raid_ativa(guild_id: int):
    agora = int(time.time())
    cursor.execute("""
        SELECT raid_id, boss_nome, boss_linha, boss_emoji, raridade, mutacao, inicio, fim
        FROM raids
        WHERE guild_id = ? AND ativa = 1
        ORDER BY raid_id DESC
        LIMIT 1
    """, (guild_id,))
    raid = cursor.fetchone()

    if not raid:
        return None

    # Se expirou, ainda retorna para permitir finalização automática.
    return raid


def escolher_boss_raid():
    miticos = [pet for pet in PETS if pet["raridade"] == "Mítico"]
    return random.choice(miticos)


async def finalizar_raid_por_id(guild: discord.Guild, raid_id: int):
    cursor.execute("""
        SELECT boss_nome, boss_linha, boss_emoji, raridade, mutacao
        FROM raids
        WHERE raid_id = ?
    """, (raid_id,))
    raid = cursor.fetchone()

    if not raid:
        return "❌ Raid não encontrada."

    boss_nome, boss_linha, boss_emoji, raridade, mutacao = raid

    cursor.execute("""
        SELECT user_id, dano
        FROM raid_participantes
        WHERE raid_id = ?
        ORDER BY dano DESC
    """, (raid_id,))
    participantes = cursor.fetchall()

    cursor.execute("UPDATE raids SET ativa = 0 WHERE raid_id = ?", (raid_id,))
    conn.commit()

    if not participantes:
        texto = (
            f"⚔️ **Raid encerrada!**\n"
            f"{boss_emoji} **{boss_nome} {mutacao}** desapareceu sem ser enfrentado."
        )
        await enviar_log(guild, texto)
        return texto

    linhas = []
    for posicao, (user_id, dano) in enumerate(participantes, start=1):
        recompensa = max(100, int(dano / 10))

        if posicao == 1:
            recompensa += 1000
        elif posicao == 2:
            recompensa += 600
        elif posicao == 3:
            recompensa += 300

        bonus_sorte = bonus_recompensa_sorte(user_id)
        if bonus_sorte > 0:
            recompensa = int(recompensa * (1 + bonus_sorte))

        drops = gerar_drops_raid(user_id)
        if drops:
            registrar_missao_evento(user_id, "drop", len(drops))
        alterar_saldo(user_id, recompensa)
        cursor.execute(
            "UPDATE raid_participantes SET recompensa = ? WHERE raid_id = ? AND user_id = ?",
            (recompensa, raid_id, user_id)
        )

        medalha = "🥇" if posicao == 1 else "🥈" if posicao == 2 else "🥉" if posicao == 3 else "▫️"
        drop_txt = f" — Drop: {', '.join(drops)}" if drops else ""
        linhas.append(f"{medalha} <@{user_id}> — **{dano:,} dano** — **{recompensa:,} {SIGLA}**{drop_txt}")

    conn.commit()

    texto = (
        f"🏆 **Raid finalizada!**\n"
        f"Boss: {boss_emoji} **{boss_nome} {mutacao}** — **{raridade}**\n\n"
        + "\n".join(linhas[:10])
    )

    await enviar_log(guild, texto)
    return texto


def calcular_bonus_linha(user_id: int, linha_bonus: str):
    cursor.execute("""
        SELECT nome, raridade, linha, emoji, mutacao, evolucao, nivel
        FROM pets
        WHERE user_id = ? AND equipado = 1 AND linha = ?
    """, (user_id, linha_bonus))
    pets_equipados = cursor.fetchall()

    bonus_total = 0.0
    detalhes = []

    for nome, raridade, linha, emoji, mutacao, evolucao, nivel in pets_equipados:
        bonus = MULTIPLICADOR_RARIDADE_BONUS.get(raridade, 0)
        bonus *= MULTIPLICADOR_EVOLUCAO_BONUS.get(evolucao, 1.0)

        # Cada nível acima do 1 adiciona +0.5% no bônus daquele pet.
        bonus += max(0, nivel - 1) * 0.005

        for item in mutacoes_lista(mutacao):
            bonus += MULTIPLICADOR_MUTACAO_BONUS.get(item, 0)

        bonus = max(0, bonus)
        bonus_total += bonus
        detalhes.append(f"{emoji} {nome} Nv.{nivel} ({bonus * 100:.1f}%)")

    bonus_acessorio, detalhes_acessorio = bonus_acessorio_linha(user_id, linha_bonus)
    bonus_total += bonus_acessorio
    detalhes.extend(detalhes_acessorio)

    return bonus_total, detalhes


def obter_profissao(user_id: int):
    criar_usuario(user_id)
    cursor.execute("SELECT profissao, ultima_troca_profissao FROM usuarios WHERE user_id = ?", (user_id,))
    return cursor.fetchone()


def canal_correto(interaction: discord.Interaction, canal_nome: str):
    if not interaction.channel:
        return False

    canal_id = CANAIS.get(canal_nome)
    if canal_id and interaction.channel.id == canal_id:
        return True

    return interaction.channel.name == canal_nome


async def validar_atividade(interaction: discord.Interaction, chave_profissao: str):
    config = PROFISSOES[chave_profissao]
    profissao_atual, _ = obter_profissao(interaction.user.id)

    if profissao_atual != chave_profissao:
        await interaction.response.send_message(
            f"❌ Você precisa ter a profissão **{config['nome']}** para usar este comando.\n"
            f"Use `/profissao escolher {chave_profissao}`.",
            ephemeral=True
        )
        return False

    if not canal_correto(interaction, config["canal"]):
        await interaction.response.send_message(
            f"❌ Use este comando no canal {nome_canal(config['canal'])}.",
            ephemeral=True
        )
        return False

    return True


async def executar_atividade(interaction: discord.Interaction, chave_profissao: str):
    config = PROFISSOES[chave_profissao]

    if not await validar_atividade(interaction, chave_profissao):
        return

    ok, energia_restante = gastar_energia(interaction.user.id, config["energia"])

    if not ok:
        await interaction.response.send_message(
            f"❌ Energia insuficiente.\n"
            f"Necessário: **{config['energia']}**\n"
            f"Sua energia: **{energia_restante}/{ENERGIA_MAXIMA}**",
            ephemeral=True
        )
        return

    ganho_base = random.randint(config["ganho_min"], config["ganho_max"])
    bonus, detalhes = calcular_bonus_linha(interaction.user.id, config["linha_bonus"])

    evento = evento_ativo(interaction.guild.id, chave_profissao) if interaction.guild else None
    multiplicador_evento = MINI_EVENTO_GANHO_MULT if evento else 1.0

    bonus_sorte = bonus_recompensa_sorte(interaction.user.id)
    bonus_total = bonus + bonus_sorte
    ganho_final = int(ganho_base * (1 + bonus_total) * multiplicador_evento)

    alterar_saldo(interaction.user.id, ganho_final)
    registrar_missao_evento(interaction.user.id, "atividade", 1)
    registrar_missao_evento(interaction.user.id, chave_profissao, 1)

    levelups = adicionar_xp_pets_equipados(interaction.user.id, config["linha_bonus"], XP_ATIVIDADE)
    drops = gerar_drops_atividade(
        interaction.user.id,
        chave_profissao,
        MINI_EVENTO_DROP_MULT if evento else 1.0
    )
    if drops:
        registrar_missao_evento(interaction.user.id, "drop", len(drops))

    detalhes_txt = "\n".join(detalhes) if detalhes else "Nenhum pet equipado da linha certa."
    if bonus_sorte > 0:
        detalhes_txt += f"\n🍀 Poção de Sorte ({bonus_sorte * 100:.1f}%)"
    if evento:
        detalhes_txt += f"\n✨ Evento ativo: {evento['nome']} (+{int((MINI_EVENTO_GANHO_MULT - 1) * 100)}% ganho, drops melhores)"

    xp_txt = "\n".join(levelups) if levelups else f"Pets da linha **{config['linha_bonus']}** equipados ganharam **{XP_ATIVIDADE} XP**."
    drops_txt = "\n".join(drops) if drops else "Nenhum drop raro desta vez."

    await interaction.response.send_message(
        f"{config['emoji']} **{config['nome']} concluído!**\n\n"
        f"Ganho base: **{ganho_base:,} {SIGLA}**\n"
        f"Bônus total: **{bonus_total * 100:.1f}%**\n"
        f"Total recebido: **{ganho_final:,} {SIGLA}**\n"
        f"Energia restante: **{energia_restante}/{ENERGIA_MAXIMA}**\n\n"
        f"Bônus considerados:\n{detalhes_txt}\n\n"
        f"XP:\n{xp_txt}\n\n"
        f"Drops:\n{drops_txt}"
    )

    await enviar_log(
        interaction.guild,
        f"{config['emoji']} **LOG DE ATIVIDADE**\n"
        f"Jogador: {interaction.user.mention}\n"
        f"Atividade: **{config['nome']}**\n"
        f"Ganho: **{ganho_final:,} {SIGLA}**\n"
        f"Bônus: **{bonus * 100:.1f}%**"
    )


def texto_chances(chances: dict):
    linhas = []
    for raridade, chance in chances.items():
        linhas.append(f"{raridade}: **{chance}%**")
    return "\n".join(linhas)


async def processar_abertura_gacha(interaction: discord.Interaction, tipo_gacha: str, pagamento_tipo: str):
    config = GACHAS[tipo_gacha]
    user_id = interaction.user.id
    criar_usuario(user_id)

    cristais, bilhetes, *_ = obter_dados(user_id)

    if pagamento_tipo == "bilhete":
        if tipo_gacha != "premium":
            await interaction.response.edit_message(content="❌ Bilhete só pode ser usado no Gacha Premium.", view=None)
            return
        if bilhetes <= 0:
            await interaction.response.edit_message(content="❌ Você não tem bilhetes premium.", view=None)
            return
        alterar_bilhetes(user_id, -1)
        pagamento = "1 bilhete"
    else:
        if cristais < config["custo"]:
            await interaction.response.edit_message(
                content=f"❌ Você não tem Cristais suficientes. Custo: **{config['custo']:,} {SIGLA}**.",
                view=None
            )
            return
        alterar_saldo(user_id, -config["custo"])
        pagamento = f"{config['custo']:,} {SIGLA}"

    raridade = escolher_raridade(config["chances"])
    pet = escolher_pet_por_raridade(raridade)
    mutacao = escolher_mutacao(user_id)
    pet_id = criar_pet(user_id, pet, mutacao)
    registrar_missao_evento(user_id, "gacha", 1)
    if pet["raridade"] == "Lendário":
        registrar_missao_evento(user_id, "gacha_lendario", 1)
    if pet["raridade"] == "Mítico":
        registrar_missao_evento(user_id, "gacha_mitico", 1)
    if mutacao != "Normal":
        registrar_missao_evento(user_id, "gacha_mutacao", 1)

    mutacao_txt = f"\nMutação: **{mutacao}**" if mutacao != "Normal" else "\nMutação: **Normal**"

    await interaction.response.edit_message(
        content=(
            f"🎉 **Gacha aberto!**\n\n"
            f"Você gastou: **{pagamento}**\n\n"
            f"{pet['emoji']} Você recebeu:\n"
            f"**{pet['nome']} #{pet_id}**\n"
            f"Raridade: **{pet['raridade']}**\n"
            f"Linha: **{pet['linha']}**"
            f"{mutacao_txt}"
        ),
        view=None
    )

    if pet["raridade"] in ["Lendário", "Mítico"] or mutacao in ["Shiny", "Anjo", "Demônio"]:
        await enviar_log(
            interaction.guild,
            f"🎲 **LOG DE GACHA**\n"
            f"Jogador: {interaction.user.mention}\n"
            f"Gacha: **{config['nome']}**\n"
            f"Resultado: **{pet['nome']} #{pet_id}**\n"
            f"Raridade: **{pet['raridade']}**\n"
            f"Mutação: **{mutacao}**"
        )


class ConfirmarGachaView(discord.ui.View):
    def __init__(self, user_id: int, tipo_gacha: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.tipo_gacha = tipo_gacha
        self.usado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "❌ Esse gacha não é seu.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", emoji="✅", style=discord.ButtonStyle.success)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Esse gacha já foi usado.", ephemeral=True)
            return
        self.usado = True
        await processar_abertura_gacha(interaction, self.tipo_gacha, "dinheiro")

    @discord.ui.button(label="Cancelar", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Esse gacha já foi usado.", ephemeral=True)
            return
        self.usado = True
        await interaction.response.edit_message(content="❌ Gacha cancelado.", view=None)


class PremiumGachaView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.usado = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Esse gacha não é seu.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Usar dinheiro", emoji="💎", style=discord.ButtonStyle.primary)
    async def dinheiro(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Esse gacha já foi usado.", ephemeral=True)
            return
        self.usado = True
        await processar_abertura_gacha(interaction, "premium", "dinheiro")

    @discord.ui.button(label="Usar bilhete", emoji="🎟️", style=discord.ButtonStyle.success)
    async def bilhete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Esse gacha já foi usado.", ephemeral=True)
            return
        self.usado = True
        await processar_abertura_gacha(interaction, "premium", "bilhete")

    @discord.ui.button(label="Cancelar", emoji="❌", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.usado:
            await interaction.response.send_message("❌ Esse gacha já foi usado.", ephemeral=True)
            return
        self.usado = True
        await interaction.response.edit_message(content="❌ Gacha cancelado.", view=None)


async def iniciar_gacha(interaction: discord.Interaction, tipo_gacha: str):
    config = GACHAS[tipo_gacha]
    criar_usuario(interaction.user.id)
    cristais, bilhetes, *_ = obter_dados(interaction.user.id)

    if tipo_gacha == "premium":
        custo_texto = f"{config['custo']:,} {SIGLA} ou 1 bilhete"
        view = PremiumGachaView(interaction.user.id)
        pergunta = "Escolha a forma de pagamento:"
    else:
        custo_texto = f"{config['custo']:,} {SIGLA}"
        view = ConfirmarGachaView(interaction.user.id, tipo_gacha)
        pergunta = "Confirmar abertura?"

    await interaction.response.send_message(
        f"🎲 **{config['nome']}**\n"
        f"Custo: **{custo_texto}**\n\n"
        f"Suas moedas: **{cristais:,} {SIGLA}**\n"
        f"Seus bilhetes: **{bilhetes}**\n\n"
        f"**Chances:**\n"
        f"{texto_chances(config['chances'])}\n\n"
        f"{pergunta}",
        view=view
    )


# ============================================================
# BLOQUEIO GLOBAL DURANTE MANUTENÇÃO
# ============================================================
@bot.tree.interaction_check
async def checar_manutencao_global(interaction: discord.Interaction) -> bool:
    if not modo_manutencao_ativo():
        return True

    nome_comando = ""
    if interaction.command:
        nome_comando = interaction.command.qualified_name or interaction.command.name

    # Comandos admin continuam liberados para permitir desligar manutenção,
    # importar backup, status, save, etc.
    if nome_comando.startswith("admin"):
        return True

    if not interaction.response.is_done():
        await interaction.response.send_message(
            "🛠️ **Cristal está em manutenção.** Tente novamente em alguns instantes."
        )
    return False
