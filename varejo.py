import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os
import json

# Função para ajustar a altura do gráfico Plotly
def set_chart_height(fig, height=400):
    fig.update_layout(height=height)
    return fig

# Função para codificar a imagem em base64
def load_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        st.error("Imagem não encontrada. Verifique o caminho do arquivo.")
        return None

# Função para carregar o CSS
def load_css(css_path):
    try:
        with open(css_path, "r") as css_file:
            return css_file.read()
    except FileNotFoundError:
        st.warning("Arquivo CSS não encontrado.")
        return ""

# Função de formatação de moeda
def format_currency(value):
    return f"R$ {value:,.2f}".replace('.', ',')

# Função de formatação com ponto para milhar
def format_number(value):
    return f"{int(value):,}".replace(',', '.')

# Função para calcular métricas
def calcular_metrica(df, metrica):
    metrica_dict = {
        'Vendas': df.shape[0],
        'Fat. sem frete': df['Preço'].sum(),
        'Fat. com frete': df['Preço_com_frete'].sum(),
        'Clientes': df['cliente_Log'].nunique()
    }
    return metrica_dict.get(metrica, 0)

# Função para agrupar dados pela métrica selecionada
def agrupar_dados(df, metrica, group_by):
    agrupar_dict = {
        'Vendas': df.groupby(group_by).size().reset_index(name='Vendas'),
        'Fat. sem frete': df.groupby(group_by)['Preço'].sum().reset_index(name='Faturamento sem Frete'),
        'Fat. com frete': df.groupby(group_by)['Preço_com_frete'].sum().reset_index(name='Faturamento com Frete'),
        'Clientes': df.groupby(group_by)['cliente_Log'].nunique().reset_index(name='Clientes')
    }
    return agrupar_dict.get(metrica, pd.DataFrame())

# Carregar o arquivo GeoJSON dos estados do Brasil
def load_geojson(filename):
    with open(filename) as f:
        return json.load(f)

# Função para categorizar faixas
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

# Título do Dashboard
st.title("Dashboard de Vendas do Varejo")

# Carregar o CSS
css = load_css("styles.css")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Adicionar a logo
logo_base64 = load_image("LogoBranca.png")
if logo_base64:
    st.sidebar.markdown(f"""
        <div class="sidebar-content">
            <img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: auto;" />
        </div>
    """, unsafe_allow_html=True)

# Botão de opção para selecionar a métrica
metrica = st.sidebar.radio("Selecione a Métrica", ('Vendas', 'Fat. sem frete', 'Fat. com frete', 'Clientes'))

# Verificar se o arquivo existe antes de carregar
if os.path.exists("vendas_cliente_processado.csv"):
    vendas_cliente = pd.read_csv("vendas_cliente_processado.csv")
else:
    st.error("Arquivo vendas_cliente_processado.csv não encontrado.")
    st.stop()

# Mapeamento e ordenação de meses
meses_ordenados_lista = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
vendas_cliente['Mes'] = pd.Categorical(vendas_cliente['Mes'].map({
    'JAN': 'JAN', 'FEB': 'FEV', 'MAR': 'MAR', 'APR': 'ABR', 
    'MAY': 'MAI', 'JUN': 'JUN', 'JUL': 'JUL', 'AUG': 'AGO', 
    'SEP': 'SET', 'OCT': 'OUT', 'NOV': 'NOV', 'DEC': 'DEZ'
}), categories=meses_ordenados_lista, ordered=True)

# Filtros
st.sidebar.header("Filtros")
bandeira = st.sidebar.multiselect("Bandeira", vendas_cliente['bandeira'].unique())
mes = st.sidebar.multiselect("Mês", vendas_cliente['Mes'].unique())
canal = st.sidebar.multiselect("Canal de Venda", vendas_cliente['idcanalvenda'].unique())
estado = st.sidebar.multiselect("Estado", vendas_cliente['estado'].unique())

# Filtragem dos dados com base nos filtros
filtered_data = vendas_cliente
if bandeira:
    filtered_data = filtered_data[filtered_data['bandeira'].isin(bandeira)]
if mes:
    filtered_data = filtered_data[filtered_data['Mes'].isin(mes)]
if canal:
    filtered_data = filtered_data[filtered_data['idcanalvenda'].isin(canal)]
if estado:
    filtered_data = filtered_data[filtered_data['estado'].isin(estado)]

# Verificar se a coluna 'Faixa de Idade' existe, se não criar uma categórica
if 'Faixa de Idade' not in filtered_data.columns:
    filtered_data['Faixa de Idade'] = filtered_data['idade'].apply(faixa_idade)
filtered_data['Faixa de Idade'] = pd.Categorical(filtered_data['Faixa de Idade'], 
                                                 categories=["até 20", "20 a 34", "35 a 49", "50 a 79", "80 ou mais"], 
                                                 ordered=True)

# Exibição dos cards com as métricas
with st.container():
    col1, col2, col3, col4 = st.columns(4)
    metrics = {
        'Vendas': format_number(filtered_data.shape[0]),
        'Fat. sem frete': format_currency(filtered_data['Preço'].sum()),
        'Fat. com frete': format_currency(filtered_data['Preço_com_frete'].sum()),
        'Clientes': format_number(filtered_data['cliente_Log'].nunique())
    }
    cards = [
        ("Vendas", metrics['Vendas']),
        ("Faturamento sem frete", metrics['Fat. sem frete']),
        ("Faturamento com frete", metrics['Fat. com frete']),
        ("Clientes", metrics['Clientes'])
    ]
    for col, (title, value) in zip([col1, col2, col3, col4], cards):
        col.markdown(f"""
            <div class="card">
                <div class="card-value">{value}</div>
                <div class="card-title">{title}</div>
            </div>
        """, unsafe_allow_html=True)

