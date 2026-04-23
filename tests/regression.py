import subprocess
import sys

def run_tests():
    print("Iniciando testes de regressão...")
    # Por enquanto, apenas verifica se o ambiente está ok
    try:
        import fastapi
        import whisper
        print("Dependências básicas encontradas.")
    except ImportError as e:
        print(f"Erro: Dependência não encontrada - {e}")
        # Não falha ainda pois as dependências serão instaladas na Task 1
    
    # Executa pytest se existir
    result = subprocess.run(["pytest"], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0 and "no tests ran" not in result.stdout:
        print("Falha nos testes!")
        sys.exit(1)
    print("Testes concluídos com sucesso.")

if __name__ == "__main__":
    run_tests()
