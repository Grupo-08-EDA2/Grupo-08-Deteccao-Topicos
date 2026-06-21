from src import dados

def main():
    print("[1/4] Carregando chamados...")
    chamados = dados.carregar_chamados()
    print(f"      {len(chamados)} chamados carregados.")

if __name__ == "__main__":
    main()
