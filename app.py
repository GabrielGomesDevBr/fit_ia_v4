import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
import yaml
from datetime import datetime, timedelta
import re
import random

# Função para carregar configuração
def load_config():
    try:
        with open('config.yaml', 'r') as config_file:
            config = yaml.safe_load(config_file)
        return config
    except Exception as e:
        st.error(f"Erro ao carregar a configuração: {e}")
        return None

# Função para inicializar o modelo AI
def initialize_ai_model(api_key):
    try:
        os.environ['GOOGLE_API_KEY'] = api_key
        model = ChatGoogleGenerativeAI(model='gemini-pro')
        return model
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo AI: {e}")
        return None

# Função para calcular o TMB (Taxa Metabólica Basal)
def calcular_tmb(peso, altura, idade, sexo):
    if sexo == 'Masculino':
        tmb = 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
    else:
        tmb = 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)
    return tmb

# Função para extrair informações do plano
def extrair_informacoes_plano(content, duracao_plano, peso_inicial, objetivo, preferencias_atividade_fisica):
    data_inicio = datetime.today()
    datas = [data_inicio + timedelta(days=i) for i in range(duracao_plano)]
    
    # Simulação de perda/ganho de peso baseado no objetivo
    if objetivo == 'Emagrecimento':
        pesos = [peso_inicial - (0.1 * i) for i in range(duracao_plano)]
    elif objetivo == 'Ganho de Massa Muscular':
        pesos = [peso_inicial + (0.05 * i) for i in range(duracao_plano)]
    else:
        pesos = [peso_inicial] * duracao_plano

    # Geração de exercícios baseados nas preferências
    exercicios = []
    for _ in range(duracao_plano):
        exercicio_dia = random.choice(preferencias_atividade_fisica)
        duracao = random.randint(30, 60)  # Duração entre 30 e 60 minutos
        exercicios.append(f"{exercicio_dia} - {duracao} minutos")

    data = {
        'Data': [d.strftime('%d/%m/%Y') for d in datas],
        'Peso': pesos,
        'Exercícios': exercicios
    }
    return pd.DataFrame(data)

# Função para validar o plano
def validar_plano(plano_df, objetivo, restricoes_alimentares):
    if len(plano_df) == 0:
        return False, "O plano está vazio."
    return True, "Plano validado com sucesso."

# Função para gerar distribuição de macronutrientes
def gerar_macronutrientes(objetivo):
    if objetivo == 'Emagrecimento':
        return {'Proteínas': 30, 'Carboidratos': 40, 'Gorduras': 30}
    elif objetivo == 'Ganho de Massa Muscular':
        return {'Proteínas': 35, 'Carboidratos': 50, 'Gorduras': 15}
    elif objetivo == 'Manutenção do Peso':
        return {'Proteínas': 25, 'Carboidratos': 50, 'Gorduras': 25}
    else:  # Aumento de Performance Esportiva
        return {'Proteínas': 30, 'Carboidratos': 55, 'Gorduras': 15}

# Interface Streamlit
st.set_page_config(page_title="Fit-IA - Planejador Avançado de Vida Saudável", layout="wide")
st.title('Fit-IA - Seu Planejador Personalizado de Vida Saudável')

# Carregar configuração
config = load_config()
if config is None:
    st.stop()

# Inicializar modelo AI
ai_model = initialize_ai_model(config['GOOGLE_API_KEY'])
if ai_model is None:
    st.stop()

# Criar colunas para layout
col1, col2 = st.columns(2)

with col1:
    nome = st.text_input('Nome:')
    idade = st.number_input('Idade:', min_value=18, max_value=100, step=1)
    sexo = st.selectbox('Sexo:', ['Masculino', 'Feminino'])
    altura = st.number_input('Altura (cm):', min_value=100, max_value=250, step=1)
    peso = st.number_input('Peso atual (kg):', min_value=30.0, max_value=300.0, step=0.1)
    
with col2:
    nivel_atividade = st.selectbox('Nível de atividade física:', [
        'Sedentário', 'Levemente ativo', 'Moderadamente ativo', 'Muito ativo', 'Extremamente ativo'
    ])
    objetivo = st.selectbox('Objetivo principal:', [
        'Emagrecimento', 'Ganho de Massa Muscular', 'Manutenção do Peso', 'Aumento de Performance Esportiva'
    ])
    restricoes_alimentares = st.multiselect('Restrições alimentares:', [
        'Nenhuma', 'Vegetariano', 'Vegano', 'Sem Glúten', 'Sem Lactose', 'Baixo Carboidrato',
        'Alergia a Nozes', 'Alergia a Frutos do Mar'
    ])
    preferencias_alimentares = st.text_area('Preferências alimentares (opcional):')
    preferencias_atividade_fisica = st.multiselect('Preferências de atividade física:', [
        'Caminhada', 'Corrida', 'Natação', 'Ciclismo', 'Musculação', 'Yoga', 'Pilates',
        'Esportes Coletivos', 'Dança', 'Artes Marciais'
    ])
    limitacoes_fisicas = st.text_area('Limitações físicas (se houver):')

