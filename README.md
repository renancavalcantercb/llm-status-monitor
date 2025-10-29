# LLM Status Monitor

Monitor de status simples para Claude (Anthropic) e ChatGPT (OpenAI) com alertas via Discord ou Slack webhook.

## Funcionalidades

- ✅ Monitora RSS feeds de status do Anthropic e OpenAI
- 🔔 Envia notificações para **Discord ou Slack** apenas quando há problemas ativos
- 🧠 Filtro inteligente que ignora resoluções e status normais
- 💾 Mantém estado persistente para evitar notificações duplicadas
- ⏱️ Verificação configurável por intervalo de tempo
- 🎨 Notificações formatadas com cores diferentes por serviço

## Pré-requisitos

- Python 3.7+
- Discord webhook URL **ou** Slack webhook URL (veja como criar abaixo)

## Configuração

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar webhook (Discord ou Slack)

#### Opção A: Discord

1. No Discord, vá para o canal onde quer receber as notificações
2. Clique na engrenagem de configurações do canal
3. Vá em "Integrações" → "Webhooks" → "Criar Webhook"
4. Copie a URL do webhook

#### Opção B: Slack

1. Acesse https://api.slack.com/apps e crie um novo app
2. Vá em "Incoming Webhooks" e ative
3. Clique em "Add New Webhook to Workspace"
4. Selecione o canal onde quer receber as notificações
5. Copie a Webhook URL gerada

### 3. Criar arquivo .env

```bash
cp .env.example .env
```

Edite o arquivo `.env` com as configurações apropriadas:

**Para Discord:**
```env
NOTIFICATION_TYPE=discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN
CHECK_INTERVAL=300
```

**Para Slack:**
```env
NOTIFICATION_TYPE=slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
CHECK_INTERVAL=300
```

## Uso

### Testar notificações

Antes de executar o monitor, teste se as notificações estão funcionando:

```bash
python scripts/test_notification.py
```

Isso enviará uma mensagem de teste para o Discord ou Slack configurado.

### Executar o monitor

```bash
python run_monitor.py
```

O monitor irá:
- Verificar os feeds RSS a cada 5 minutos (configurável)
- Enviar notificações no Discord ou Slack quando detectar novos incidentes
- Manter estado em `data/state.json` para evitar duplicatas
- Salvar logs em `logs/monitor.log`

### Executar em background

#### Linux/macOS (usando nohup)

```bash
nohup python run_monitor.py > monitor.log 2>&1 &
```

#### Linux (usando systemd)

Crie o arquivo `/etc/systemd/system/llm-monitor.service`:

```ini
[Unit]
Description=LLM Status Monitor
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/path/to/llm-status-monitor
ExecStart=/usr/bin/python3 /path/to/llm-status-monitor/run_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative o serviço:

```bash
sudo systemctl enable llm-monitor
sudo systemctl start llm-monitor
sudo systemctl status llm-monitor
```

#### Usando Docker Compose (recomendado)

```bash
# Construir e iniciar
docker compose up -d

# Ver logs
docker compose logs -f

# Parar
docker compose down

# Reiniciar
docker compose restart

