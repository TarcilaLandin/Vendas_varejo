import pandas as pd

# Funções para faixas de preço, idade e renda
def faixa_preco(preco):
    if preco < 500:
        return "até 500"
    elif preco < 1500:
        return "500 a 1.499"
    elif preco < 3000:
        return "1.500 a 2.999"
    elif preco < 5000:
        return "3.000 a 4.999"
    else:
        return "5.000 ou mais"

def faixa_idade(idade):
    if idade < 20:
        return "até 20"
    elif idade < 35:
        return "20 a 34"
    elif idade < 50:
        return "35 a 49"
    elif idade < 80:
        return "50 a 79"
    else:
        return "80 ou mais"

def faixa_renda(renda):
    if renda < 2000:
        return "até 2000"
    elif renda < 4000:
        return "2.000 a 3.999"
    elif renda < 10000:
        return "4.000 a 9.999"
    elif renda < 15000:
        return "10.000 a 14.999"
    else:
        return "15.000 ou mais"

def processar_dados():
    # Carregar os dados
    try:
        vendas = pd.read_excel("varejo.xlsx")
        cliente = pd.read_excel("cliente_varejo.xlsx")
    except FileNotFoundError as e:
        print(f"Erro ao carregar os arquivos: {e}")
        return None
    
    # Preprocessamento
    vendas["idcanalvenda"] = vendas["idcanalvenda"].str.replace("APP", "Aplicativo", regex=False)
    vendas["Nome_Departamento"] = vendas["Nome_Departamento"].str.replace(" ", "_", regex=False)
    vendas["estado"].fillna("MS", inplace=True)
    media_preco = vendas["Preço"].mean()
    vendas["Preço"].fillna(media_preco, inplace=True)
    
    # Filtrar a base para trazer somente os registros onde Preço < Preço_com_frete
    vendas_filtradas = vendas[vendas["Preço"] < vendas["Preço_com_frete"]]
    
    # Verificar e remover duplicações na base de clientes
    cliente = cliente.drop_duplicates(subset=['cliente_Log'])
    
    # Merge com cliente
    vendas_cliente = vendas_filtradas.merge(cliente, how="left", on="cliente_Log")
    
    # Adicionar as colunas de faixa ao DataFrame
    vendas_cliente['Faixa de Preço'] = vendas_cliente['Preço'].apply(faixa_preco)
    vendas_cliente['Faixa de Idade'] = vendas_cliente['idade'].apply(faixa_idade)
    vendas_cliente['Faixa de Renda'] = vendas_cliente['renda'].apply(faixa_renda)
    
    # Criar a variável Mês a partir da variável Data
    if 'Data' in vendas_cliente.columns:
        vendas_cliente['Data'] = pd.to_datetime(vendas_cliente['Data'], errors='coerce')
        vendas_cliente['Mes'] = vendas_cliente['Data'].dt.strftime('%b').str.upper()
        
        # Adicionar a coluna com o dia da semana em português
        vendas_cliente['Dia_da_Semana'] = vendas_cliente['Data'].dt.day_name()
        dias_da_semana = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        vendas_cliente['Dia_da_Semana'] = vendas_cliente['Dia_da_Semana'].map(dias_da_semana)
    else:
        vendas_cliente['Mes'] = 'Desconhecido'
        vendas_cliente['Dia_da_Semana'] = 'Desconhecido'
    
    # Adicionar a coluna com o nome do estado
    uf_to_estado = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapá', 'BA': 'Bahia', 'CE': 'Ceará',
        'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás', 'MA': 'Maranhão', 'MG': 'Minas Gerais',
        'MS': 'Mato Grosso do Sul', 'MT': 'Mato Grosso', 'PA': 'Pará', 'PB': 'Paraíba', 'PE': 'Pernambuco',
        'PI': 'Piauí', 'PR': 'Paraná', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RO': 'Rondônia',
        'RR': 'Roraima', 'RS': 'Rio Grande do Sul', 'SC': 'Santa Catarina', 'SE': 'Sergipe', 'SP': 'São Paulo',
        'TO': 'Tocantins'
    }
    vendas_cliente['Nome_Estado'] = vendas_cliente['estado'].map(uf_to_estado)
    
    # Salvar a base de dados processada
    try:
        vendas_cliente.to_csv("vendas_cliente_processado.csv", index=False)
        print("Arquivo 'vendas_cliente_processado.csv' criado com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")
    
    return vendas_cliente

# Chamar a função para garantir que o arquivo seja gerado
vendas_cliente = processar_dados()
