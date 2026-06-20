# Z-API + Supabase Sender

Script em Python que lê contatos cadastrados no **Supabase** e envia, via **Z-API**, a mensagem:

> Olá, `<nome_contato>` tudo bem com você?

Envia para até **3 contatos** (ou menos, se a tabela tiver menos registros), personalizando o nome de cada um.

## Stack

- Python 3.11+
- [Supabase](https://supabase.com) (Postgres + API) — plano gratuito
- [Z-API](https://www.z-api.io) (API não oficial de WhatsApp) — plano gratuito

## Estrutura

```
.
├── main.py                  # orquestra a leitura e o envio
├── config.py                # carrega e valida variáveis de ambiente
├── supabase_repository.py   # busca os contatos no Supabase
├── zapi_client.py           # envia mensagens via Z-API
├── schema.sql                # script para criar a tabela de exemplo
├── requirements.txt
├── .env.example
└── README.md
```

## 1. Setup da tabela no Supabase

1. Crie um projeto gratuito em [supabase.com](https://supabase.com).
2. Abra **SQL Editor** e rode o conteúdo de [`schema.sql`](./schema.sql), que cria a tabela `contatos`:

   | coluna     | tipo      | observação                          |
   |------------|-----------|--------------------------------------|
   | id         | bigint    | gerado automaticamente (PK)          |
   | nome       | text      | usado para personalizar a mensagem   |
   | telefone   | text      | formato `DDI DDD NÚMERO`, ex: `5511999999999` (apenas dígitos; o código também remove `+`, espaços, `-` e parênteses automaticamente) |
   | created_at | timestamp | preenchido automaticamente           |

3. Substitua os dados de exemplo pelos números reais que você quer notificar.
4. Em **Project Settings > API**, copie a **Project URL** e a chave **anon public** (ou `service_role`, se preferir).

## 2. Setup da Z-API

1. Crie uma conta gratuita em [z-api.io](https://www.z-api.io) e uma instância conectada ao seu WhatsApp (leia o QR Code pelo celular).
2. No painel da instância, copie:
   - **Instance ID**
   - **Token**
   - **Client-Token** (token de segurança da conta, em "Segurança")

## 3. Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
cp .env.example .env
```

```ini
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_KEY=sua_chave_anon_ou_service_role_aqui
SUPABASE_TABLE=contatos

# Z-API
ZAPI_INSTANCE_ID=sua_instance_id
ZAPI_TOKEN=seu_token
ZAPI_CLIENT_TOKEN=seu_client_token_de_seguranca
ZAPI_DELAY_TYPING=3
ZAPI_DELAY_MESSAGE=2

# Geral
MAX_CONTATOS=3
INTERVALO_MIN_SEGUNDOS=3
INTERVALO_MAX_SEGUNDOS=8
```

> O arquivo `.env` **não** é versionado (veja `.gitignore`).

### Envio humanizado

Para não disparar as 3 mensagens em menos de 1 segundo (padrão clássico de bot/spam), o script:

- Espera um intervalo **aleatório** entre `INTERVALO_MIN_SEGUNDOS` e `INTERVALO_MAX_SEGUNDOS` antes de enviar para o próximo contato.
- Usa os parâmetros nativos da Z-API `delayTyping` (mostra "digitando..." no WhatsApp por `ZAPI_DELAY_TYPING` segundos antes da mensagem chegar) e `delayMessage` (espera `ZAPI_DELAY_MESSAGE` segundos antes de entregar).

Ambos os pares de variáveis aceitam apenas valores de **1 a 15** (limite da própria Z-API) para os `ZAPI_DELAY_*`, e qualquer valor não-negativo para os `INTERVALO_*`.

## 4. Como rodar

```bash
# 1. Crie e ative um ambiente virtual (opcional, recomendado)
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o .env (passo anterior)

# 4. Execute
python main.py
```

### Saída esperada

```
2026-06-19 21:00:00 [INFO] Buscando até 3 contato(s) na tabela 'contatos'...
2026-06-19 21:00:00 [INFO] 3 contato(s) válido(s) encontrado(s).
2026-06-19 21:00:00 [INFO] Iniciando envio para 3 contato(s)...
2026-06-19 21:00:01 [INFO] ✅ [1/3] Mensagem enviada para Maria (telefone=5511999999999) | messageId=ABC123
2026-06-19 21:00:01 [INFO] Aguardando 5.2s antes do próximo envio...
2026-06-19 21:00:06 [INFO] ✅ [2/3] Mensagem enviada para João (telefone=5521988888888) | messageId=DEF456
2026-06-19 21:00:06 [INFO] Aguardando 3.8s antes do próximo envio...
2026-06-19 21:00:10 [INFO] ✅ [3/3] Mensagem enviada para Ana (telefone=5531977777777) | messageId=GHI789
2026-06-19 21:00:10 [INFO] Concluído. Sucessos: 3 | Falhas: 0
```

## Tratamento de erros

- **Variável de ambiente faltando**: o script para antes de fazer qualquer chamada de rede e mostra qual variável falta (`ConfigError`).
- **Registro do Supabase sem nome ou telefone**: é ignorado individualmente, com um log de `WARNING`, sem interromper o restante do fluxo.
- **Falha ao enviar para um contato específico** (rede, telefone inválido, erro da Z-API): é registrada como `ERROR` para aquele contato, mas o script continua tentando enviar para os demais.
- **Código de saída**: `0` se todos os envios deram certo (ou não havia contatos), `1` se houve algum erro de configuração, de leitura do Supabase, ou pelo menos uma falha de envio.

## Decisões de design

- A leitura limita o número de registros direto na query (`limit`), evitando trazer a tabela inteira só para descartar o excedente em Python.
- O cliente Z-API normaliza o telefone (remove `+`, espaços, `-`, `()`), já que a Z-API exige apenas dígitos.
- A mensagem é montada em um único ponto (`montar_mensagem`), garantindo que o texto enviado seja sempre exatamente `"Olá, <nome_contato> tudo bem com você?"`.