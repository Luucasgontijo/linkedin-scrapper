# LinkedIn Scraper API

Uma API REST para extrair dados do LinkedIn usando Python e Flask, containerizada com Docker e pronta para deployment em VPS.

## 🚀 Deployment Options

### 1. Local Development

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a API
python main.py
```

A API estará disponível em `http://localhost:8080`

### 2. Docker Local

```bash
# Build and run
docker-compose up -d --build

# Teste a API
curl http://localhost:8080/

# Parar os containers
docker-compose down
```

### 3. VPS Production Deployment (Recommended)

#### Opção A: Deployment Automatizado

```bash
# 1. Execute o script de deployment automático
./deploy-to-vps.sh user@your-vps-ip

# Exemplo:
./deploy-to-vps.sh ubuntu@192.168.1.100
```

#### Opção B: Deployment Manual

**Passo 1: Configurar o VPS**

```bash
# No seu VPS, execute:
curl -fsSL https://raw.githubusercontent.com/seu-usuario/linkedin-scraper/main/vps-setup.sh | bash
```

**Passo 2: Upload dos arquivos**

```bash
# Do seu computador local:
scp -r . user@your-vps-ip:/opt/linkedin-scraper/
```

**Passo 3: Deploy**

```bash
# No VPS:
cd /opt/linkedin-scraper
chmod +x deploy-production.sh
./deploy-production.sh
```

### 4. Docker com nginx (Produção)

```bash
# Deploy com nginx reverse proxy
docker-compose --profile production up -d --build

# Acesse via nginx
curl http://localhost/
```

## ⚙️ Configuração

### Sistema de Múltiplas Contas

O sistema agora suporta múltiplas contas do LinkedIn com rotação automática e detecção de challenges. Configure suas contas no arquivo `accounts.json`:

```json
{
  "accounts": [
    {
      "id": "account_1",
      "email": "conta1@gmail.com",
      "password": "senha1",
      "status": "active",
      "last_used": null,
      "challenge_count": 0,
      "blocked_until": null,
      "max_requests_per_hour": 100,
      "requests_count": 0,
      "requests_reset_time": null
    },
    {
      "id": "account_2", 
      "email": "conta2@gmail.com",
      "password": "senha2",
      "status": "active",
      "last_used": null,
      "challenge_count": 0,
      "blocked_until": null,
      "max_requests_per_hour": 100,
      "requests_count": 0,
      "requests_reset_time": null
    }
  ],
  "settings": {
    "rotation_strategy": "round_robin",
    "challenge_cooldown_minutes": 60,
    "max_challenge_retries": 3,
    "request_delay_seconds": 2,
    "retry_attempts": 3
  }
}
```

### Gerenciamento de Contas

Use o script `manage_accounts.py` para gerenciar suas contas:

```bash
# Listar todas as contas
python manage_accounts.py list

# Adicionar nova conta
python manage_accounts.py add account_3 conta3@gmail.com senha3

# Remover conta
python manage_accounts.py remove account_3

# Resetar conta específica
python manage_accounts.py reset account_1

# Resetar todas as contas
python manage_accounts.py reset-all

# Ver configurações
python manage_accounts.py settings --show

# Atualizar configurações
python manage_accounts.py settings --rotation-strategy least_used --challenge-cooldown 120
```

### Funcionalidades do Sistema de Contas

1. **Rotação Automática**: Alterna entre contas automaticamente
2. **Detecção de Challenge**: Detecta quando uma conta enfrenta verificação
3. **Bloqueio Temporário**: Bloqueia contas temporariamente após múltiplos challenges
4. **Limite de Requests**: Controla quantas requisições cada conta pode fazer por hora
5. **Retry Inteligente**: Tenta novamente com outra conta em caso de erro

### Variáveis de Ambiente (Opcional)

Ainda é possível usar `.env` para configurações adicionais:

```env
# Flask Configuration
FLASK_ENV=production
PORT=8080
```

### Variáveis de Ambiente

Crie um arquivo `.env` com suas credenciais do LinkedIn:

```env
# LinkedIn Credentials
LINKEDIN_EMAIL=seu-email@example.com
LINKEDIN_PASSWORD=sua-senha

# Flask Configuration
FLASK_ENV=production
PORT=8080
```

