import os

def listar_arquivos(caminho, nivel=0):
    # Adiciona espaços para representar a hierarquia
    prefixo = '  ' * nivel

    # Lista todos os arquivos e diretórios no caminho fornecido
    arquivos = os.listdir(caminho)

    for arquivo in arquivos:
        caminho_completo = os.path.join(caminho, arquivo)

        # Verifica se é um diretório
        if os.path.isdir(caminho_completo):
            print(f"{prefixo}[D] {arquivo}")
            # Chama a função recursivamente para listar os arquivos dentro do diretório
            listar_arquivos(caminho_completo, nivel + 1)
        else:
            print(f"{prefixo}[F] {arquivo}")

# Substitua '/caminho/do/seu/diretorio' pelo caminho do seu diretório
diretorio_do_projeto = '/home/brenosm/PycharmProjects/tracking-api/Clients'

# Chama a função para listar a estrutura do diretório
listar_arquivos(diretorio_do_projeto)
