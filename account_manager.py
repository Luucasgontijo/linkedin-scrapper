"""
LinkedIn Account Manager
Gerencia múltiplas contas do LinkedIn com rotação automática e detecção de challenges
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from linkedin_api import Linkedin
import os

logger = logging.getLogger(__name__)

class LinkedInAccountManager:
    def __init__(self, accounts_file: str = "accounts.json"):
        self.accounts_file = accounts_file
        self.accounts_data = self.load_accounts()
        self.current_account_index = 0
        self.linkedin_api = None
        self.current_account = None
        
    def load_accounts(self) -> dict:
        """Carrega a configuração das contas do arquivo JSON"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Arquivo {self.accounts_file} não encontrado")
            return {"accounts": [], "settings": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return {"accounts": [], "settings": {}}
    
    def save_accounts(self):
        """Salva a configuração das contas no arquivo JSON"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar contas: {e}")
    
    def get_available_accounts(self) -> List[dict]:
        """Retorna lista de contas disponíveis (não bloqueadas)"""
        available = []
        current_time = datetime.now()
        
        for account in self.accounts_data["accounts"]:
            if account["status"] != "active":
                continue
                
            # Verifica se a conta está bloqueada temporariamente
            if account.get("blocked_until"):
                blocked_until = datetime.fromisoformat(account["blocked_until"])
                if current_time < blocked_until:
                    continue
                else:
                    # Remove o bloqueio se o tempo passou
                    account["blocked_until"] = None
                    account["challenge_count"] = 0
            
            # Verifica limite de requests por hora
            if account.get("requests_reset_time"):
                reset_time = datetime.fromisoformat(account["requests_reset_time"])
                if current_time > reset_time:
                    account["requests_count"] = 0
                    account["requests_reset_time"] = None
                elif account.get("requests_count", 0) >= account.get("max_requests_per_hour", 100):
                    continue
            
            available.append(account)
        
        return available
    
    def get_next_account(self) -> Optional[dict]:
        """Retorna a próxima conta disponível baseada na estratégia de rotação"""
        available_accounts = self.get_available_accounts()
        
        if not available_accounts:
            logger.warning("Nenhuma conta disponível")
            return None
        
        strategy = self.accounts_data.get("settings", {}).get("rotation_strategy", "round_robin")
        
        if strategy == "round_robin":
            # Rotação circular
            if self.current_account_index >= len(available_accounts):
                self.current_account_index = 0
            account = available_accounts[self.current_account_index]
            self.current_account_index = (self.current_account_index + 1) % len(available_accounts)
            
        elif strategy == "least_used":
            # Usar a conta menos utilizada
            account = min(available_accounts, 
                         key=lambda x: x.get("requests_count", 0))
        
        else:
            # Padrão: primeira disponível
            account = available_accounts[0]
        
        return account
    
    def mark_challenge(self, account_id: str):
        """Marca uma conta como tendo enfrentado um challenge"""
        for account in self.accounts_data["accounts"]:
            if account["id"] == account_id:
                account["challenge_count"] = account.get("challenge_count", 0) + 1
                cooldown_minutes = self.accounts_data.get("settings", {}).get("challenge_cooldown_minutes", 60)
                max_retries = self.accounts_data.get("settings", {}).get("max_challenge_retries", 3)
                
                if account["challenge_count"] >= max_retries:
                    # Bloquear conta temporariamente
                    blocked_until = datetime.now() + timedelta(minutes=cooldown_minutes)
                    account["blocked_until"] = blocked_until.isoformat()
                    account["status"] = "blocked"
                    logger.warning(f"Conta {account_id} bloqueada até {blocked_until}")
                
                self.save_accounts()
                break
    
    def mark_request(self, account_id: str):
        """Marca uma requisição feita pela conta"""
        for account in self.accounts_data["accounts"]:
            if account["id"] == account_id:
                current_time = datetime.now()
                
                # Inicializar contador se necessário
                if not account.get("requests_reset_time"):
                    account["requests_reset_time"] = (current_time + timedelta(hours=1)).isoformat()
                    account["requests_count"] = 0
                
                account["requests_count"] = account.get("requests_count", 0) + 1
                account["last_used"] = current_time.isoformat()
                
                self.save_accounts()
                break
    
    def initialize_api(self, max_retries: int = 3) -> bool:
        """Inicializa a API do LinkedIn com rotação de contas"""
        retry_count = 0
        
        while retry_count < max_retries:
            account = self.get_next_account()
            
            if not account:
                logger.error("Nenhuma conta disponível para autenticação")
                return False
            
            try:
                logger.info(f"Tentando autenticar com conta: {account['id']}")
                
                # Criar nova instância da API
                self.linkedin_api = Linkedin(account["email"], account["password"])
                self.current_account = account
                
                # Marcar uso da conta
                self.mark_request(account["id"])
                
                logger.info(f"Autenticação bem-sucedida com conta: {account['id']}")
                return True
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Detectar challenges comuns
                if any(keyword in error_message for keyword in [
                    "challenge", "captcha", "verification", "suspicious", 
                    "unusual activity", "security check", "verify"
                ]):
                    logger.warning(f"Challenge detectado na conta {account['id']}: {e}")
                    self.mark_challenge(account["id"])
                else:
                    logger.error(f"Erro de autenticação na conta {account['id']}: {e}")
                
                retry_count += 1
                
                # Delay entre tentativas
                delay = self.accounts_data.get("settings", {}).get("request_delay_seconds", 2)
                time.sleep(delay)
        
        logger.error("Falha na autenticação após todas as tentativas")
        return False
    
    def rotate_account(self) -> bool:
        """Força a rotação para a próxima conta"""
        logger.info("Forçando rotação de conta...")
        return self.initialize_api()
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Executa uma função com retry automático e rotação de contas"""
        max_retries = self.accounts_data.get("settings", {}).get("retry_attempts", 3)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.linkedin_api:
                    if not self.initialize_api():
                        raise Exception("Falha na inicialização da API")
                
                # Marcar requisição
                if self.current_account:
                    self.mark_request(self.current_account["id"])
                
                # Executar função
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_message = str(e).lower()
                retry_count += 1
                
                logger.warning(f"Erro na execução (tentativa {retry_count}): {e}")
                
                # Detectar challenges ou problemas que requerem rotação
                if any(keyword in error_message for keyword in [
                    "challenge", "captcha", "verification", "suspicious",
                    "unusual activity", "security check", "verify",
                    "rate limit", "too many requests", "blocked"
                ]):
                    if self.current_account:
                        self.mark_challenge(self.current_account["id"])
                    
                    # Tentar próxima conta
                    if retry_count < max_retries:
                        logger.info("Tentando próxima conta...")
                        if not self.rotate_account():
                            break
                else:
                    # Erro não relacionado a challenge, aguardar antes de tentar novamente
                    delay = self.accounts_data.get("settings", {}).get("request_delay_seconds", 2)
                    time.sleep(delay)
        
        raise Exception(f"Falha após {max_retries} tentativas")
    
    def get_api(self):
        """Retorna a instância atual da API do LinkedIn"""
        if not self.linkedin_api:
            if not self.initialize_api():
                return None
        return self.linkedin_api
    
    def get_account_status(self) -> dict:
        """Retorna status de todas as contas"""
        status = {
            "total_accounts": len(self.accounts_data["accounts"]),
            "active_accounts": 0,
            "blocked_accounts": 0,
            "current_account": self.current_account["id"] if self.current_account else None,
            "accounts": []
        }
        
        current_time = datetime.now()
        
        for account in self.accounts_data["accounts"]:
            account_status = {
                "id": account["id"],
                "email": account["email"],
                "status": account["status"],
                "challenge_count": account.get("challenge_count", 0),
                "requests_count": account.get("requests_count", 0),
                "last_used": account.get("last_used"),
                "blocked_until": account.get("blocked_until"),
                "is_available": False
            }
            
            # Verificar se está disponível
            if account["status"] == "active":
                is_blocked = False
                if account.get("blocked_until"):
                    blocked_until = datetime.fromisoformat(account["blocked_until"])
                    is_blocked = current_time < blocked_until
                
                if not is_blocked:
                    account_status["is_available"] = True
                    status["active_accounts"] += 1
                else:
                    status["blocked_accounts"] += 1
            else:
                status["blocked_accounts"] += 1
            
            status["accounts"].append(account_status)
        
        return status
