import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import hydralit_components as hc
import plotly.express as px
import plotly.graph_objects as go

def setup_page_config(config):
    """Configura a página inicial do Streamlit"""
    st.set_page_config(
        page_title=config['app_config']['title'],
        page_icon=config['app_config']['icon'],
        layout="wide"
    )

    # Inject custom CSS
    st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
        }
        .main {
            padding: 2rem;
        }
        .stButton>button {
            border-radius: 20px;
            padding: 0.5rem 2rem;
            background: linear-gradient(45deg, #FF4B4B, #FF6B6B);
            border: none;
            color: white;
            font-weight: 600;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
        .stNumberInput>div>div>input {
            border-radius: 10px;
        }
        .stSelectbox>div>div>div {
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

def create_navigation():
    """Cria menu de navegação"""
    selected = option_menu(
        menu_title=None,
        options=["Home", "Perfil", "Plano", "Progresso", "Sobre"],
        icons=['house', 'person', 'calendar3', 'graph-up', 'info-circle'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#FF4B4B", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#FF4B4B"},
        }
    )
    return selected

ddef show_welcome_page(lottie_fitness=None):
    """Exibe página inicial"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <h1 style='color: #FF4B4B;'>Bem-vindo ao Fit-IA 🎯</h1>
            <p style='font-size: 20px;'>Seu assistente pessoal para uma vida mais saudável!</p>
            """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;'>
            <h3>O que oferecemos:</h3>
            <ul>
                <li>Planos personalizados de treino</li>
                <li>Recomendações nutricionais</li>
                <li>Acompanhamento de progresso</li>
                <li>Inteligência artificial adaptativa</li>
            </ul>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        if lottie_fitness:
            st_lottie(lottie_fitness, height=300, key="welcome")
        else:
            st.image("https://via.placeholder.com/300x300.png?text=Fit-IA", width=300)

def create_user_profile_form():
    """Cria formulário de perfil do usuário"""
    with st.form(key='profile_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input('Nome:', placeholder="Seu nome completo")
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
            restricoes = st.multiselect('Restrições alimentares:', [
                'Nenhuma', 'Vegetariano', 'Vegano', 'Sem Glúten', 'Sem Lactose',
                'Baixo Carboidrato', 'Alergia a Nozes', 'Alergia a Frutos do Mar'
            ])
            preferencias = st.multiselect('Preferências de atividade física:', [
                'Caminhada', 'Corrida', 'Natação', 'Ciclismo', 'Musculação',
                'Yoga', 'Pilates', 'Esportes Coletivos', 'Dança', 'Artes Marciais'
            ])
            
        submit_button = st.form_submit_button(label='Salvar Perfil')
        return submit_button, {
            'nome': nome, 'idade': idade, 'sexo': sexo, 'altura': altura,
            'peso': peso, 'nivel_atividade': nivel_atividade, 'objetivo': objetivo,
            'restricoes': restricoes, 'preferencias': preferencias
        }

def display_plan(plan_df, meal_plan):
    """Exibe o plano gerado"""
    # Tabs para diferentes aspectos do plano
    tab1, tab2, tab3 = st.tabs(['📊 Visão Geral', '🏋️ Treinos', '🍎 Nutrição'])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Calorias Diárias", f"{meal_plan['calories']} kcal")
        with col2:
            st.metric("Proteínas", f"{meal_plan['protein']}g")
        with col3:
            st.metric("Carboidratos", f"{meal_plan['carbs']}g")
            
        # Gráfico de projeção de peso
        fig_weight = px.line(plan_df, x='Data', y='Peso Estimado',
                           title='Projeção de Peso',
                           labels={'Peso Estimado': 'Peso (kg)'})
        st.plotly_chart(fig_weight, use_container_width=True)
    
    with tab2:
        # Calendário de treinos
        st.dataframe(
            plan_df[['Data', 'Exercício', 'Duração (min)', 'Intensidade']],
            use_container_width=True
        )
        
        # Gráfico de distribuição de exercícios
        exercise_dist = plan_df['Exercício'].value_counts()
        fig_exercises = px.pie(values=exercise_dist.values,
                             names=exercise_dist.index,
                             title='Distribuição dos Exercícios')
        st.plotly_chart(fig_exercises)
    
    with tab3:
        # Gráfico de macronutrientes
        fig_macro = go.Figure(data=[go.Pie(
            labels=['Proteínas', 'Carboidratos', 'Gorduras'],
            values=[meal_plan['protein'] * 4,
                   meal_plan['carbs'] * 4,
                   meal_plan['fats'] * 9],
            hole=.3
        )])
        fig_macro.update_layout(title='Distribuição de Macronutrientes (kcal)')
        st.plotly_chart(fig_macro)

def show_progress(historical_data=None):
    """Exibe página de progresso"""
    if historical_data is None:
        st.info("Ainda não há dados de progresso registrados.")
        return
    
    # Métricas de progresso
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Peso Inicial", f"{historical_data['peso_inicial']} kg")
    with col2:
        st.metric("Peso Atual", f"{historical_data['peso_atual']} kg")
    with col3:
        diferenca = historical_data['peso_atual'] - historical_data['peso_inicial']
        st.metric("Variação", f"{diferenca:+.1f} kg")

def show_about():
    """Exibe página sobre"""
    st.markdown("""
        <div style='text-align: center; padding: 2rem;'>
            <h1>Sobre o Fit-IA</h1>
            <p style='font-size: 1.2rem;'>
                O Fit-IA é um assistente de vida saudável desenvolvido pela AperData,
                utilizando inteligência artificial avançada para criar planos personalizados
                de exercícios e nutrição.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            ### Recursos
            - Planos personalizados de treino
            - Recomendações nutricionais baseadas em IA
            - Acompanhamento de progresso
            - Interface intuitiva
        """)
    with col2:
        st.markdown("""
            ### Contato
            - 🌐 Website: [aperdata.com](https://aperdata.com)
            - 📱 WhatsApp: (11) 98854-3437
            - 📧 Email: gabriel@aperdata.com
        """)
