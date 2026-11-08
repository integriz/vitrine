"""Le a planilha publicada do Google e gera o arquivo produtos.json.

Roda sozinho no GitHub Actions (veja .github/workflows/atualizar.yml).
Nao precisa instalar nada: usa so a biblioteca padrao do Python.
"""
import csv
import io
import json
import sys
import urllib.request

# Link da planilha publicada na web (formato CSV)
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vS10VseRTkM6Vgd5B9SEs9nd0whVPHCpSAypaUpoS_t5gwYgQyWsHFrr7WLlOIBe-A7vdiCSvXzEO6y/pub?gid=0&single=true&output=csv"
)
# Endereco direto da planilha (atualiza em segundos). Usado primeiro; se falhar, usa o link publicado acima.
CSV_DIRETO = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vS10VseRTkM6Vgd5B9SEs9nd0whVPHCpSAypaUpoS_t5gwYgQyWsHFrr7WLlOIBe-A7vdiCSvXzEO6y/pub?gid=0&single=true&output=csv"
)
SAIDA = "produtos.json"


def baixar_csv():
    for url in (CSV_DIRETO, CSV_URL):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "vitrine-atualizador"})
            with urllib.request.urlopen(req, timeout=30) as r:
                texto = r.read().decode("utf-8")
            if not texto.lstrip().lower().startswith(("<!doctype", "<html")):
                return texto
        except Exception as e:
            print(f"Falhou em {url[:60]}...: {e}")
    sys.exit("Nao foi possivel ler a planilha por nenhum dos links.")


def url_segura(u):
    u = (u or "").strip()
    return u if u.lower().startswith(("http://", "https://")) else ""


def main():
    texto = baixar_csv()

    linhas = [l for l in csv.reader(io.StringIO(texto)) if any(c.strip() for c in l)]
    produtos = []
    # colunas: 0 = nome, 1 = link do Mercado Livre, 2 = imagem. Primeira linha = cabecalho.
    for l in linhas[1:]:
        titulo = (l[0] if len(l) > 0 else "").strip()
        link = url_segura(l[1] if len(l) > 1 else "")
        img = url_segura(l[2] if len(l) > 2 else "")
        if titulo and link:
            produtos.append({"titulo": titulo, "link": link, "img": img})

    produtos.reverse()  # ultima linha da planilha = produto mais novo, aparece primeiro

    if not produtos:
        # Protecao: nao apaga o site se a planilha vier vazia por algum erro
        sys.exit("Nenhum produto encontrado na planilha. Mantendo o produtos.json anterior.")

    with open(SAIDA, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=1)
    print(f"{len(produtos)} produtos gravados em {SAIDA}")


if __name__ == "__main__":
    main()
