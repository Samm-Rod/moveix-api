# health_check.py
import requests # type: ignore
import sys

def check_app_health():
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ app está funcionando!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ app retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a app: {e}")
        return False

if __name__ == "__main__":
    if check_app_health():
        sys.exit(0)
    else:
        sys.exit(1)