# Novo campo para duração do plano
duracao_plano = st.selectbox('Duração do plano:', [7, 14, 30], index=2)

if st.button(f'Gerar Plano Personalizado de {duracao_plano} Dias'):
    if not all([nome, idade, altura, peso, objetivo]):
        st.warning('Por favor, preencha todos os campos obrigatórios.')
    else:
        try:
            tmb = calcular_tmb(peso, altura, idade, sexo)
            
            prompt_template = """
            Gerar plano personalizado para {nome}, idade {idade}, {sexo}, altura {altura} cm, peso {peso} kg. 
            Nível de atividade: {nivel_atividade}. Objetivo: {objetivo}. Restrições alimentares: {restricoes_alimentares}. 
            Preferências alimentares: {preferencias_alimentares}. Preferências de atividade física: {preferencias_atividade_fisica}. 
            Limitações físicas: {limitacoes_fisicas}. TMB: {tmb}. Duração: {dias} dias.
            """
            
            prompt = prompt_template.format(
                nome=nome,
                idade=idade,
                sexo=sexo,
                altura=altura,
                peso=peso,
                nivel_atividade=nivel_atividade,
                objetivo=objetivo,
                restricoes_alimentares=', '.join(restricoes_alimentares) if restricoes_alimentares else 'Nenhuma',
                preferencias_alimentares=preferencias_alimentares,
                preferencias_atividade_fisica=', '.join(preferencias_atividade_fisica),
                limitacoes_fisicas=limitacoes_fisicas,
                tmb=tmb,
                dias=duracao_plano
            )

            response = ai_model.invoke(prompt)

            # Extrair informações do plano da resposta do AI
            plano_df = extrair_informacoes_plano(response.content, duracao_plano, peso, objetivo, preferencias_atividade_fisica)

            # Validar o plano
            plano_valido, mensagem_validacao = validar_plano(plano_df, objetivo, restricoes_alimentares)

            if plano_valido:
                st.success(mensagem_validacao)
                st.subheader(f'Seu Plano Personalizado de {duracao_plano} Dias:')
                st.markdown(response.content)

                # Exibir o plano em formato de tabela
                st.dataframe(plano_df)

                # Gerar e exibir gráfico de projeção de peso
                fig_peso = px.line(plano_df, x='Data', y='Peso', title='Projeção de Peso')
                fig_peso.update_layout(xaxis_title='Data', yaxis_title='Peso (kg)')
                st.plotly_chart(fig_peso)

                # Gráfico de distribuição de macronutrientes
                macronutrientes = gerar_macronutrientes(objetivo)
                fig_macro = go.Figure(data=[go.Pie(labels=list(macronutrientes.keys()), values=list(macronutrientes.values()))])
                fig_macro.update_layout(title='Distribuição de Macronutrientes')
                st.plotly_chart(fig_macro)

                # Calendário visual do plano de exercícios
                fig_calendar = go.Figure(data=[go.Table(
                    header=dict(values=['Data', 'Exercícios']),
                    cells=dict(values=[plano_df['Data'], plano_df['Exercícios']])
                )])
                fig_calendar.update_layout(title='Calendário de Exercícios')
                st.plotly_chart(fig_calendar)

                # Adicionar funcionalidade para exportar o plano como CSV
                csv = plano_df.to_csv(index=False)
                st.download_button(
                    label=f"Baixar Plano de {duracao_plano} Dias como CSV",
                    data=csv,
                    file_name=f"plano_{duracao_plano}_dias.csv",
                    mime="text/csv",
                )
            else:
                st.error(f"O plano gerado não é adequado: {mensagem_validacao}")
        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o plano: {str(e)}")

if __name__ == "__main__":
    # Sidebar
    st.sidebar.title("Sobre o Fit-IA")
    st.sidebar.info("""
    O Fit-IA é um assistente de vida saudável, desenvolvido pela AperData para ajudar 
    as pessoas a atingirem seus objetivos de bem-estar, oferecendo recomendações personalizadas de exercícios e dietas.
    """)

    st.sidebar.title("Entre em Contato")
    st.sidebar.markdown("""
    Para soluções de IA sob medida ou suporte:

    - 🌐 [aperdata.com](https://aperdata.com)
    - 📱 WhatsApp: **11 98854-3437**
    - 📧 Email: **gabriel@aperdata.com**
    """)