### Estrutura de Arquivos

```
ds-lkd-scrapper/
├── main.py                 # Aplicação Flask principal
├── requirements.txt        # Dependências Python
├── Dockerfile             # Configuração do container
├── docker-compose.yml     # Orquestração dos serviços
├── gunicorn.conf.py       # Configuração do Gunicorn
├── nginx.conf             # Configuração do nginx
├── .env                   # Variáveis de ambiente
├── deploy-production.sh   # Script de deployment VPS
├── deploy-to-vps.sh       # Script de upload para VPS
├── vps-setup.sh           # Script de setup do VPS
└── README.md              # Documentação
```

## 📋 Gerenciamento

### Comandos Docker

```bash
# Ver status dos containers
docker-compose ps

# Ver logs
docker-compose logs -f linkedin-scraper

# Restart serviços
docker-compose restart

# Parar serviços
docker-compose down

# Atualizar e redeploy
docker-compose up -d --build
```

### Comandos VPS

```bash
# Verificar status do serviço
sudo systemctl status linkedin-scraper

# Iniciar serviço
sudo systemctl start linkedin-scraper

# Parar serviço
sudo systemctl stop linkedin-scraper

# Ver logs do sistema
sudo journalctl -u linkedin-scraper -f
```

## 🛠️ Scripts de Teste e Gerenciamento

### Testar Sistema de Contas

```bash
# Testar sistema de múltiplas contas
python test_accounts.py

# Testar endpoint específico de URN
./test-urn-to-url.sh

# Testar toda a API
./test-api.sh
```

### Gerenciar Contas

```bash
# Ver ajuda do gerenciador
python manage_accounts.py --help

# Listar contas
python manage_accounts.py list

# Adicionar conta
python manage_accounts.py add nova_conta email@exemplo.com senha123

# Resetar conta com problemas
python manage_accounts.py reset conta_com_problema

# Ver configurações
python manage_accounts.py settings --show
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de autenticação LinkedIn**
   - Verifique suas credenciais no arquivo `accounts.json`
   - Use `python manage_accounts.py list` para ver status das contas
   - Teste login manual no LinkedIn

2. **Todas as contas bloqueadas**
   - Use `python manage_accounts.py reset-all` para resetar
   - Aguarde o período de cooldown configurado
   - Verifique `curl http://localhost:8080/api/accounts/status`

3. **Container não inicia**
   - Verifique os logs: `docker-compose logs linkedin-scraper`
   - Verifique se a porta 8080 está disponível
   - Certifique-se que o arquivo `accounts.json` existe

4. **API não responde**
   - Verifique se o container está rodando: `docker-compose ps`
   - Teste o health check: `curl http://localhost:8080/`
   - Verifique se há contas disponíveis: `curl http://localhost:8080/api/accounts/status`

5. **Muitos challenges**
   - Reduza a frequência de requests nas configurações
   - Adicione mais contas ao sistema
   - Aumente o `challenge_cooldown_minutes`

6. **Erro de permissões no VPS**
   - Execute: `sudo chown -R $USER:$USER /opt/linkedin-scraper`

### Monitoramento

```bash
# Status em tempo real das contas
watch -n 5 'curl -s http://localhost:8080/api/accounts/status | jq ".data"'

# Logs do container
docker-compose logs -f linkedin-scraper

# Logs do nginx
docker-compose logs -f nginx

# Logs do sistema (VPS)
sudo journalctl -u linkedin-scraper -f
```

## ⚠️ Observações Importantes

- Use credenciais válidas do LinkedIn
- Respeite os limites de rate da API do LinkedIn
- Use com responsabilidade e respeite os termos de uso
- Para produção, considere usar HTTPS/SSL
- Monitore o uso de recursos do servidor

## 🔒 Segurança

- Nunca commitee o arquivo `.env` no git
- Use senhas fortes para LinkedIn
- Configure firewall no VPS
- Use nginx para rate limiting
- Monitore logs de acesso

## 📞 Suporte

Para problemas ou dúvidas, verifique:

1. Os logs da aplicação
2. A documentação da API do LinkedIn
3. Os issues do projeto no GitHub

---

**Desenvolvido com ❤️ usando Flask + Docker**
