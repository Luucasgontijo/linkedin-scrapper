#!/bin/bash

# Script para testar o endpoint de conversão URN para URL
# Usage: ./test-urn-to-url.sh

echo "=== Testando endpoint de conversão URN para URL ==="
echo

# Definir a URL base da API
BASE_URL="http://localhost:8080"

# Teste 1: URN de pessoa
echo "Teste 1: URN de pessoa"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 2: URN de empresa
echo "Teste 2: URN de empresa"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:company:123456" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 3: URN de escola
echo "Teste 3: URN de escola"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:school:789012" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 4: URN de organização
echo "Teste 4: URN de organização"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:organization:345678" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 5: URN de skill
echo "Teste 5: URN de skill"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:skill:987654" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 6: URN de post
echo "Teste 6: URN de post"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=urn:li:post:654321" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 7: ID de perfil direto
echo "Teste 7: ID de perfil direto"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 8: URN inválida
echo "Teste 8: URN inválida"
curl -X GET "${BASE_URL}/api/urn-to-url?urn=invalid:urn:format" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

# Teste 9: Sem parâmetro URN
echo "Teste 9: Sem parâmetro URN"
curl -X GET "${BASE_URL}/api/urn-to-url" \
  -H "Content-Type: application/json" | jq '.'
echo
echo "---"

echo "=== Testes concluídos ==="
