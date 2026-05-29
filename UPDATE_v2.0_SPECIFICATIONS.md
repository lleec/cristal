# 🎮 CRISTAL BOT - ATUALIZAÇÃO v2.0
## Especificações Completas de Implementação

**Data:** Maio 2026  
**Versão:** 2.0  
**Status:** Pronto para Desenvolvimento

---

## 📋 INTRODUÇÃO

Este documento detalha TODAS as mudanças, adições e remoções necessárias para atualizar o bot Cristal de sua versão atual para a versão 2.0. Implementar seguindo este documento resultará em um bot extremamente divertido, balanceado e otimizado para retenção de jogadores.

---

## 🔄 FASE 1: RENOMEAÇÃO E CONFIGURAÇÃO

### **1.1 Renomear Comandos de Profissão**

**Objetivo:** Tornar os comandos mais intuitivos e universais.

**Mudanças:**

```
Comandos antigos → Novos comandos + Atalhos:

/cacar → /hunt (atalho: /h)
/pescar → /fish (atalho: /f)
/minerar → /mine (atalho: /m)
/explorar → /explore (atalho: /e)
/trabalhar → /work (atalho: /w)
/dia → /daily (atalho: /d)
/diario → /daily (atalho: /d)
```

**Implementação:**
- Renomear comandos em `commands/profissoes.py`
- Manter alias duplicados: **ambos funcionam**
  - `/hunt` E `/cacar` funcionam
  - `/fish` E `/pescar` funcionam
  - Assim veteranos não ficam confusos
- Adicionar atalhos `/h`, `/f`, `/m`, `/e`, `/w`, `/d`
- Atualizar descrição dos comandos
- Todos os comandos antigos continuam funcionando (sem breaking change)

**Arquivo afetado:** `commands/profissoes.py`

---

### **1.2 Sistema de Prefixo Secundário**

**Objetivo:** Permitir que admins definam um prefixo alternativo para evitar digitar `/` sempre.

**Mudanças:**

```
Nova tabela no banco:
├─ guild_id (PRIMARY KEY)
├─ secondary_prefix (TEXT, DEFAULT: vazio)
```

**Funcionamento:**

```
Admin configura:
/admin prefix .
/admin prefix !
/admin prefix cs

Resultado:
- Prefixo primário: / (sempre funciona)
- Prefixo secundário: . (customizável)

TODOS funcionam SIMULTANEAMENTE:
├─ /hunt = .hunt = !hunt = cs!hunt
├─ /h = .h = !h = cs!h
├─ /fish = .fish = !fish = cs!fish
└─ /daily = .daily = !daily = cs!daily

Reset:
/admin prefix reset (volta só /)
```

**Implementação:**
- Criar tabela `config_prefixo` no banco
- Adicionar comando `/admin prefix <prefixo>` (ex: `.`, `!`, `cs`)
- Modificar event listener de mensagens para reconhecer prefixo secundário
- Validar prefixo (apenas caracteres válidos)
- Armazenar por servidor (guild_id)

**Arquivo afetado:** `core.py`, `commands/admin.py`

---

### **1.3 Sistema de Canais Dinâmicos**

**Objetivo:** Permitir que cada servidor configure seus próprios canais sem editar código.

**Mudanças:**

```
Nova tabela no banco:
├─ guild_id (PRIMARY KEY)
├─ canal_hunt (INT, DEFAULT: 0)
├─ canal_fish (INT, DEFAULT: 0)
├─ canal_mine (INT, DEFAULT: 0)
├─ canal_explore (INT, DEFAULT: 0)
├─ canal_work (INT, DEFAULT: 0)
├─ canal_raid (INT, DEFAULT: 0)
├─ canal_gacha (INT, DEFAULT: 0)
├─ canal_duelo (INT, DEFAULT: 0)
├─ canal_logs (INT, DEFAULT: 0)
└─ canal_anuncios (INT, DEFAULT: 0)
```

**Funcionalidade:**

