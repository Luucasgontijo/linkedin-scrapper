"""
LinkedIn Account Manager
Manages multiple LinkedIn accounts with automatic rotation and challenge detection
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from linkedin_api import Linkedin

logger = logging.getLogger(__name__)

class LinkedInAccountManager:
    def __init__(self, accounts_file: str = "accounts.json"):
        self.accounts_file = accounts_file
        self.accounts_data = self.load_accounts()
        self.current_account_index = 0
        self.linkedin_api = None
        self.current_account = None
        
    def load_accounts(self) -> dict:
        """Load accounts configuration from JSON file"""
        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"File {self.accounts_file} not found")
            return {"accounts": [], "settings": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return {"accounts": [], "settings": {}}
    
    def save_accounts(self):
        """Save accounts configuration to JSON file"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving accounts: {e}")
    
    def get_available_accounts(self) -> List[dict]:
        """Get list of available accounts (not blocked)"""
        available = []
        current_time = datetime.now()
        
        for account in self.accounts_data["accounts"]:
            if account["status"] != "active":
                continue
                
            # Check if account is temporarily blocked
            if account.get("blocked_until"):
                blocked_until = datetime.fromisoformat(account["blocked_until"])
                if current_time < blocked_until:
                    continue
                else:
                    # Remove block if time has passed
                    account["blocked_until"] = None
                    account["challenge_count"] = 0
            
            # Check hourly request limit
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
        """Get next available account based on rotation strategy"""
        available_accounts = self.get_available_accounts()
        
        if not available_accounts:
            logger.warning("No accounts available")
            return None
        
        strategy = self.accounts_data.get("settings", {}).get("rotation_strategy", "round_robin")
        
        if strategy == "round_robin":
            if self.current_account_index >= len(available_accounts):
                self.current_account_index = 0
            account = available_accounts[self.current_account_index]
            self.current_account_index = (self.current_account_index + 1) % len(available_accounts)
        elif strategy == "least_used":
            account = min(available_accounts, key=lambda x: x.get("requests_count", 0))
        else:
            account = available_accounts[0]
        
        return account
    
    def mark_challenge(self, account_id: str):
        """Mark an account as having faced a challenge"""
        for account in self.accounts_data["accounts"]:
            if account["id"] == account_id:
                account["challenge_count"] = account.get("challenge_count", 0) + 1
                cooldown_minutes = self.accounts_data.get("settings", {}).get("challenge_cooldown_minutes", 60)
                max_retries = self.accounts_data.get("settings", {}).get("max_challenge_retries", 3)
                
                if account["challenge_count"] >= max_retries:
                    blocked_until = datetime.now() + timedelta(minutes=cooldown_minutes)
                    account["blocked_until"] = blocked_until.isoformat()
                    account["status"] = "blocked"
                    logger.warning(f"Account {account_id} blocked until {blocked_until}")
                
                self.save_accounts()
                break
    
    def mark_request(self, account_id: str):
        """Mark a request made by the account"""
        for account in self.accounts_data["accounts"]:
            if account["id"] == account_id:
                current_time = datetime.now()
                
                if not account.get("requests_reset_time"):
                    account["requests_reset_time"] = (current_time + timedelta(hours=1)).isoformat()
                    account["requests_count"] = 0
                
                account["requests_count"] = account.get("requests_count", 0) + 1
                account["last_used"] = current_time.isoformat()
                
                self.save_accounts()
                break
    
    def initialize_api(self, max_retries: int = 3) -> bool:
        """Initialize LinkedIn API with account rotation"""
        retry_count = 0
        
        while retry_count < max_retries:
            account = self.get_next_account()
            
            if not account:
                logger.error("No accounts available for authentication")
                return False
            
            try:
                logger.info(f"Trying to authenticate with account: {account['id']}")
                
                self.linkedin_api = Linkedin(account["email"], account["password"])
                self.current_account = account
                
                self.mark_request(account["id"])
                
                logger.info(f"Authentication successful with account: {account['id']}")
                return True
                
            except Exception as e:
                error_message = str(e).lower()
                
                # Detect common challenges
                if any(keyword in error_message for keyword in [
                    "challenge", "captcha", "verification", "suspicious", 
                    "unusual activity", "security check", "verify"
                ]):
                    logger.warning(f"Challenge detected for account {account['id']}: {e}")
                    self.mark_challenge(account["id"])
                else:
                    logger.error(f"Authentication error for account {account['id']}: {e}")
                
                retry_count += 1
                
                delay = self.accounts_data.get("settings", {}).get("request_delay_seconds", 2)
                time.sleep(delay)
        
        logger.error("Authentication failed after all attempts")
        return False
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute a function with automatic retry and account rotation"""
        max_retries = self.accounts_data.get("settings", {}).get("retry_attempts", 3)
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if not self.linkedin_api:
                    if not self.initialize_api():
                        raise Exception("Failed to initialize API")
                
                if self.current_account:
                    self.mark_request(self.current_account["id"])
                
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_message = str(e).lower()
                retry_count += 1
                
                logger.warning(f"Execution error (attempt {retry_count}): {e}")
                
                # Detect challenges or problems requiring rotation
                if any(keyword in error_message for keyword in [
                    "challenge", "captcha", "verification", "suspicious",
                    "unusual activity", "security check", "verify",
                    "rate limit", "too many requests", "blocked"
                ]):
                    if self.current_account:
                        self.mark_challenge(self.current_account["id"])
                    
                    if retry_count < max_retries:
                        logger.info("Trying next account...")
                        if not self.initialize_api():
                            break
                else:
                    delay = self.accounts_data.get("settings", {}).get("request_delay_seconds", 2)
                    time.sleep(delay)
        
        raise Exception(f"Failed after {max_retries} attempts")
    
    def get_api(self):
        """Get current LinkedIn API instance"""
        if not self.linkedin_api:
            if not self.initialize_api():
                return None
        return self.linkedin_api
    
    def get_account_status(self) -> dict:
        """Get status of all accounts"""
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
