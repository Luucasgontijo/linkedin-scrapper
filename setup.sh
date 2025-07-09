#!/bin/bash

# Script de setup inicial para o LinkedIn Scraper com múltiplas contas

echo "🚀 Configurando LinkedIn Scraper com Sistema de Múltiplas Contas"
echo "================================================================"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado. Por favor, instale Python 3."
    exit 1
fi

print_status "Python 3 encontrado"

# Verificar se arquivo accounts.json existe
if [ ! -f "accounts.json" ]; then
    print_warning "Arquivo accounts.json não encontrado"
    
    if [ -f "accounts.json.example" ]; then
        echo "Copiando arquivo de exemplo..."
        cp accounts.json.example accounts.json
        print_status "Arquivo accounts.json criado a partir do exemplo"
        print_warning "⚠️  IMPORTANTE: Edite o arquivo accounts.json e configure suas credenciais do LinkedIn!"
        echo ""
        echo "Abra o arquivo accounts.json e substitua:"
        echo "- SEU_EMAIL_1@gmail.com por seu email real"
        echo "- SUA_SENHA_1 por sua senha real"
        echo "- Faça o mesmo para todas as contas"
        echo ""
    else
        print_error "Arquivo accounts.json.example não encontrado"
        exit 1
    fi
else
    print_status "Arquivo accounts.json encontrado"
fi

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    print_error "Arquivo requirements.txt não encontrado"
    exit 1
fi

print_status "Arquivo requirements.txt encontrado"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    print_status "Criando ambiente virtual..."
    python3 -m venv venv
    print_status "Ambiente virtual criado"
else
    print_status "Ambiente virtual já existe"
fi

# Ativar ambiente virtual e instalar dependências
print_status "Ativando ambiente virtual e instalando dependências..."
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

print_status "Dependências instaladas com sucesso"

# Testar se as contas estão configuradas corretamente
print_status "Verificando configuração das contas..."
python3 -c "
import json
try:
    with open('accounts.json', 'r') as f:
        data = json.load(f)
    
    accounts = data.get('accounts', [])
    if not accounts:
        print('❌ Nenhuma conta configurada')
        exit(1)
    
    unconfigured = 0
    for account in accounts:
        if 'SEU_EMAIL' in account.get('email', '') or 'SUA_SENHA' in account.get('password', ''):
            unconfigured += 1
    
    if unconfigured > 0:
        print(f'⚠️  {unconfigured} conta(s) ainda precisam ser configuradas')
        print('   Edite o arquivo accounts.json com suas credenciais reais')
    else:
        print(f'✅ {len(accounts)} conta(s) configurada(s)')
        
except Exception as e:
    print(f'❌ Erro ao ler accounts.json: {e}')
    exit(1)
"

# Tornar scripts executáveis
chmod +x *.sh *.py

print_status "Scripts tornados executáveis"

echo ""
echo "================================================================"
print_status "Setup concluído!"
echo ""
echo "Próximos passos:"
echo "1. Edite o arquivo accounts.json com suas credenciais do LinkedIn"
echo "2. Execute: python manage_accounts.py list (para verificar contas)"
echo "3. Execute: python main.py (para iniciar a API)"
echo "4. Teste: python test_accounts.py (para testar o sistema)"
echo ""
echo "Comandos úteis:"
echo "- Listar contas: python manage_accounts.py list"
echo "- Adicionar conta: python manage_accounts.py add ID EMAIL SENHA"
echo "- Testar API: ./test-api.sh"
echo "- Status das contas: curl http://localhost:8080/api/accounts/status"
echo ""
print_warning "LEMBRE-SE: Nunca commite o arquivo accounts.json no git!"
echo "================================================================"