```
Admin configura:
/admin set-channel hunt #caça
/admin set-channel fish #pesca
/admin set-channel mine #mineração
/admin set-channel explore #exploração
/admin set-channel work #trabalho
/admin set-channel raid #boss-diário
/admin set-channel gacha #gachas
/admin set-channel duelo #duelos
/admin set-channel logs #logs
/admin set-channel anuncios #anúncios

Resultado:
- /hunt SOMENTE responde em #caça
- /fish SOMENTE responde em #pesca
- Etc...

Se usa em lugar errado:
├─ Nenhuma resposta pública
├─ Mensagem oculta (ephemeral) pro usuário:
│  └─ "❌ Use /hunt em #caça."
│  └─ "#caça" aparece como link clicável
└─ Ninguém no chat vê nada (chat fica limpo)
```

**Implementação:**
- Criar tabela `config_servidor` no banco
- Adicionar comando `/admin set-channel tipo #canal`
- Modificar TODOS os comandos de atividade para verificar canal
- Se canal errado: resposta ephemeral (oculta) com dica
- Se canal certo: resposta normal (visível)
- Armazenar por servidor (guild_id)

**Arquivo afetado:** `core.py`, `commands/profissoes.py`, `commands/admin.py`

---

### **1.4 Canal de Anúncios**

**Objetivo:** Centralizar anúncios de eventos raros em um único canal.

**Mudanças:**

```
Novo canal: #anúncios (configurável via /admin set-channel anuncios #canal)

Eventos que anunciam:
├─ 🌟 Pet Secreto ganho
│  └─ "🌟 usuario_123 ganhou Pet Secreto: Orkami!"
│
├─ 🎰 Jackpot ganho
│  └─ "🎰 usuario_456 acertou Jackpot! +50.000 CS!"
│
├─ 👑 Ranking mudou
│  └─ "👑 usuario_789 é novo #1 em CS!"
│
├─ 🏆 Boss finalizado
│  └─ "🏆 Boss de CS finalizado! Dano total: 75.000"
│  └─ Mostra top 3 participantes
│
├─ 💕 Relacionamento novo
│  └─ "💕 usuario_111 casou com usuario_222!"
│
└─ 📢 Eventos especiais
   └─ Mensagens customizadas do admin
```

**Implementação:**
- Criar função `enviar_anuncio(guild, titulo, emoji, mensagem)`
- Modificar função de pet secreto para anunciar
- Modificar função de jackpot para anunciar
- Adicionar anúncio ao finalizar boss
- Adicionar anúncio ao casar/amizade
- **Importante:** Usar @username SEM marcar (evita notificação em massa)

**Arquivo afetado:** `core.py`, `commands/*.py`

---

## 🐾 FASE 2: PETS SECRETOS

### **2.1 Criar Pets Secretos (Não Equipáveis)**

**Objetivo:** Adicionar pets ultra-raros que aparecem apenas como passivas no perfil.

**Mudanças:**

```
Adicionar coluna na tabela pets:
├─ secreto INTEGER (0/1, DEFAULT: 0)

Novo índice no banco:
└─ Tabela: pets_secretos (para tracking)
   ├─ user_id
   ├─ nome_pet
   ├─ criado_em
```

**Pets Secretos (3 total):**

```
1. Orkami (Deus Orca) 🌊
   ├─ Raridade: SECRETO
   ├─ Chance: 0.1% (1 em 1.000)
   ├─ Stats: +20% em TUDO (CS, XP, Drops)
   ├─ Visual: Descrição no perfil "Orkami ✨"
   ├─ Equipável: NÃO
   └─ Vender: NÃO (locked)

2. Ume (Deusa Arraia) 💜
   ├─ Raridade: SECRETO
   ├─ Chance: 0.1% (1 em 1.000)
   ├─ Stats: +20% em TUDO (CS, XP, Drops)
   ├─ Visual: Descrição no perfil "Ume ✨"
   ├─ Equipável: NÃO
   └─ Vender: NÃO (locked)

3. Carlinhos (Deus Cavalo) 🎭
   ├─ Raridade: SECRETO
   ├─ Chance: 0.1% (1 em 1.000)
   ├─ Stats: +20% em TUDO (CS, XP, Drops)
   ├─ Visual: Descrição no perfil "Carlinhos ✨"
   ├─ Equipável: NÃO
   └─ Vender: NÃO (locked)
```

**Funcionamento:**

```
Ao ganhar pet secreto no gacha:
├─ Não aparece em /pets
├─ Não aparece em /team
├─ Apenas PASSIVO (dá bônus)
├─ Anúncio no #anúncios:
│  └─ "🌟 usuario_123 ganhou Pet Secreto: Orkami!"
│
└─ Aparece SOMENTE em /perfil

Comando /perfil mostra:
├─ Dados normais
├─ Pets: 25
├─ 👫 Parceiro: @Maria
├─ 🌟 Pet Secreto: Orkami ✨
└─ Sem marcar o usuário
```

