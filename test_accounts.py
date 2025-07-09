#!/usr/bin/env python3
"""
Script para testar o sistema de gerenciamento de múltiplas contas do LinkedIn
"""

import requests
import json
import time

def test_account_system():
    """Testa o sistema de múltiplas contas"""
    base_url = "http://localhost:8080"
    
    print("=== Testando Sistema de Múltiplas Contas LinkedIn ===\n")
    
    # 1. Verificar status das contas
    print("1. Verificando status das contas...")
    try:
        response = requests.get(f"{base_url}/api/accounts/status")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                accounts_info = data['data']
                print(f"✅ Total de contas: {accounts_info['total_accounts']}")
                print(f"✅ Contas ativas: {accounts_info['active_accounts']}")
                print(f"✅ Contas bloqueadas: {accounts_info['blocked_accounts']}")
                print(f"✅ Conta atual: {accounts_info['current_account']}")
                
                print("\nDetalhes das contas:")
                for account in accounts_info['accounts']:
                    status_icon = "✅" if account['is_available'] else "❌"
                    print(f"  {status_icon} {account['id']}: {account['email']}")
                    print(f"      Status: {account['status']}")
                    print(f"      Challenges: {account['challenge_count']}")
                    print(f"      Requests: {account['requests_count']}")
                    if account['last_used']:
                        print(f"      Último uso: {account['last_used']}")
                    if account['blocked_until']:
                        print(f"      Bloqueada até: {account['blocked_until']}")
                    print()
            else:
                print(f"❌ Erro: {data['message']}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    
    print("-" * 60)
    
    # 2. Testar conversão URN (operação simples)
    print("2. Testando conversão URN (não requer autenticação)...")
    try:
        response = requests.get(f"{base_url}/api/urn-to-url", 
                               params={'urn': 'urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU'})
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"✅ URN convertida: {data['data']['url']}")
            else:
                print(f"❌ Erro: {data['message']}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("-" * 60)
    
    # 3. Testar busca de pessoas (requer autenticação)
    print("3. Testando busca de pessoas (requer autenticação e rotação de contas)...")
    try:
        response = requests.get(f"{base_url}/api/search/people", 
                               params={'keywords': 'software engineer'})
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"✅ Busca realizada com sucesso")
                if isinstance(data['data'], list):
                    print(f"   Resultados encontrados: {len(data['data'])}")
                else:
                    print(f"   Dados retornados: {type(data['data'])}")
            else:
                print(f"❌ Erro na busca: {data['message']}")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("-" * 60)
    
    # 4. Verificar status das contas após operações
    print("4. Verificando status das contas após operações...")
    try:
        response = requests.get(f"{base_url}/api/accounts/status")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                accounts_info = data['data']
                print(f"✅ Conta atual após operações: {accounts_info['current_account']}")
                
                print("\nUso das contas:")
                for account in accounts_info['accounts']:
                    if account['requests_count'] > 0:
                        print(f"  📊 {account['id']}: {account['requests_count']} requests")
            else:
                print(f"❌ Erro: {data['message']}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("-" * 60)
    
    # 5. Testar múltiplas requisições para verificar rotação
    print("5. Testando múltiplas requisições para verificar rotação...")
    for i in range(3):
        print(f"   Requisição {i+1}...")
        try:
            response = requests.get(f"{base_url}/api/urn-to-url", 
                                   params={'urn': f'urn:li:company:123456{i}'})
            if response.status_code == 200:
                print(f"   ✅ Requisição {i+1} bem-sucedida")
            else:
                print(f"   ❌ Requisição {i+1} falhou: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro na requisição {i+1}: {e}")
        
        # Pequeno delay entre requisições
        time.sleep(1)

def simulate_challenge_scenario():
    """Simula um cenário de challenge para testar a rotação"""
    print("\n=== Simulando Cenário de Challenge ===\n")
    
    base_url = "http://localhost:8080"
    
    # Fazer várias requisições rápidas para tentar provocar um challenge
    print("Fazendo requisições rápidas para testar resistência a challenges...")
    
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/api/search/people", 
                                   params={'keywords': f'test{i}'})
            if response.status_code == 200:
                print(f"✅ Requisição {i+1} bem-sucedida")
            else:
                print(f"❌ Requisição {i+1} falhou: {response.status_code}")
                
            # Verificar status das contas após cada requisição
            status_response = requests.get(f"{base_url}/api/accounts/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                if status_data['status'] == 'success':
                    current = status_data['data']['current_account']
                    blocked = status_data['data']['blocked_accounts']
                    print(f"   Conta atual: {current}, Bloqueadas: {blocked}")
            
        except Exception as e:
            print(f"❌ Erro na requisição {i+1}: {e}")
        
        # Delay curto
        time.sleep(2)

if __name__ == "__main__":
    # Executar testes básicos
    test_account_system()
    
    # Perguntar se deve executar teste de challenge
    try:
        response = input("\nDeseja executar teste de challenge? (s/n): ")
        if response.lower() in ['s', 'sim', 'y', 'yes']:
            simulate_challenge_scenario()
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    
    print("\n=== Testes concluídos ===")
    print("Para monitorar as contas em tempo real, use:")
    print("curl http://localhost:8080/api/accounts/status | jq '.'")
