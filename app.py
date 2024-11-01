import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
from typing import Dict, List
import json

# Importando módulos locais
from config import (
    APP_TITLE, APP_ICON, APP_LAYOUT, COLORS, CUSTOM_CSS,
    ACTIVITY_LEVELS, GOALS, DIETARY_RESTRICTIONS, PHYSICAL_ACTIVITIES,
    load_config
)
from utils import (
    initialize_ai_model, calcular_tmb, calcular_calorias_diarias,
    criar_plano_treino, gerar_graficos_plano
)

def setup_page():
    """Configura a página inicial do Streamlit."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def criar_header():
    """Cria o cabeçalho da aplicação."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title(APP_TITLE)
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <p style='font-size: 1.2rem; color: #666;'>
                Transforme sua vida com inteligência artificial e conhecimento personalizado! 🌟
            </p>
        </div>
        """, unsafe_allow_html=True)

def criar_sidebar():
    """Cria e configura a barra lateral."""
    with st.sidebar:
        st.image("https://via.placeholder.com/150", caption="Fit-IA Logo")
        
        st.markdown("""
        ## 🎯 Sobre o Fit-IA
        
        Desenvolvido pela **AperData**, o Fit-IA é sua solução completa para:
        
        - 🏋️‍♀️ Planejamento de treinos
        - 🥗 Orientação nutricional
        - 📊 Análise de progresso
        - 🎯 Definição de metas
        
        ---
        
        ## 🚀 Powered by AperData
        
        Especialistas em soluções de IA para saúde e bem-estar.
        
        ### 📱 Contato
        
        - 🌐 [aperdata.com](https://aperdata.com)
        - 📱 WhatsApp: [11 98854-3437](https://wa.me/5511988543437)
        - 📧 [gabriel@aperdata.com](mailto:gabriel@aperdata.com)
        
        ---
        """)
        
        # Adiciona um CTA (Call to Action)
        st.markdown("""
        <div style='background: linear-gradient(45deg, #FF6B6B, #FF8E8E); 
                    padding: 1rem; border-radius: 10px; text-align: center;'>
            <h3 style='color: white;'>🌟 Quer uma solução personalizada?</h3>
            <p style='color: white;'>Entre em contato para uma consultoria gratuita!</p>
            <a href='https://wa.me/5511988543437' target='_blank' 
               style='background: white; color: #FF6B6B; padding: 0.5rem 1rem; 
                      border-radius: 20px; text-decoration: none; display: inline-block;'>
                Agendar Conversa 📱
            </a>
        </div>
        """, unsafe_allow_html=True)

def formulario_usuario():
    """Cria o formulário de entrada do usuário."""
    with st.form(key='user_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Dados Pessoais")
            nome = st.text_input('Nome:', placeholder="Seu nome completo")
            idade = st.number_input('Idade:', min_value=18, max_value=100, value=30)
            sexo = st.selectbox('Sexo:', ['Masculino 👨', 'Feminino 👩'])
            altura = st.number_input('Altura (cm):', min_value=100, max_value=250, value=170)
            peso = st.number_input('Peso atual (kg):', min_value=30.0, max_value=300.0, value=70.0, step=0.1)
            
        with col2:
            st.markdown("### 🎯 Objetivos e Preferências")
            nivel_atividade = st.selectbox('Nível de atividade:', list(ACTIVITY_LEVELS.keys()))
            objetivo = st.selectbox('Objetivo principal:', list(GOALS.keys()))
            restricoes = st.multiselect('Restrições alimentares:', DIETARY_RESTRICTIONS)
            
            st.markdown("### 🏃‍♂️ Atividades Físicas")
            atividades = st.multiselect('Suas atividades preferidas:', PHYSICAL_ACTIVITIES)
        
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 📝 Informações Adicionais")
            preferencias_alimentares = st.text_area('Preferências alimentares:', 
                placeholder="Ex: Gosto de frutas, prefiro frango a carne vermelha...")
            
        with col4:
            limitacoes = st.text_area('Limitações físicas:', 
                placeholder="Ex: Lesão no joelho, problema nas costas...")
            
        duracao_plano = st.select_slider('Duração do plano (dias):', 
            options=[7, 14, 21, 30], value=30)
            
        submit_button = st.form_submit_button(label='🚀 Gerar Meu Plano Personalizado')
        
        return (submit_button, {
            'nome': nome, 'idade': idade, 'sexo': sexo, 'altura': altura,
            'peso': peso, 'nivel_atividade': nivel_atividade, 'objetivo': objetivo,
            'restricoes': restricoes, 'atividades': atividades,
            'preferencias_alimentares': preferencias_alimentares,
            'limitacoes': limitacoes, 'duracao_plano': duracao_plano
        })

def exibir_plano(dados_usuario: Dict, plano_treino: List[Dict], calorias: float):
    """Exibe o plano gerado para o usuário."""
    st.markdown("""
    ## 🎉 Seu Plano Personalizado está Pronto!
    """)
    
    # Criar tabs para organizar a informação
    tab1, tab2, tab3 = st.tabs(['📊 Visão Geral', '💪 Plano de Treino', '🥗 Nutrição'])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calorias Diárias", f"{int(calorias)} kcal")
        with col2:
            st.metric("Duração do Plano", f"{dados_usuario['duracao_plano']} dias")
        with col3:
            st.metric("Meta de Peso", 
                f"{dados_usuario['peso'] - 2 if 'Emagrecimento' in dados_usuario['objetivo'] else dados_usuario['peso'] + 2} kg")
        
        # Gráficos
        df_plano = pd.DataFrame(plano_treino)
        fig_peso, fig_macro, fig_treinos = gerar_graficos_plano(
            df_plano, dados_usuario['peso'], dados_usuario['objetivo'], 
            GOALS[dados_usuario['objetivo']]
        )
        
        st.plotly_chart(fig_peso, use_container_width=True)
        col4, col5 = st.columns(2)
        with col4:
            st.plotly_chart(fig_macro, use_container_width=True)
        with col5:
            st.plotly_chart(fig_treinos, use_container_width=True)
    
    with tab2:
        st.markdown("### 📅 Calendário de Treinos")
        st.dataframe(
            df_plano[['data', 'dia_semana', 'exercicio', 'intensidade', 'duracao']],
            use_container_width=True
        )
        
        # Botão para download do plano
        csv = df_plano.to_csv(index=False)
        st.download_button(
            label="📥 Baixar Plano de Treino",
            data=csv,
            file_name=f"plano_treino_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with tab3:
        st.markdown("""
        ### 🥗 Orientações Nutricionais
        
        Baseado no seu objetivo e características, recomendamos:
        """)
        
        col6, col7, col8 = st.columns(3)
        macros = GOALS[dados_usuario['objetivo']]
        with col6:
            st.metric("Proteínas", f"{macros['protein']}%")
        with col7:
            st.metric("Carboidratos", f"{macros['carbs']}%")
        with col8:
            st.metric("Gorduras", f"{macros['fats']}%")

def main():
    """Função principal da aplicação."""
    setup_page()
    criar_header()
    criar_sidebar()
    
    # Carregar configuração
    try:
        config = load_config()
        ai_model = initialize_ai_model(config['GOOGLE_API_KEY'])
    except Exception as e:
        st.error(f"Erro na configuração: {e}")
        return
    
    # Formulário principal
    submit_button, dados_usuario = formulario_usuario()
    
    if submit_button:
        if not all([dados_usuario['nome'], dados_usuario['idade'], dados_usuario['altura'], 
                   dados_usuario['peso'], dados_usuario['objetivo']]):
            st.warning('⚠️ Por favor, preencha todos os campos obrigatórios.')
            return
        
        with st.spinner('🔮 Gerando seu plano personalizado...'):
            try:
                # Cálculos básicos
                tmb = calcular_tmb(
                    dados_usuario['peso'], 
                    dados_usuario['altura'],
                    dados_usuario['idade'],
                    dados_usuario['sexo']
                )
                
                calorias = calcular_calorias_diarias(
                    tmb,
                    dados_usuario['nivel_atividade'],
                    dados_usuario['objetivo']
                )
                
                # Gerar plano de treino
                plano_treino = criar_plano_treino(
                    dados_usuario['atividades'],
                    dados_usuario['duracao_plano'],
                    dados_usuario['objetivo'],
                    dados_usuario['limitacoes'],
                    dados_usuario['peso']  # Adicionando peso inicial
                )
                
                # Exibir resultados
                exibir_plano(dados_usuario, plano_treino, calorias)
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao gerar o plano: {str(e)}")

if __name__ == "__main__":
    main()
