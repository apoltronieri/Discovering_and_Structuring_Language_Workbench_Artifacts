import json
import re

def filtrar_objetos_com_yes(entrada, saida):
    print("\n=== DEBUG: Início da execução ===")
    print(f"Arquivo de entrada: {entrada}")
    print(f"Arquivo de saída:   {saida}")

    # 1. Leitura do arquivo
    try:
        with open(entrada, "r", encoding="utf-8") as f:
            texto = f.read()
        print(f"DEBUG: Tamanho do arquivo lido: {len(texto)} caracteres")
    except FileNotFoundError:
        print("ERRO: Arquivo de entrada não encontrado.")
        return
    except Exception as e:
        print(f"ERRO ao ler arquivo: {e}")
        return

    # 2. Captura dos objetos JSON-like
    objetos_brutos = re.findall(r"\{[\s\S]*?\}", texto)
    print(f"DEBUG: Objetos capturados pelo regex: {len(objetos_brutos)}")

    if len(objetos_brutos) == 0:
        print("DEBUG: Nenhum objeto encontrado. Verifique o formato do arquivo.")
    
    objetos_validos = []

    # 3. Iteração e processamento
    for idx, obj_texto in enumerate(objetos_brutos):
        print(f"\n--- DEBUG OBJETO {idx+1}/{len(objetos_brutos)} ---")
        print(f"DEBUG: Primeiras 80 chars:\n{obj_texto[:80]}")

        linhas = obj_texto.splitlines()
        contem_yes = any('"url"' in linha and "yes" in linha for linha in linhas)

        print(f"DEBUG: Contém 'yes' na linha da URL? {contem_yes}")

        if contem_yes:
            obj_corrigido = obj_texto

            # 1. Remover tudo após a URL (comentários, yes, observações)
            obj_corrigido = re.sub(
                r'("url"\s*:\s*"[^"]*"),.*$',
                r'\1,',
                obj_corrigido,
                flags=re.MULTILINE
            )

            # 2. Remover ", yes" se ainda existir
            obj_corrigido = re.sub(
                r",\s*yes\s*$",
                "",
                obj_corrigido,
                flags=re.MULTILINE
            )

            # 3. Normalizar vírgulas penduradas
            obj_corrigido = re.sub(
                r",\s*$",
                ",",
                obj_corrigido,
                flags=re.MULTILINE
            )

            # 4. Validar JSON
            try:
                objeto_json = json.loads(obj_corrigido)
                objetos_validos.append(objeto_json)
                print("DEBUG: Objeto convertido com sucesso.")
            except json.JSONDecodeError as e:
                print("ERRO de JSON ao processar objeto corrigido:")
                print(obj_corrigido)
                print("Mensagem:", e)

    # 4. Escrita do arquivo final
    try:
        with open(saida, "w", encoding="utf-8") as f_out:
            json.dump(objetos_validos, f_out, indent=4, ensure_ascii=False)
        print("\n=== DEBUG: Escrita finalizada com sucesso ===")
    except Exception as e:
        print(f"ERRO ao salvar arquivo de saída: {e}")
        return

    print(f"Processo concluído. {len(objetos_validos)} objetos válidos gravados em {saida}.\n")


# Execução direta
if __name__ == "__main__":
    filtrar_objetos_com_yes("gabriel.json", "aprovado.json")