# Carregar o arquivo GeoJSON
geojson_data = load_geojson("brazil-states.geojson")
group_by = st.selectbox("Agrupar por", options=["Mes", "Dia", "Dia_da_Semana"], index=0)
# Linha 1 dos gráficos
with st.container():
    col1, col2, col3 = st.columns(3)  # Modifique para ter 3 colunas na linha 1
    # Caixa de seleção para agrupar por Mês, Dia ou Dia da Semana
    with col1:
        metrica_por_tempo = agrupar_dados(filtered_data, metrica, group_by)
        fig_tempo = px.line(metrica_por_tempo, x=group_by, y=metrica_por_tempo.columns[1], title=f"{metrica} por {group_by}")
        st.plotly_chart(set_chart_height(fig_tempo, height=300), use_container_width=True)

    with col2:
        # Gráfico de Vendas por Faixa de Preço
        metrica_por_faixa_preco = agrupar_dados(filtered_data, metrica, 'Faixa de Preço')
        fig_faixa_preco = px.bar(
            metrica_por_faixa_preco,
            x='Faixa de Preço',
            y=metrica_por_faixa_preco.columns[1],
            title=f"{metrica} por Faixa de Preço",
            category_orders={'Faixa de Preço': ["até 500", "500 a 1.499", "1.500 a 2.999", "3.000 a 4.999", "5.000 ou mais"]}
        )
        st.plotly_chart(set_chart_height(fig_faixa_preco, height=300), use_container_width=True)

    with col3:
        # Gráfico de Mapa de Calor por Estado (Brasil) - Aumentado para altura 500
        metrica_por_estado = agrupar_dados(filtered_data, metrica, 'estado')
        fig_estado = px.choropleth(
            metrica_por_estado,
            geojson=geojson_data,
            locations='estado',
            featureidkey="properties.sigla",  # Ajuste de acordo com a estrutura do seu GeoJSON
            color=metrica_por_estado.columns[1],
            color_continuous_scale=px.colors.sequential.Plasma,
            title=f"{metrica} por Estado",
            scope='south america'  # O scope deve ser 'south america' para mostrar o Brasil
        )
        fig_estado.update_geos(fitbounds="locations", visible=False)  # Ajustar visualização
        st.plotly_chart(set_chart_height(fig_estado, height=350), use_container_width=True)

# Linha 2 dos gráficos
with st.container():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Gráfico de Vendas por Bandeira (Rosca)
        metrica_por_bandeira = agrupar_dados(filtered_data, metrica, 'bandeira')
        fig_bandeira = px.pie(
            metrica_por_bandeira,
            names='bandeira',
            values=metrica_por_bandeira.columns[1],
            hole=0.4,
            title=f"{metrica} por Bandeira"
        )
        fig_bandeira.update_layout(
            legend_orientation='h',  # Orientação horizontal da legenda
            legend_title=None,        # Opcional: Remove o título da legenda
            legend=dict(yanchor='top', y=-0.2, xanchor='center', x=0.5)  # Posição da legenda
        )
        st.plotly_chart(set_chart_height(fig_bandeira, height=300), use_container_width=True)

    with col2:
        # Gráfico de Vendas por Canal de Venda (Pizza)
        metrica_por_canal = agrupar_dados(filtered_data, metrica, 'idcanalvenda')
        fig_canal = px.pie(
            metrica_por_canal,
            names='idcanalvenda',
            values=metrica_por_canal.columns[1],
            title=f"{metrica} por Canal de Venda"
        )
        fig_canal.update_layout(
            legend_orientation='h',  # Orientação horizontal da legenda
            legend_title=None,        # Opcional: Remove o título da legenda
            legend=dict(yanchor='top', y=-0.2, xanchor='center', x=0.5)  # Posição da legenda
        )
        st.plotly_chart(set_chart_height(fig_canal, height=300), use_container_width=True)

    with col3:
        # Gráfico de Vendas por Faixa Etária
        metrica_por_faixa_idade = agrupar_dados(filtered_data, metrica, 'Faixa de Idade')
        fig_faixa_idade = px.bar(
            metrica_por_faixa_idade,
            x='Faixa de Idade',
            y=metrica_por_faixa_idade.columns[1],
            title=f"{metrica} por Faixa Etária",
            category_orders={'Faixa de Idade': ["até 20", "20 a 34", "35 a 49", "50 a 79", "80 ou mais"]}
        )
        st.plotly_chart(set_chart_height(fig_faixa_idade, height=300), use_container_width=True)

    with col4:
        with col4:
            # Gráfico de Vendas por Departamento (Top 10, Barras Horizontais)
            metrica_por_departamento = agrupar_dados(filtered_data, metrica, 'Nome_Departamento')
            metrica_por_departamento = metrica_por_departamento.sort_values(by=metrica_por_departamento.columns[1], ascending=True).head(10)
            fig_departamento = px.bar(
                metrica_por_departamento,
                y='Nome_Departamento',
                x=metrica_por_departamento.columns[1],
                title=f"Top 10 {metrica} por Departamento",
                orientation='h'  # Barra horizontal
            )
            st.plotly_chart(set_chart_height(fig_departamento, height=300), use_container_width=True)