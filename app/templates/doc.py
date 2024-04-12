import os
import re
import dash
import shutil
import tempfile
from flask import send_file, send_from_directory
import dash_bootstrap_components as dbc
from dash import html, Input, Output, dcc, dash, callback_context
from dash.exceptions import PreventUpdate
import dash_html_components as html
from app import app

# Constantes
NETWORK_DIRECTORY_PATH = r'\\192.168.0.253\publico\Joseane (Arquivo Engenharia)\00 Envio DOC. SST e RH\00 DOC. SST e RH'

APP = dash.Dash(__name__, external_stylesheets=["style.css", dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, url_base_pathname="/remessa/", server=app)
server = APP.server

# Layout da página principal
main_layout = html.Div(
    [
        html.H1('Página de Cópias de Documentos', className='titulo-principal'),
        # Aqui você pode adicionar o layout da sua página de cópias de documentos
    ],
    className='container-fluid imgbg',
)

APP.title = "Remessa de Documentos"

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
        folder_structure = []
        sub_folders = []
        files = []

        for item in sorted(os.listdir(root)):
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
                        html.A("Download Pasta", href=f'/download-folder/{file_path_relative}', download=item, className='botao-download', id=folder_download_id),
                        html.Div(sub_folder_content, className='estrutura'),
                    ], className='item-pasta')
                ], open=False, className='item-pasta'))

            else:
                clean_file_id = clean_filename(item)
                file_path_relative = os.path.relpath(item_path, NETWORK_DIRECTORY_PATH)
                download_id = f'download-{clean_file_id}'
                files.append(html.Div([
                    html.I(className="far fa-file", style={'margin-right': '5px'}),
                    html.A(f" {item}", href=f'/download/{file_path_relative}', download=item, className='botao-download', id=download_id)
                ], className='item-arquivo'))

        folder_structure.extend(sub_folders)
        folder_structure.extend(files)
        return folder_structure

    return build_tree(path)

# Modal para mensagens
modal_atualizar = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Saudações,")),
    dbc.ModalBody([
        html.P("É um prazer recebê-lo(a) aqui. Seu download iniciará em instantes! "),
        html.P("O download de alguns arquivos pode levar algum tempo para iniciar; por favor, tenha paciência."),
        html.P("Não compartilhe dados com terceiros sem autorização.")]),
], id="modal-atualizar", is_open=False)

# Modal para mensagens de download
modal_download = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Download de Pasta")),
    dbc.ModalBody(html.P("O download da pasta foi iniciado!")),
], id="modal-download", is_open=False)

# Define o layout inicial
APP.layout = main_layout

APP.layout = html.Div(
    [
        html.Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
        html.Div(
            [
                html.Img(
                    src=APP.get_asset_url('img/LOGO_paisagem.png'),
                    className='logo-img img-fluid'
                ),
                html.H1('Documentação mobilização RH e SST - UFV SABESP', className='titulo-principal'),
                html.A(html.Button('Logout', id='btn-logout', className='botao-logout'), href='/login'),
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
        modal_atualizar,
        modal_download,
        html.Footer(
            [
                html.Div([
                    html.P('CÁPUA ENGENHARIA', className='font-rodape-title'),
                    ], className='info-contato'),

                html.Div([
                    html.P('André Gondim © 2024', className='font-rodape'),
                ], className='creditos-desenvolvedor'),
                html.Div([
                    html.A(
                        html.Img(src=APP.get_asset_url("img/pin.png")),
                        href="https://maps.app.goo.gl/AETsHhsox8qcbbLk8", target="_blank", className='font-rodape'
                    ),
                    
                    html.A(
                        html.Img(src=APP.get_asset_url("img/facebook.png")),
                        href="https://www.facebook.com/capuamarketing", target="_blank", className='font-rodape'
                    ),
                    
                    html.A(
                        html.Img(src=APP.get_asset_url("img/linkedin.png")),
                        href="https://br.linkedin.com/company/c-pua-projetos", target="_blank", className='font-rodape'
                    ),
                    html.A(
                        html.Img(src=APP.get_asset_url("img/www.png")),
                        href="http://capua.com.br/", target="_blank", className='font-rodape'
                    ),
                ], className='redes-sociais')
            ],
            className='rodape'
        )
    ],
    className='container-fluid imgbg',
)

# Callback para abrir o modal de atualização
@APP.callback(
    Output('modal-atualizar', 'is_open'),
    [Input('btn-atualizar', 'n_clicks')],
    prevent_initial_call=True,
)
def open_modal_atualizar(btn_atualizar_clicks):
    return True

# Callback para abrir o modal de download
@APP.callback(
    [Output('modal-download', 'is_open'),
     Output('modal-download', 'children')],
    [Input('download-folder-', 'n_clicks')],
    prevent_initial_call=True,
)
def open_modal_download(download_clicks):
    return True, "O download da pasta foi iniciado!"

# Callback para atualizar a lista de pastas
@APP.callback(
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

# Adicione a rota para download de pasta
@APP.server.route("/download-folder/<path:foldername>")
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

# Adicione a rota para download de arquivo
@APP.server.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(NETWORK_DIRECTORY_PATH, filename, as_attachment=True)

if __name__ == '__main__':
    APP.run(debug=False)