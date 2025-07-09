#!/usr/bin/env python3
"""
Exemplo de uso do endpoint de conversão URN para URL
"""

import requests
import json

def test_urn_to_url_endpoint():
    """Testa o endpoint de conversão URN para URL"""
    base_url = "http://localhost:8080"
    
    # Lista de URNs para testar
    test_urns = [
        "urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU",
        "urn:li:company:123456",
        "urn:li:school:789012",
        "urn:li:organization:345678",
        "urn:li:skill:987654",
        "urn:li:post:654321",
        "urn:li:activity:111222",
        "urn:li:industry:456789",
        "ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU",  # ID direto
        "invalid:urn:format"  # URN inválida
    ]
    
    print("=== Testando endpoint de conversão URN para URL ===\n")
    
    for i, urn in enumerate(test_urns, 1):
        print(f"Teste {i}: {urn}")
        
        try:
            response = requests.get(f"{base_url}/api/urn-to-url", params={'urn': urn})
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success':
                    print(f"✅ Sucesso: {data['data']['url']}")
                else:
                    print(f"❌ Erro: {data['message']}")
            else:
                print(f"❌ Erro HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
        
        print("-" * 50)
    
    # Teste sem parâmetro URN
    print("\nTeste sem parâmetro URN:")
    try:
        response = requests.get(f"{base_url}/api/urn-to-url")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ Erro: {e}")

def convert_urn_to_url(urn, base_url="http://localhost:8080"):
    """
    Função utilitária para converter URN em URL usando a API
    
    Args:
        urn (str): URN do LinkedIn para converter
        base_url (str): URL base da API
    
    Returns:
        str: URL convertida ou None se houver erro
    """
    try:
        response = requests.get(f"{base_url}/api/urn-to-url", params={'urn': urn})
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return data['data']['url']
        
        return None
        
    except Exception as e:
        print(f"Erro ao converter URN: {e}")
        return None

if __name__ == "__main__":
    # Executar testes
    test_urn_to_url_endpoint()
    
    # Exemplo de uso da função utilitária
    print("\n=== Exemplo de uso da função utilitária ===")
    
    example_urn = "urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU"
    url = convert_urn_to_url(example_urn)
    
    if url:
        print(f"URN: {example_urn}")
        print(f"URL: {url}")
    else:
        print("Não foi possível converter a URN")
