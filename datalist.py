import csv
import customtkinter as ctk
import pandas as pd
import time

from IPython.display import display
from tkinter import *
from tkinter.ttk import *

sleepTime = 3
global customSize
customSize = "400x400"
maxDataFrameSize = 500000

States = ["Selecione o estado",
          "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", 
          "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
          "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

# estabelecimentoList = {'CNPJ':[],'Nome Fantasia':[], 'Situação Cadastral': [],
#                        'Data da Situacao Cadastral':[], 'Motivo Situacao Cadastral':[], 
#                        'Nome da Cidade no Exterior':[], 'País':[], 'Data de Início Atividade':[], 
#                        'CNAE Principal':[], 'CNAE Secundario':[], 'Endereço':[], 
#                        'Bairro':[], 'Cidade':[], 'Estado':[], 'CEP':[], 'DDD1':[], 'Telefone 1':[],
#                        'DDD2':[], 'Telefone 2':[], 'DDDFAX':[], 'FAX':[], 'Email':[], 'Situacao Especial':[],
#                        'Data da Situacao Especial':[]}

situacaoCadastral = {
    'NULA': 1,
    'ATIVA':2, 
    'SUSPENSA':3, 
    'INAPTA':4, 
    'BAIXADA':8
}

cabecalho = [
    'CNPJ_Raiz',
    'CNPJ_Ordem',
    'CNPJ_DV',
    'ID_Matriz_Filial',
    'Nome_Fantasia', 
    'Situacao_Cadastral',
    'Data_da_Situacao_Cadastral', 
    'Motivo_Situacao_Cadastral', 
    'Nome_da_Cidade_no_Exterior', 
    'Pais', 
    'Data_de_Inicio_Atividade', 
    'CNAE_Principal', 
    'CNAE_Secundario', 
    'Tipo_de_Logradouro',
    'Logradouro', 
    'Numero', 
    'Complemento', 
    'Bairro', 
    'CEP', 
    'Estado', 
    'Cod_Cidade', 
    'DDD1', 
    'Telefone_1', 
    'DDD2', 
    'Telefone_2', 
    'DDDFAX', 
    'FAX', 
    'Email', 
    'Situacao_Especial', 
    'Data_da_Situacao_Especial'
]

cabecalhoEmpresas = [
    'CNPJ_Raiz', 
    'Razao_Social', 
    'Natureza_Juridica', 
    'Qualificacao_do_Responsavel', 
    'Capital_Social', 
    'Porte da Empresa', 
    'Ente Federativo Responsavel'
]

cabecalhoSimples = [
    'CNPJ_Raiz',
    'Opcao_pelo_Simples',
    'Data_de_Opcao_pelo_Simples',
    'Data_de_Exclusao_do_Simples',
    'Opcao_pelo_MEI',
    'Data_de_Opcao_pelo_MEI',
    'Data_de_Exclusao_do_MEI'
]

columns = [
    'Cod_Cidade', 
    'Cidade'
]

def buscar():
    
    #Le as informaçoes preenchidas na tela de busca
    State = fieldState.get()
    City = fieldCity.get()
    CNAE1 = fieldCNAE.get()
    archive = pd.DataFrame()
    progresso = 5
    
    #Carrega a tabela de referencia para identificar o municipio a partir do seu codigo
    referencia = pd.read_csv(
        'municipios.csv', 
        names=columns, 
        header=None, 
        index_col=False, 
        sep=';'
    )
    referencia.info()

    for i in range(10):
        #Abre cada arquivo EstabelecimentosX
        data = pd.read_csv(
            f'Estabelecimentos{i}.csv', 
            dtype=object, 
            names=cabecalho, 
            header=None, 
            index_col=False, 
            sep=';', 
            encoding='Latin-1'
        )   
        display(data)
        data.info()

        #Altera o tipo da coluna 'Situação Cadastral'
        data['Situacao_Cadastral'] = data['Situacao_Cadastral'].astype('Int16')
        data.info()
        
        #Altera o tipo da coluna 'Cod_Cidade'
        data['Cod_Cidade'] = data['Cod_Cidade'].astype('int64')
        
        #Busca apenas pelas empresas que estão ativas
        data.query('Situacao_Cadastral == 2', inplace=True)
        
        print(data)

        #Filtro por estado caso tenha sido preenchido na tela inicial
        if State:
            data.query(
                'Estado == @State', 
                inplace=True
            )
            print(data)

        #Filtro por cidade caso tenha sido preenchido na tela inicial
        if City:
            if i == 0:
                #Converte nome da cidade em código
                citiesList = pd.read_csv(
                    'Municipios.csv', 
                    names=columns, 
                    header=None, 
                    index_col=False,
                    sep=';'
                )

                citiesList.query(
                    'Cidade == @City', 
                    inplace=True
                )
                print(citiesList)

                City = citiesList.iloc[0]['Cod_Cidade']
                City = str(City)
            
            #Filtro por cidade utilizando o código de referencia
            data.query(
                'Cidade == @City', 
                inplace=True
            )
            print(data)

        #Filtro por CNAE caso tenha sido preenchido na tela inicial
        if CNAE1:
            search = data[data['CNAE_Principal'].str.startswith(CNAE1)]
            search = search[~search['Nome_Fantasia'].isna()]
            print(search)
        else:
            search = data[~data['Nome_Fantasia'].isna()]
        
        #Substitui código de matriz, pela palavra "Matriz" e código de filial pela palavra "Filial"
        search['ID_Matriz_Filial'].replace('1', 'Matriz', inplace=True)
        search['ID_Matriz_Filial'].replace('2', 'Filial', inplace=True)

        display(referencia)

        #Puxa os nomes das cidades para o dataframe que será convertido em csv
        search = pd.merge(
            search, 
            referencia, 
            on='Cod_Cidade', 
            how='left'
        )
        display(search)

        #Concatena o resultado da ultima busca no df que irá gerar o arquivo ao final do loop
        archive = pd.concat([archive, search])
        archive.info()
        display(archive)
        
    #Puxar as informações contidas nas tabelas "EmpresasX"
    dfEmpresas = pd.read_csv(
        'Empresas0.csv', 
        dtype=object, 
        names=cabecalhoEmpresas, 
        header=None, 
        index_col=False, 
        sep=';', 
        encoding='Latin-1'
    )

    for k in range(1, 10):
        dfAux = pd.read_csv(
            f'Empresas{k}.csv', 
            dtype=object, 
            names=cabecalhoEmpresas, 
            header=None, 
            index_col=False, 
            sep=';', 
            encoding='Latin-1'
        )

        dfEmpresas = pd.concat([dfEmpresas, dfAux])

    #*******************************************************
    #Puxar as informações contidas na tabela "Simples.csv"
    #*******************************************************
    dfSimples = pd.read_csv(
        'Simples.csv', 
        dtype=object, 
        names=cabecalhoSimples, 
        header=None, 
        index_col=False, 
        sep=';', 
        encoding='Latin-1'
    )

    #Inclui as informações das empresas
    archive =   pd.merge(
        archive, 
        dfEmpresas, 
        on='CNPJ_Raiz', 
        how='left'
                
    )

    #Inclui as informações do Simples
    archive =   pd.merge(
        archive, 
        dfSimples, 
        on='CNPJ_Raiz', 
        how='left'
                
    )
    
    archive.info()
    display(archive)

    #Substitui código de porte, pelo porte da empresa
    archive['Porte da Empresa'].replace(
        '00', 
        'NAO INFORMADO', 
        inplace=True
    )

    archive['Porte da Empresa'].replace(
        '01', 
        'ME', 
        inplace=True
    )

    archive['Porte da Empresa'].replace(
        '03', 
        'EPP', 
        inplace=True
    )

    archive['Porte da Empresa'].replace(
        '05', 
        'DEMAIS', 
        inplace=True
    )
    
    # Adicionar contato da empresa
    for row in archive:
        if (archive[row, 'Telefone_1'] > 70000000) and (archive[row, 'Telefone_1'] < 900000000):
            archive[row, 'Contato'] = '+55' + archive[row, 'DDD1'].astype(str) + '9' + archive[row, 'Telefone_1'].astype(str)
        else:
            archive[row, 'Contato'] = '+55' + archive[row, 'DDD1'].astype(str) + archive[row, 'Telefone_1'].astype(str)

    archive.to_csv(
        'contatos_' + State + '_' + 'CNAE' + CNAE1 + '.csv', 
        sep=';', 
        index=False, 
        columns=[
            'CNPJ_Raiz', 
            'Razao_Social', 
            'ID_Matriz_Filial',
            'Nome_Fantasia', 
            'Data_de_Inicio_Atividade', 
            'Tipo_de_Logradouro', 
            'Logradouro', 
            'Numero', 
            'Complemento', 
            'Bairro', 
            'CEP', 
            'Estado', 
            'Cidade', 
            'CNAE_Principal', 
            'CNAE_Secundario', 
            'DDD1', 
            'Telefone_1', 
            'DDD2', 
            'Telefone_2', 
            'Email', 
            'Capital_Social', 
            'Porte da Empresa',
            'Opcao_pelo_Simples'
        ]       
    )
        
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
window = ctk.CTk()
window.geometry(customSize)
window.title("Contatos - Portal da Transparência")

label = ctk.CTkLabel(
    window, 
    text="Busca de Empresas - Portal da Transparência"        
)

label.pack()

labelState = ctk.CTkLabel(
    window, 
    text="Estado"               
)

labelState.pack()

fieldState = ctk.CTkComboBox(
    window, 
    values = States, 
    width=200
)
fieldState.set("Selecione o estado")
fieldState.pack()

labelCity = ctk.CTkLabel(
    window, 
    text="Cidade"
)
labelCity.pack()

fieldCity = ctk.CTkEntry(
    window, 
    placeholder_text='Cidade', 
    width=200
)
fieldCity.pack()

labelCNAE = ctk.CTkLabel(
    window, 
    text="CNAE"
)
labelCNAE.pack()

fieldCNAE = ctk.CTkEntry(
    window, 
    placeholder_text='CNAE (apenas números)',
    width=200
)
fieldCNAE.pack()

button = ctk.CTkButton(
    window, 
    text="Buscar", 
    command=buscar, 
    width=200
)
button.pack(padx=20, pady=20)

progressBar = ctk.CTkProgressBar(
    window, 
    width=250, 
    height=10, 
    mode='indeterminate'
)
progressBar.pack(
    padx=30, 
    ady=30
)

window.mainloop()