**Implementação:**
- Modificar função `escolher_mutacao()` para incluir pets secretos na chance
- Adicionar coluna `secreto` na tabela `pets`
- Modificar função de gacha para detectar pet secreto
- Não mostrar pet secreto em `/pets`
- Não permitir equip de pet secreto
- Mostrar no `/perfil` apenas se tiver
- Anunciar no #anúncios quando ganhar
- Bônus +30% aplicado automaticamente (passivo)

**Arquivo afetado:** `core.py`, `commands/pets.py`, `commands/perfil.py`, `commands/economia.py`

---

## 💰 FASE 3: VENDA AUTOMÁTICA DE ITENS

### **3.1 Sistema Smart Sell**

**Objetivo:** Vender automaticamente itens duplicados para gerar CS passivo.

**Mudanças:**

```
Quando jogador ganha item raro:
├─ Se JÁ tem 3+ do mesmo:
│  ├─ Vende automaticamente os extras
│  └─ Credita CS na conta
│
└─ Mensagem discreta:
   └─ "💰 +1.400 CS (Vendeu 2x Cristal Raro)"
```

**Implementação:**
- Modificar função `gerar_drops_atividade()`
- Após adicionar item, verificar se tem 3+
- Se sim: vender automaticamente
- Creditar CS (valor_venda * quantidade_extra)
- Mostrar mensagem ao fim da atividade
- Não criar confusão (automático e silencioso)

**Arquivo afetado:** `core.py`

---

## ⚔️ FASE 4: ENCANTAMENTOS (NOVO SISTEMA)

### **4.1 Criar Sistema de Encantamentos (Sem Craft)**

**Objetivo:** Adicionar profundidade ao sistema de pets com encantamentos PVE focados.

**Mudanças:**

```
Nova tabela no banco:
├─ user_id
├─ pet_id
├─ tipo_encantamento (TEXT)
├─ aplicado_em (INTEGER)

Novo recurso: P�� DE ENCANTO
├─ Obtido em atividades
├─ Drop chance baseada na atividade
├─ Acumula no banco do jogador
```

**12 Encantamentos (Sem Debuffs):**

```
OFENSIVOS PVE:
├─ Infernal 🔥
│  └─ +15% dano
│
├─ Elétrico ⚡
│  └─ +10% dano
│
└─ Primal 🦅
   └─ +5% dano

FARMING SPECIALIST:
├─ Saqueador 💰
│  └─ +15% CS (para farming)
│
├─ Colhedor 🌾
│  └─ +10% cs
│
└─ Mineiro ⛰️
   └─ +5% cs

ESPECIAIS:
├─ Sábio 📚
│  └─ +10% XP
│
├─ Noturno 🌙
│  └─ +10% CS entre 00:00-06:00 UTC
│
├─ Diurno ☀️
│  └─ +10% CS entre 12:00-18:00 UTC
│
├─ Sorte 🍀
│  └─ +5% chance drops raros
│
└─ Espectral 👻
   └─ +5% em tudo dano/xp/cs
```

**Obtenção de Pó:**

```
Por cada atividade:
├─ /hunt: 1 pó (min 0, max 1)
├─ /fish: 1 pó (min 0, max 1)
├─ /mine: 1 pó (min 0, max 1)
├─ /explore: 1 pó (min 0, max 1)
├─ /work: 1 pó (min 0, max 1)
├─ /daily: 2 pó (min 0, max 2)
└─ Boss semanal: 5 pó (min 0, max 5)

Total possível por dia: ~12 pó (consistente)
```

**Aplicação de Encantamento:**

