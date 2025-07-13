#!/usr/bin/env python3
"""
Script para executar todos os testes da aplicação Moveix
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o resultado"""
    print(f"\n{'='*60}")
    print(f"Executando: {description}")
    print(f"Comando: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("✅ SUCESSO")
            print(result.stdout)
        else:
            print("❌ FALHA")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False
    
    return True

def main():
    """Função principal para executar todos os testes"""
    
    print("🚀 Iniciando execução de todos os testes do Moveix")
    print(f"Diretório atual: {os.getcwd()}")
    
    # Lista de testes para executar
    tests = [
        {
            "command": "python -m pytest app/tests/test_payments.py -v",
            "description": "Testes de Pagamentos"
        },
        {
            "command": "python -m pytest app/tests/test_services.py -v",
            "description": "Testes de Services"
        },
        {
            "command": "python -m pytest app/tests/test_routes.py -v",
            "description": "Testes de Routes"
        },
        {
            "command": "python -m pytest app/tests/test_integration.py -v",
            "description": "Testes de Integração"
        },
        {
            "command": "python -m pytest app/tests/ -v --tb=short",
            "description": "Todos os Testes"
        }
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test in tests:
        if run_command(test["command"], test["description"]):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"RESUMO DOS TESTES")
    print(f"{'='*60}")
    print(f"Testes executados: {total_tests}")
    print(f"Sucessos: {success_count}")
    print(f"Falhas: {total_tests - success_count}")
    
    if success_count == total_tests:
        print("🎉 Todos os testes passaram!")
        return 0
    else:
        print("⚠️  Alguns testes falharam!")
        return 1

def run_specific_test(test_name):
    """Executa um teste específico"""
    test_map = {
        "payments": "app/tests/test_payments.py",
        "services": "app/tests/test_services.py",
        "routes": "app/tests/test_routes.py",
        "integration": "app/tests/test_integration.py",
        "all": "app/tests/"
    }
    
    if test_name not in test_map:
        print(f"❌ Teste '{test_name}' não encontrado!")
        print(f"Testes disponíveis: {', '.join(test_map.keys())}")
        return 1
    
    test_path = test_map[test_name]
    command = f"python -m pytest {test_path} -v"
    
    return run_command(command, f"Teste: {test_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Executa um teste específico
        test_name = sys.argv[1]
        exit(run_specific_test(test_name))
    else:
        # Executa todos os testes
        exit(main()) 