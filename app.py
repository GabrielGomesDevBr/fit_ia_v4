import streamlit as st
import pandas as pd
import plotly.express as px
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
import yaml

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

# Função para calcular a Taxa Metabólica Basal (TMB)
def calcular_tmb(peso, altura, idade, sexo):
    if sexo == 'Masculino':
        tmb = 88.362 + (13.397 * peso) + (4.799 * altura) - (5.677 * idade)
    else:  # Feminino
        tmb = 447.593 + (9.247 * peso) + (3.098 * altura) - (4.330 * idade)
    return round(tmb, 2)

# Função para projetar perda de peso
def projetar_perda_peso(peso_inicial, altura, idade, sexo, nivel_atividade, semanas=12):
    tmb = calcular_tmb(peso_inicial, altura, idade, sexo)
    fator_atividade = {
        'Sedentário': 1.2,
        'Levemente ativo': 1.375,
        'Moderadamente ativo': 1.55,
        'Muito ativo': 1.725,
        'Extremamente ativo': 1.9
    }
    
    gasto_calorico_diario = tmb * fator_atividade[nivel_atividade]
    deficit_calorico_diario = 500  # Déficit calórico moderado para perda de peso saudável
    
    projecao = [peso_inicial]
    for _ in range(1, semanas + 1):
        perda_semanal = (deficit_calorico_diario * 7) / 7700  # 7700 calorias = 1kg de gordura
        novo_peso = projecao[-1] - perda_semanal
        projecao.append(novo_peso)
    
    return projecao

# Template do prompt
template = '''
Você é um assistente chamado Fit-IA, especializado em ajudar pessoas a estabelecer uma vida saudável e atingir seus objetivos de forma sustentável. Suas atribuições incluem:
- Fornecer orientações personalizadas para emagrecimento, ganho de massa muscular ou manutenção de peso.
- Sugerir estratégias para aumentar a adesão a novos hábitos alimentares e de exercícios.
- Oferecer dicas de bem-estar geral e estilo de vida saudável.
- Interpretar dados de saúde e fornecer recomendações baseadas em evidências.
- Criar planos de exercícios e alimentação personalizados.

Dados do usuário:
Nome: {nome}
Idade: {idade} anos
Sexo: {sexo}
Altura: {altura} cm
Peso atual: {peso} kg
Nível de atividade física: {nivel_atividade}
Objetivo principal: {objetivo}
Restrições alimentares: {restricoes_alimentares}
Preferências alimentares: {preferencias_alimentares}
Preferências de atividade física: {preferencias_atividade_fisica}
Limitações físicas: {limitacoes_fisicas}
Taxa Metabólica Basal (TMB): {tmb} calorias/dia

Com base nessas informações, forneça um plano personalizado, incluindo:
1. Análise detalhada do perfil do usuário e seu objetivo.
2. Recomendações dietéticas personalizadas, considerando as preferências e restrições.
3. Plano de exercícios detalhado, adequado ao nível de atividade física e limitações.
4. Estratégias para aumentar a adesão ao novo estilo de vida.
5. Dicas de bem-estar geral, gestão do estresse e melhoria da qualidade do sono.
6. Metas realistas e timeline esperado para atingir o objetivo.
7. Sugestão de cardápio saudável para um dia, adequado ao objetivo e TMB.
8. Recomendações para superar possíveis obstáculos e manter a motivação.

Forneça respostas detalhadas, motivadoras e focadas na sustentabilidade das mudanças propostas. Use uma linguagem amigável e empática, considerando a individualidade de cada usuário.

Formate o plano utilizando Markdown para melhor legibilidade.
'''

prompt_template = PromptTemplate.from_template(template)

# Interface Streamlit
st.set_page_config(page_title="Fit-IA - Assistente de Vida Saudável", layout="wide")
st.title('Fit-IA - Seu Assistente Personalizado de Vida Saudável')

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

if st.button('Gerar Plano Personalizado'):
    if not all([nome, idade, altura, peso, objetivo]):
        st.warning('Por favor, preencha todos os campos obrigatórios.')
    else:
        try:
            tmb = calcular_tmb(peso, altura, idade, sexo)
            
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
                tmb=tmb
            )

            response = ai_model.invoke(prompt)

            st.subheader('Seu Plano Personalizado:')
            st.markdown(response.content)

            # Gerar e exibir gráfico de projeção de peso
            if objetivo == 'Emagrecimento':
                projecao_peso = projetar_perda_peso(peso, altura, idade, sexo, nivel_atividade)
                df = pd.DataFrame({'Semana': range(13), 'Peso': projecao_peso})

                fig = px.line(df, x='Semana', y='Peso', title='Projeção de Perda de Peso em 12 Semanas')
                fig.update_layout(xaxis_title='Semana', yaxis_title='Peso (kg)')
                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Ocorreu um erro ao gerar o plano: {e}")