```
/enchant apply pet_id tipo
├─ Verifica: 100 pó?
├─ Mostra confirmação: "Aplicar Infernal no pet #42? (100 pó)"
├─ Botão sim/não
└─ Se sim: aplica + deduz 100 pó

/enchant remove pet_id
├─ Custo: 50 CS + 50 pó (caro pra evitar spam)
├─ Remove encantamento
└─ Pet volta ao normal

/enchant list
├─ Mostra TODOS 12 encantamentos
├─ Categorias: Ofensivo, Farming, Especial
├─ Descrição, custo, efeito

/enchant info Infernal
├─ "Infernal 🔥: +15% dano"
├─ "Raridade: Lendario"
├─ "Categoria: Ofensivo"
└─ "Remoção: 50 CS + 50 pó"

só vale um encantamento por pet, caso ele encante novamente o bot avisa que ira remover o encatamento atual
reagir para confirmar

```
```

**Implementação:**
- Criar tabela `encantamentos_pet`
- Adicionar coluna `po_encanto` em `usuarios`
- Modificar funções de atividades para dar pó
- Criar comandos `/enchant apply`, `/enchant remove`, `/enchant list`, `/enchant info`
- Modificar cálculo de bônus para incluir encantamentos
- Sistema de stacking automático
- Info detalhada em `/enchant info`

**Arquivo afetado:** `core.py`, `commands/pets.py`, novo arquivo `commands/enchantments.py`

---

## 🎯 FASE 5: BOSSES SEMANAIS

### **5.1 Criar Sistema de 3 Bosses Semanais**

**Objetivo:** Substituir o boss diário por 3 bosses semanais focados em diferentes objetivos.

**Mudanças:**

```
NOVO SISTEMA - 3 BOSSES SEMANAIS:

