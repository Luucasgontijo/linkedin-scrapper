#!/usr/bin/env python3
"""
Script para gerenciar contas do LinkedIn
Permite adicionar, remover, resetar e visualizar contas
"""

import json
import sys
import argparse
from datetime import datetime

class AccountsManager:
    def __init__(self, accounts_file="accounts.json"):
        self.accounts_file = accounts_file
        self.load_accounts()
    
    def load_accounts(self):
        """Carrega as contas do arquivo JSON"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo {self.accounts_file} não encontrado")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao decodificar JSON: {e}")
            sys.exit(1)
    
    def save_accounts(self):
        """Salva as contas no arquivo JSON"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print("✅ Contas salvas com sucesso")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def list_accounts(self):
        """Lista todas as contas"""
        print("\n=== Lista de Contas ===")
        
        if not self.data.get("accounts"):
            print("Nenhuma conta encontrada")
            return
        
        for i, account in enumerate(self.data["accounts"], 1):
            status_icon = "✅" if account["status"] == "active" else "❌"
            print(f"\n{i}. {status_icon} {account['id']}")
            print(f"   Email: {account['email']}")
            print(f"   Status: {account['status']}")
            print(f"   Challenges: {account.get('challenge_count', 0)}")
            print(f"   Requests: {account.get('requests_count', 0)}")
            if account.get('last_used'):
                print(f"   Último uso: {account['last_used']}")
            if account.get('blocked_until'):
                print(f"   Bloqueada até: {account['blocked_until']}")
        
        print(f"\nTotal: {len(self.data['accounts'])} contas")
    
    def add_account(self, account_id, email, password):
        """Adiciona uma nova conta"""
        # Verificar se ID já existe
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                print(f"❌ Conta com ID '{account_id}' já existe")
                return
        
        # Verificar se email já existe
        for account in self.data["accounts"]:
            if account["email"] == email:
                print(f"❌ Conta com email '{email}' já existe")
                return
        
        new_account = {
            "id": account_id,
            "email": email,
            "password": password,
            "status": "active",
            "last_used": None,
            "challenge_count": 0,
            "blocked_until": None,
            "max_requests_per_hour": 100,
            "requests_count": 0,
            "requests_reset_time": None
        }
        
        self.data["accounts"].append(new_account)
        self.save_accounts()
        print(f"✅ Conta '{account_id}' adicionada com sucesso")
    
    def remove_account(self, account_id):
        """Remove uma conta"""
        for i, account in enumerate(self.data["accounts"]):
            if account["id"] == account_id:
                self.data["accounts"].pop(i)
                self.save_accounts()
                print(f"✅ Conta '{account_id}' removida com sucesso")
                return
        
        print(f"❌ Conta '{account_id}' não encontrada")
    
    def reset_account(self, account_id):
        """Reseta o status de uma conta"""
        for account in self.data["accounts"]:
            if account["id"] == account_id:
                account["status"] = "active"
                account["challenge_count"] = 0
                account["blocked_until"] = None
                account["requests_count"] = 0
                account["requests_reset_time"] = None
                account["last_used"] = None
                self.save_accounts()
                print(f"✅ Conta '{account_id}' resetada com sucesso")
                return
        
        print(f"❌ Conta '{account_id}' não encontrada")
    
    def reset_all_accounts(self):
        """Reseta o status de todas as contas"""
        for account in self.data["accounts"]:
            account["status"] = "active"
            account["challenge_count"] = 0
            account["blocked_until"] = None
            account["requests_count"] = 0
            account["requests_reset_time"] = None
            account["last_used"] = None
        
        self.save_accounts()
        print("✅ Todas as contas foram resetadas")
    
    def update_settings(self, **kwargs):
        """Atualiza configurações do sistema"""
        if "settings" not in self.data:
            self.data["settings"] = {}
        
        for key, value in kwargs.items():
            if value is not None:
                self.data["settings"][key] = value
                print(f"✅ {key} atualizado para: {value}")
        
        self.save_accounts()
    
    def show_settings(self):
        """Mostra as configurações atuais"""
        print("\n=== Configurações ===")
        settings = self.data.get("settings", {})
        
        print(f"Estratégia de rotação: {settings.get('rotation_strategy', 'round_robin')}")
        print(f"Cooldown de challenge: {settings.get('challenge_cooldown_minutes', 60)} minutos")
        print(f"Máximo de challenges: {settings.get('max_challenge_retries', 3)}")
        print(f"Delay entre requests: {settings.get('request_delay_seconds', 2)} segundos")
        print(f"Tentativas de retry: {settings.get('retry_attempts', 3)}")

def main():
    parser = argparse.ArgumentParser(description="Gerenciador de Contas LinkedIn")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando list
    subparsers.add_parser('list', help='Lista todas as contas')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Adiciona uma nova conta')
    add_parser.add_argument('id', help='ID da conta')
    add_parser.add_argument('email', help='Email da conta')
    add_parser.add_argument('password', help='Senha da conta')
    
    # Comando remove
    remove_parser = subparsers.add_parser('remove', help='Remove uma conta')
    remove_parser.add_argument('id', help='ID da conta a remover')
    
    # Comando reset
    reset_parser = subparsers.add_parser('reset', help='Reseta uma conta específica')
    reset_parser.add_argument('id', help='ID da conta a resetar')
    
    # Comando reset-all
    subparsers.add_parser('reset-all', help='Reseta todas as contas')
    
    # Comando settings
    settings_parser = subparsers.add_parser('settings', help='Gerencia configurações')
    settings_parser.add_argument('--show', action='store_true', help='Mostra configurações atuais')
    settings_parser.add_argument('--rotation-strategy', choices=['round_robin', 'least_used'], help='Estratégia de rotação')
    settings_parser.add_argument('--challenge-cooldown', type=int, help='Cooldown de challenge em minutos')
    settings_parser.add_argument('--max-challenges', type=int, help='Máximo de challenges antes de bloquear')
    settings_parser.add_argument('--request-delay', type=int, help='Delay entre requests em segundos')
    settings_parser.add_argument('--retry-attempts', type=int, help='Número de tentativas de retry')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = AccountsManager()
    
    if args.command == 'list':
        manager.list_accounts()
    
    elif args.command == 'add':
        manager.add_account(args.id, args.email, args.password)
    
    elif args.command == 'remove':
        manager.remove_account(args.id)
    
    elif args.command == 'reset':
        manager.reset_account(args.id)
    
    elif args.command == 'reset-all':
        confirm = input("⚠️  Tem certeza que deseja resetar TODAS as contas? (s/N): ")
        if confirm.lower() in ['s', 'sim']:
            manager.reset_all_accounts()
        else:
            print("Operação cancelada")
    
    elif args.command == 'settings':
        if args.show:
            manager.show_settings()
        else:
            manager.update_settings(
                rotation_strategy=args.rotation_strategy,
                challenge_cooldown_minutes=args.challenge_cooldown,
                max_challenge_retries=args.max_challenges,
                request_delay_seconds=args.request_delay,
                retry_attempts=args.retry_attempts
            )

if __name__ == "__main__":
    main()
