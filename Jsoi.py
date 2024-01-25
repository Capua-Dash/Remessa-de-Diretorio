import os
import re
import dash
import shutil
import tempfile
from flask import send_file, send_from_directory
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, dcc, ctx

# Constantes
NETWORK_DIRECTORY_PATH = r'\\192.168.0.253\publico\Joseane (Arquivo Engenharia)\_Envio DOC. SST e RH\@DOC. SST e RH _ PADRAO'

app = dash.Dash(__name__, external_stylesheets=["style.css", dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

HelloWorld = False

idx = 0

# Função para limpar nomes de arquivos
def clean_filename(name):
    """Remove caracteres especiais do nome do arquivo."""
    return re.sub(r'[^\w\s]', '_', name)

# Teste de acesso ao diretório de rede
def check_network_directory():
    """Verifica se o diretório de rede está acessível."""
    return os.path.exists(NETWORK_DIRECTORY_PATH)

# Teste de permissões de leitura
def check_read_permissions(path):
    """Verifica se as permissões de leitura são concedidas para o diretório."""
    test_file = os.path.join(path, 'test.txt')
    try:
        with open(test_file, 'w') as file:
            file.write('test')
        os.remove(test_file)
        return True
    except PermissionError as e:
        print(f"Erro de permissão ao acessar ou modificar o diretório: {e}")
        return False
    except Exception as e:
        print(f"Erro ao acessar ou modificar o diretório: {e}")
        return False

# Função para gerar a estrutura de pastas
def generate_folder_structure(path):
    """Gera a estrutura de pastas e arquivos."""
    def build_tree(root):
        global idx
        folder_structure = []
        sub_folders = []
        files = []

        for i, item in enumerate(sorted(os.listdir(root))):
            print(i)
            item_path = os.path.join(root, item)

            if os.path.isdir(item_path):
                sub_folder_content = build_tree(item_path)
                clean_file_id = clean_filename(item)
                file_path_relative = os.path.relpath(item_path, NETWORK_DIRECTORY_PATH)

                # Adiciona link para download da pasta
                folder_download_id = f'download-folder-{clean_file_id}'
                sub_folders.append(html.Details([
                    html.Summary(f"{item}", className='mouse'),
                    html.Div([
                        html.A("Download Pasta", href=f'/download-folder/{file_path_relative}', download=item, className='botao-download', id=f'download_id_{i}'),
                        html.Div(sub_folder_content, className='estrutura'),
                    ], className='item-pasta')
                ], open=False, className='item-pasta'))

            else:
                clean_file_id = clean_filename(item)
                file_path_relative = os.path.relpath(item_path, NETWORK_DIRECTORY_PATH)
                download_id = f'download-{clean_file_id}'
                files.append(html.Div([
                    html.I(className="far fa-file", style={'margin-right': '5px'}),
                    html.A(f" {item}", href=f'/download/{file_path_relative}', download=item, className='botao-download')
                ], className='item-arquivo'))

        idx = len(sub_folders)            
        folder_structure.extend(sub_folders)
        folder_structure.extend(files)
        return folder_structure

    return build_tree(path)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src='assets/img/LOGO_paisagem.png',
                    className='logo-img img-fluid'
                ),
                html.H1('Remessa de Documentos - UFV SABESP', className='titulo-principal'),
                html.Button('Atualizar Lista', id='btn-atualizar', className='botao-atualizar'),
                dcc.Loading(
                    id="loading-1",
                    children=[
                        html.Div(id='lista-pastas', className='margem-rodape'),
                    ],
                    type="default", className='loading'
                ),
            ],
            className='container-rodape' 
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Teste")),
                dbc.ModalBody("This is the content of the modal", id='Hello'),
            ],
            id="modal_id",
            is_open=False,
        ),
        html.Footer(
            [
                html.P('Criado por André Gondim', className='font-rodape'),
                html.P('2024', className='font-rodape')
            ],
            className='rodape'  
        )
    ],
    className='container-fluid imgbg',
)

for i in range(idx):
    
    @app.callback(
        Output('modal_id', 'is_open'),
        Output('Hello', 'children'),
        [Input(f'download_id_{i}', 'n_clicks')],
        [State('btn-atualizar', 'n_clicks')],
        prevent_initial_call=True,
    )
    def downloadid(download_clicks, btn_atualizar_clicks):
        # Se o botão "Download Pasta" foi clicado, abre o modal
        if f'download_id_{i}' == ctx.triggered_id:
            HelloWorld = True
            return True, 'Quero retornar'
        # if 'download_id' == ctx.triggered_id:
        #     HelloWorld = False
        #     return True, 'Quero so ver'
        return False, None

# Adicione a rota para download
@app.server.route("/download-folder/<path:foldername>")
def download_folder(foldername):
    folder_path = os.path.join(NETWORK_DIRECTORY_PATH, foldername)

    try:
        # Cria um diretório temporário
        temp_dir = tempfile.mkdtemp()

        # Copia todo o conteúdo da pasta para o diretório temporário
        shutil.copytree(folder_path, os.path.join(temp_dir, foldername))

        # Cria o arquivo zip
        shutil.make_archive(temp_dir, 'zip', temp_dir)

        # Retorna o arquivo zip como um download
        return send_file(f"{temp_dir}.zip", as_attachment=True)

    except Exception as e:
        print(f"Erro ao criar o arquivo zip da pasta: {e}")
        return "Erro ao criar o arquivo zip da pasta."

# Adicione a rota para download
@app.server.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(NETWORK_DIRECTORY_PATH, filename, as_attachment=True)

@app.callback(
    Output('lista-pastas', 'children'),
    [Input('btn-atualizar', 'n_clicks')],
    prevent_initial_call=True
)
def update_folders(n_clicks):
    if not check_network_directory():
        return "O diretório de rede não está acessível."
    
    if not check_read_permissions(NETWORK_DIRECTORY_PATH):
        return "Permissões de leitura não concedidas."
    
    path = NETWORK_DIRECTORY_PATH
    structure = generate_folder_structure(path)
    return structure

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)