Segunda-feira: BOSS DE CS
├─ Nome: Boss CS (aleatório entre Míticos)
├─ Objetivo: Ganho de CS
├─ Meta coletiva 30k = +50% CS
├─ Meta coletiva 60k = +100% CS
├─ Drops: Puro CS (nenhum pó)
│
Quarta-feira: BOSS DE XP
├─ Nome: Boss XP (aleatório entre Míticos)
├─ Objetivo: Leveling de pets
├─ Meta coletiva 30k = +50% XP
├─ Meta coletiva 60k = +100% XP
├─ Drops: Puro XP (nenhum CS)
│
Sexta-feira: BOSS DE PÓ
├─ Nome: Boss Pó (aleatório entre Míticos)
├─ Objetivo: Encantamentos
├─ Meta coletiva 30k = +50% pó drops
├─ Meta coletiva 60k = +100% pó drops
├─ Drops: Muito pó (nenhum CS)
```

**Mecânica Detalhada:**

```
PARTICIPAÇÃO:
├─ Cada jogador pode atacar 3x por semana
├─ Reseta segunda-feira 00:00 UTC
├─ Comando: /raid attack (em #raid)
│
DANO:
├─ Calcula based em pets equipados
├─ Variância ±30% (não é determinístico)
│
RECOMPENSAS:
├─ Dano base: CS/XP/Pó por dano contribuído
├─ Se atingir 30k: +50% recompensa
├─ Se atingir 60k: +100% recompensa
│
ANÚNCIOS:
├─ Ao finalizar boss:
│  └─ "🏆 Boss de CS finalizado!"
│  └─ "Dano total: 75.000 | Meta atingida: +100%"
│  └─ Top 3 participantes listados
│
└─ No #anúncios (canal dedicado)
```

**Implementação:**
- Modificar tabela `raids` para incluir tipo (cs/xp/po)
- Criar função que seleciona boss correto por dia
- Modificar `/raid attack` para calcular recompensa baseada no tipo
- Adicionar anúncio ao finalizar boss
- Sistema de metas coletivas com bonus
- Mostrar progresso do boss (dano total atual)
- Comando `/raid info` mostra info atual do boss

**Arquivo afetado:** `core.py`, `commands/raid.py`

---

## ⚔️ FASE 6: DUELOS CASUAIS

### **6.1 Criar Sistema de Duelos Casual**

**Objetivo:** Permitir que amigos duelem sem ranking, com recompensas baixas e foco em diversão.

**Mudanças:**

```
NOVO SISTEMA - DUELOS SEM RANKING:

Comando:
/duelo @usuario

Funcionamento:
├─ Envia proposta via reação
├─ "⚔️ Duelo com @usuario?"
├─ Botões: ✅ Aceitar | ❌ Recusar
├─ Timeout: 60 segundos
│
SE ACEITAR:
├─ Bot pega 1 pet aleatório de cada um
├─ Calcula dano com variância ±30%
├─ Mostra resultado:
│  └─ "⚔️ João venceu!"
│  └─ "Pet: Dragon (45 dano) vs Orca (38 dano)"
│
├─ VENCEDOR: +10 CS + 2 XP pet
├─ PERDEDOR: +2 CS (consolação) + 1 XP pet
│
└─ Cooldown: 5 minutos entre duelos

CARACTERÍSTICAS:
├─ Ilimitado (sem limite de duelos/dia)
├─ Não gasta energia
├─ Não tem ranking
├─ Foco: diversão com amigos
├─ Recompensas baixas (não é farm)
```

**Implementação:**
- Criar comando `/duelo @usuario`
- Criar classe `DueloView` com botões de aceitar/recusar
- Função para calcular dano com variância
- Recompensas hardcoded (10 CS win, 2 CS lose)
- Cooldown de 5 min entre duelos
- Armazenar último duelo do usuário no banco
- Sem sistema de ranking

**Arquivo afetado:** novo arquivo `commands/duelo.py`

---

## 💕 FASE 7: RELACIONAMENTOS

### **7.1 Sistema de Relacionamentos (Cosmético)**

**Objetivo:** Permitir que jogadores se casem ou façam amizade, mostrando apenas no perfil.

**Mudanças:**

```
Nova tabela no banco:
├─ user_id_1
├─ user_id_2
├─ tipo (marriage/friendship)
├─ desde (INTEGER timestamp)
├─ reputacao (INTEGER, default 0)

MECANISMO DE REPUTAÇÃO:
├─ +1 ponto por DIA (se ambos fizeram /daily)
├─ Reputação só aumenta ao fim do dia automático
├─ Max +7 por semana (1 por dia)
├─ Impossível explorar (uma vez por dia)
```

**Comandos:**

```
/marry @usuario
├─ Envia proposta de casamento
├─ Outro usuário aceita via reação
├─ Ambos aparecem no perfil um do outro
│
/befriend @usuario
├─ Proposta de amizade
├─ Outro usuário aceita
├─ Mostra no perfil como amigo
│
/divorce
├─ Desfaz casamento
├─ Remove perfil
│
/unfriend @usuario
├─ Remove amizade
├─ Remove perfil
│
/rep rank
├─ Top 10 casais
├─ Top 10 amizades
├─ "👫 João + Maria | Rep: 245"
│
/rep info @usuario
├─ "Casado com @Maria por 45 dias"
├─ "Amigo de @Pedro por 120 dias"
├─ Rep total com cada pessoa
└─ Data de início
```

**Exibição no Perfil:**

```
/perfil @usuario mostra:
├─ Nome + avatar
├─ Cristais, bilhetes, energia
├─ Profissão
├─ Pets: 25
├─ 👫 Parceiro: @Maria (SEM marcar)
├─ 👥 Amigos: @João, @Pedro, @Ana (Max 5, SEM marcar)
├─ 🌟 Pet Secreto: Orkami (se tiver)
└─ Resto dos dados

IMPORTANTE:
└─ Usar @username SEM marcar (evita notificação)
```

**Reputação - Automática:**

```
Sistema automático ao fim do dia:
├─ Verifica se ambos fizeram /daily
├─ Se sim: +1 reputação para cada
├─ Sem necessidade de comando
├─ Impossível explorar
```

**Implementação:**
- Criar tabela `relacionamentos`
- Adicionar coluna `reputacao` em `relacionamentos`
- Criar comandos `/marry`, `/befriend`, `/divorce`, `/unfriend`
- Criar comando `/rep rank` e `/rep info`
- Modificar `/perfil` para mostrar relacionamentos
- Task automática ao fim do dia para aumentar reputação
- Validações de aceitação via reação

**Arquivo afetado:** `core.py`, `commands/perfil.py`, novo arquivo `commands/relacionamentos.py`

---

## 🎯 FASE 8: SLOTS DE PETS

### **8.1 Sistema de 3 Slots Salvos de Pets**

**Objetivo:** Permitir que jogadores salvem diferentes times de pets para trocar rapidamente.

**Mudanças:**

```
Nova tabela no banco:
├─ user_id
├─ slot_numero (1-3)
├─ pet1_id (pode ser NULL)
├─ pet2_id (pode ser NULL)
├─ pet3_id (pode ser NULL)
├─ ativo (0/1)

Nova coluna em usuarios:
└─ slot_ativo (INTEGER, 1-3)
```

**Comandos:**

```
/slot 1 (ativa slot 1)
/slot 2 (ativa slot 2)
/slot 3 (ativa slot 3)

Função:
├─ Desativa slot atual
├─ Ativa novo slot
├─ Carrega os 3 pets salvos
├─ Mensagem oculta: "✅ Carregou Slot 2"
├─ Nenhuma mensagem pública
│
└─ Pode usar em QUALQUER canal

/slot set 1 pet1_id pet2_id pet3_id
├─ Salva 3 pets no slot 1
├─ Todos devem ser do usuário
├─ Validação de propriedade

/slot info 1
├─ Mostra pets salvos em slot 1
├─ "Slot 1: Dragon #42, Orca #15, Fenrir #88"
├─ Status: "Ativo" ou "Inativo"

/slot info
├─ Mostra todos 3 slots
├─ Qual está ativo atualmente
└─ Conteúdo de cada um

FUNCIONAMENTO NA PRÁTICA:

Exemplo 1:
- Jogador tem Slot 1 ativo: Dragon, Orca, Fenrir
- Vai pra raid
- Digita /slot 2 (carrega novo time)
- Vai pra raid com novo time
- Digita /slot 1
- Volta pro time antigo

Exemplo 2:
- Salva slot 1 pra farming: pets com Saqueador
- Salva slot 2 pra raid: pets de raid
- Salva slot 3 pra balanced: todos tipos
- /slot 1 antes de farmear
- /slot 2 antes de raid
- /slot 3 antes de explorar
```

**Características:**

```
├─ Máximo 3 slots
├─ Cada slot: 3 pets
├─ Pode usar em QUALQUER canal
├─ Mensagem oculta (ephemeral)
├─ Muito rápido (sem lag)
├─ Troca automática de team
│
└─ NÃO afeta outras atividades
```

**Implementação:**
- Criar tabela `slots_pets`
- Adicionar coluna `slot_ativo` em `usuarios`
- Criar comando `/slot numero` (ativa)
- Criar comando `/slot set numero pet1 pet2 pet3` (salva)
- Criar comando `/slot info` (mostra)
- Modificar `executar_atividade()` para usar slot ativo
- Modificar equip/desequip para atualizar slots

**Arquivo afetado:** `core.py`, `commands/pets.py`, novo arquivo `commands/slots.py`

---

## 📊 FASE 9: INFORMAÇÕES SOBRE ENCANTAMENTOS E MUTAÇÕES

### **9.1 Comando Info Detalhado**

**Objetivo:** Evitar repetir informações toda vez, centralizar em comando.

**Mudanças:**

```
/enchant list
├─ Mostra TODOS 12 encantamentos
├─ Categorias: Ofensivo, Farming, Especial
├─ Cada um com emoji, bônus, custo

/enchant info Infernal
├─ "Infernal 🔥: +25% ganho CS"
├─ "Custo: 100 pó"
├─ "Categoria: Ofensivo"
├─ "Remoção: 50 CS + 50 pó"

/mutacao list
├─ Mostra TODAS as mutações
├─ "Shiny ✨: brilhante"
├─ "Gigante 📈: pet maior"
├─ "Alfa 👑: lidera"

/mutacao info Shiny
├─ "Shiny ✨: Mutação brilhante"
├─ "Chance: 3% no gacha normal"
├─ "Chance: 5% no gacha premium"
└─ "Efeito: Visual puro"
```

**Implementação:**
- Criar commands `/enchant list`, `/enchant info`
- Criar commands `/mutacao list`, `/mutacao info`
- Dados hardcoded das mutações
- Formatação clara e simples

**Arquivo afetado:** novo arquivo `commands/info.py`

---

## 🎮 MODIFICAÇÕES GERAIS

### **10.1 Remover Mutações Negativas**

**Objetivo:** Simplificar sistema, remover mutações que causam debuff.

**Mudanças:**

```
REMOVER:
├─ Anjo (confuso)
├─ Demônio (confuso)
├─ Podre (debuff)
└─ Corrompido (debuff)

MANTER:
├─ Shiny ✨ (brilhante, puro visual)
├─ Gigante 📈 (maior)
└─ Alfa 👑 (lidera)

NOVO (opcional):
└─ Nenhum novo por enquanto
```

**Implementação:**
- Remover mutações da lógica em `core.py`
- Remover de `MULTIPLICADOR_MUTACAO_BONUS`
- Atualizar chance no `escolher_mutacao()`
- Pets antigos com essas mutações permanecem (histórico)

**Arquivo afetado:** `core.py`

---

### **10.2 Simplificar Mensagens de Atividade**

**Objetivo:** Remover informações desnecessárias, deixar enxuto.

**Mudanças:**

```
ANTES (longo demais):
"🎣 Pesca concluído!
Ganho base: 50 CS
Bônus total: 25%
Total recebido: 62 CS
Energia restante: 85/100

Bônus considerados:
Peixe-Palhaço Nv.15 (+10%)
Vara de Pesca (+10%)
Poção de Sorte (+5%)

XP:
Peixe-Palhaço subiu +10 XP
Tubarão ganhou +7 XP (75%)

Drops:
Pedra Brilhante
Bilhete Premium"

DEPOIS (enxuto):
"🎣 **62 CS** | ⚡85/100 | 📦2 drops"

Mensagem adicional (oculta para detalhes):
"/info para mais detalhes"
```

**Implementação:**
- Modificar função `executar_atividade()` em `core.py`
- Remover detalhes de bônus da mensagem principal
- Mostrar APENAS: CS, energia, drops
- Adicionar comando `/info-last` para ver detalhes
- Manter logs em #logs para admins

**Arquivo afetado:** `core.py`

---

### **10.3 Aumentar XP Primário / Reduzir XP Secundário**

**Objetivo:** Fazer XP Share valer a pena, incentivar escolher pets certos.

**Mudanças:**

```
ANTES:
├─ Pet da linha: 100% XP
├─ Outros pets: 75% XP
└─ XP Share: 50% XP

DEPOIS:
├─ Pet da linha: 100% XP (SEM MUDANÇA)
├─ Outros pets: 30% XP (reduzido de 75%)
└─ XP Share: 25% XP (reduzido de 50%)

EXEMPLO:
/fish com "Orca (Pesca)" + "Lobo (Caça)"
├─ Orca: 100 XP
└─ Lobo: 30 XP (não 75!)

Com XP Share setado em outro:
└─ Esse pet: 25 XP (não 50!)
```

**Implementação:**
- Modificar função `adicionar_xp_pets_equipados()` em `core.py`
- Mudar constante `quantidade_parcial` de 0.75 para 0.30
- Mudar XP Share de 0.50 para 0.25
- Documentar mudança

**Arquivo afetado:** `core.py`

---

### **10.4 Remover Invasões Aleatórias**

**Objetivo:** Simplificar sistema, remover feature redundante.

**Mudanças:**

```
REMOVER:
├─ Sistema de invasões aleatórias
├─ Events de invasão
├─ Tabela de invasões (opcional: manter para histórico)
│
└─ Boss Diário já serve como evento coletivo

MANTER:
└─ Sistema de boss semanal (CS, XP, Pó)
```

**Implementação:**
- Remover comandos de invasão
- Remover task de invasões
- Remover lógica de invasão do core
- Manter tabela para histórico (opcional)

**Arquivo afetado:** `core.py`, `commands/raid.py`

---

### **10.5 Remover Sistema de Slots Contextuais**

**Objetivo:** Simplificar, usar slots salvos em vez de contextos.

**Mudanças:**

```
REMOVER:
├─ /slot setup daily
├─ /slot setup work
├─ /slot setup raid
├─ /slot setup duelo
│
NOVO:
├─ /slot 1, /slot 2, /slot 3 (salvos simples)
└─ Jogador controla qual usar quando
```

**Implementação:**
- Remover contextos
- Usar modelo simples de 3 slots
- Ver seção 8.1 acima

**Arquivo afetado:** `core.py`

---

### **10.6 Remover Clãs (Por Enquanto)**

**Objetivo:** Reduzir escopo, focar em features mais importantes.

**Mudanças:**

```
REMOVER:
├─ Sistema de clãs
├─ Objetivos de clã
├─ Recompensas de clã
│
FUTURO:
└─ Talvez adicionar depois (v2.1 ou v3.0)
```

**Implementação:**
- Não implementar clãs

**Arquivo afetado:** Nenhum

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **FASE 1 - RENOMEAÇÃO E CONFIG**
- [ ] Renomear comandos (hunt, fish, mine, explore, work, daily)
- [ ] Adicionar alias antigos (cacar, pescar, etc)
- [ ] Adicionar atalhos (/h, /f, /m, /e, /w, /d)
- [ ] Implementar prefixo secundário
- [ ] Implementar canais dinâmicos
- [ ] Implementar canal de anúncios
- [ ] Testar com aliases e atalhos

### **FASE 2 - PETS SECRETOS**
- [ ] Adicionar coluna `secreto` em pets
- [ ] Criar pets Orkami, Ume, Carlinhos
- [ ] Implementar chance 0.1% no gacha
- [ ] Não mostrar em /pets
- [ ] Mostrar no /perfil
- [ ] Anunciar no #anúncios
- [ ] Aplicar bônus +30% passivo

### **FASE 3 - VENDA AUTOMÁTICA**
- [ ] Implementar smart sell
- [ ] Vender duplicatas automaticamente
- [ ] Creditar CS
- [ ] Testar com múltiplos itens

### **FASE 4 - ENCANTAMENTOS**
- [ ] Criar tabela de encantamentos
- [ ] Adicionar coluna `po_encanto` em usuarios
- [ ] Criar 12 encantamentos
- [ ] Implementar coleta de pó
- [ ] Criar comando `/enchant apply`
- [ ] Criar comando `/enchant remove`
- [ ] Criar comando `/enchant list`
- [ ] Criar comando `/enchant info`
- [ ] Sistema de stacking automático
- [ ] Testar bônus aplicados

### **FASE 5 - BOSSES SEMANAIS**
- [ ] Modificar sistema de raids
- [ ] Criar 3 bosses (CS, XP, Pó)
- [ ] Implementar metas coletivas
- [ ] Anunciar ao finalizar
- [ ] Mostrar top 3 participantes
- [ ] Testar recompensas

### **FASE 6 - DUELOS CASUAL**
- [ ] Criar comando `/duelo @user`
- [ ] Implementar sistema de reação
- [ ] Calcular dano com variância
- [ ] Recompensas (10 CS win, 2 CS lose)
- [ ] Cooldown de 5 min
- [ ] Testar ilimitado

### **FASE 7 - RELACIONAMENTOS**
- [ ] Criar tabela de relacionamentos
- [ ] Criar comando `/marry`
- [ ] Criar comando `/befriend`
- [ ] Criar comando `/divorce`
- [ ] Criar comando `/unfriend`
- [ ] Criar comando `/rep rank`
- [ ] Criar comando `/rep info`
- [ ] Implementar reputação automática
- [ ] Mostrar no /perfil
- [ ] Testar propostas

### **FASE 8 - SLOTS**
- [ ] Criar tabela de slots
- [ ] Implementar /slot 1/2/3
- [ ] Implementar /slot set
- [ ] Implementar /slot info
- [ ] Carregamento automático
- [ ] Testar troca de team

### **FASE 9 - INFO**
- [ ] Criar `/enchant list` e `/enchant info`
- [ ] Criar `/mutacao list` e `/mutacao info`
- [ ] Testar exibição

### **MUDANÇAS GERAIS**
- [ ] Remover mutações negativas
- [ ] Simplificar mensagens
- [ ] Aumentar XP primário (sem mudança)
- [ ] Reduzir XP secundário (30%)
- [ ] Reduzir XP Share (25%)
- [ ] Remover invasões
- [ ] Remover slots contextuais

---

## 🎮 RESUMO FINAL

```
VERSÃO 2.0 CRISTAL BOT:

✅ Comandos renomeados + atalhos
✅ Prefixo secundário customizável
✅ Canais dinâmicos por servidor
✅ Canal de anúncios centralizado
✅ Pets secretos (passivos, cosmético)
✅ Venda automática de itens
✅ 12 encantamentos PVE focados
✅ Sistema de pó (sem craft)
✅ 3 bosses semanais (CS, XP, Pó)
✅ Duelos casual (sem ranking)
✅ Relacionamentos (cosmético)
✅ Slots de pets (3 salvos)
✅ Info centralizada
✅ XP balanceado

❌ Removido: Mutações negativas
❌ Removido: Invasões
❌ Removido: Slots contextuais
❌ Removido: Clãs (futuro)

RESULTADO:
🎮 Bot extremamente divertido
⚙️ Balanceado
🎯 Sem P2W
👥 Comunitário
🚀 Pronto para crescer
```

---

**Pronto para começar a implementação! 🚀✨**