# Ver status
docker compose ps
```

#### Usando Docker (manual)

```bash
docker build -t llm-monitor .
docker run -d --name llm-monitor --env-file .env -v $(pwd)/data:/app/data llm-monitor
```

## Estrutura do Projeto

```
llm-status-monitor/
├── llm_monitor/              # Pacote principal (modular)
│   ├── __init__.py          # Inicialização do pacote
│   ├── config.py            # Gerenciamento de configuração
│   ├── notifiers.py         # Notificadores Discord/Slack
│   ├── filters.py           # Filtro inteligente de incidentes
│   ├── feed_parser.py       # Parser de feeds RSS
│   ├── state.py             # Gerenciamento de estado
│   └── monitor.py           # Lógica principal de monitoramento
├── scripts/                  # Scripts utilitários
│   ├── test_notification.py # Teste de envio de notificações
│   ├── test_feeds.py        # Teste de conectividade dos feeds
│   └── test.sh              # Script para rodar testes
├── tests/                    # Testes com pytest
│   ├── test_filters.py      # Testes do filtro de incidentes
│   ├── test_config.py       # Testes de configuração
│   └── test_state.py        # Testes de estado
├── run_monitor.py           # Script principal de execução
├── requirements.txt         # Dependências Python
├── pyproject.toml           # Configuração do projeto
├── pytest.ini               # Configuração do pytest
├── .env.example            # Exemplo de configuração
├── .env                    # Sua configuração (não commitado)
├── data/
│   └── state.json          # Estado persistente (criado automaticamente)
├── logs/
│   └── monitor.log         # Logs da aplicação (criado automaticamente)
└── README.md               # Esta documentação
```

## Formatos de Notificação

### Discord
As notificações no Discord usam **Embeds** com:
- Título colorido com emoji 🚨
- Descrição do incidente
- Link para página de status
- Campo "Details" com descrição completa
- Footer com timestamp

### Slack
As notificações no Slack usam **Block Kit** com:
- Header colorido com emoji 🚨
- Seção principal com título em negrito
- Descrição completa do incidente
- Link formatado para página de status
- Context com timestamp
- Barra lateral colorida por serviço

## Serviços Monitorados

| Serviço | RSS Feed |
|---------|----------|
| Anthropic (Claude) | https://status.claude.com/history.rss |
| OpenAI (ChatGPT) | https://status.openai.com/history.rss |

## Filtro Inteligente de Incidentes

O monitor utiliza um filtro inteligente que **notifica apenas incidentes ativos**, ignorando resoluções e status normais.

### ✅ Quando NOTIFICA (problemas ativos)

Detecta palavras-chave que indicam problemas em andamento:
- `investigating`, `identified`, `monitoring`
- `degraded`, `outage`, `down`, `unavailable`
- `elevated error`, `high error rate`
- `service disruption`, `experiencing issues`
- `broken`, `not loading`, `failing`

### ❌ Quando IGNORA (sem notificação)

Detecta palavras-chave de resolução/normalidade:
- `resolved`, `recovered`, `fixed`
- `completed`, `restored`
- `all services operational`
- `all impacted services have now fully recovered`
- `post-mortem` (análises históricas)

### 🧪 Testar o Filtro

Execute os testes com pytest para validar a lógica:

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Rodar todos os testes
pytest

# Rodar testes com coverage
pytest --cov=llm_monitor --cov-report=html

# Ou usar o script auxiliar
./scripts/test.sh
```

Os testes incluem casos baseados em incidentes reais dos feeds RSS e fornecem relatório de cobertura.

## Configuração Avançada

### Ajustar intervalo de verificação

Edite `CHECK_INTERVAL` no arquivo `.env` (valor em segundos):

```env
CHECK_INTERVAL=300  # 5 minutos
CHECK_INTERVAL=600  # 10 minutos
CHECK_INTERVAL=60   # 1 minuto
```

### Adicionar mais serviços

Edite `llm_monitor/config.py` e adicione ao dicionário `FEEDS`:

```python
from .config import FeedConfig

FEEDS = {
    # ... serviços existentes
    'novo_servico': FeedConfig(
        name='Nome do Serviço',
        url='https://status.exemplo.com/history.rss',
        color=0xFF5733  # Cor hexadecimal
    )
}
```

## Troubleshooting

### Não recebo notificações

- ✅ Verifique se o `NOTIFICATION_TYPE` está correto no `.env` (discord ou slack)
- ✅ Verifique se o webhook URL está correto (`DISCORD_WEBHOOK_URL` ou `SLACK_WEBHOOK_URL`)
- ✅ Teste manualmente a URL do webhook
- ✅ Verifique permissões do canal (Discord ou Slack)

### Erro ao parsear RSS

- ✅ Verifique conexão com internet
- ✅ Teste se os URLs dos feeds estão acessíveis
- ✅ Veja os logs para detalhes do erro

### Estado não persiste

- ✅ Verifique permissões de escrita no diretório `data/`
- ✅ Confirme que `data/state.json` está sendo criado
- ✅ Verifique os logs em `logs/monitor.log` para erros de I/O

## Desenvolvimento

### Instalação para Desenvolvimento

```bash
# Clonar repositório
git clone <repo-url>
cd llm-status-monitor

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate  # Windows

# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"
```

### Executar Testes

```bash
# Rodar todos os testes
pytest

# Rodar com cobertura
pytest --cov=llm_monitor --cov-report=html

# Rodar testes específicos
pytest tests/test_filters.py
pytest tests/test_config.py -v

# Rodar apenas testes rápidos (excluir integration)
pytest -m "not integration"
```

### Estrutura do Código

O projeto segue princípios de código limpo com separação de responsabilidades:

- **config.py**: Validação e carregamento de configuração com type hints
- **notifiers.py**: Classes de notificação com padrão Strategy
- **filters.py**: Lógica de filtro de incidentes isolada e testável
- **feed_parser.py**: Parse de RSS com tratamento de erros robusto
- **state.py**: Gerenciamento de estado persistente
- **monitor.py**: Orquestração principal do monitoramento

Todos os módulos incluem:
- ✅ Type hints completos (Python 3.9+)
- ✅ Logging apropriado
- ✅ Tratamento de erros robusto
- ✅ Testes unitários com pytest
- ✅ Documentação em docstrings

## Licença

MIT

## Contribuindo

Pull requests são bem-vindos! Para mudanças maiores, abra uma issue primeiro.
