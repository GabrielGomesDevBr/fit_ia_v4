import streamlit as st
from datetime import datetime
import json
from utils import (
    load_config, load_lottie_url, initialize_ai_model,
    calculate_bmr, calculate_tdee, generate_meal_plan,
    generate_workout_plan, format_plan_data
)
from components import (
    setup_page_config, create_navigation, show_welcome_page,
    create_user_profile_form, display_plan, show_progress,
    show_about
)

# Inicialização da sessão
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'plan' not in st.session_state:
    st.session_state.plan = None
if 'meal_plan' not in st.session_state:
    st.session_state.meal_plan = None

# Carregamento de configurações
config = load_config()
if not config:
    st.error("Erro ao carregar configurações. Por favor, verifique o arquivo config.yaml")
    st.stop()

# Setup da página
setup_page_config(config)

# Carregamento das animações (com tratamento de erro)
try:
    lottie_fitness = load_lottie_url(config['animations']['fitness'])
    lottie_nutrition = load_lottie_url(config['animations']['nutrition'])
    lottie_wellness = load_lottie_url(config['animations']['wellness'])
except Exception as e:
    lottie_fitness = None
    lottie_nutrition = None
    lottie_wellness = None
    st.warning("Algumas animações podem não estar disponíveis.")

# Inicialização do modelo AI
try:
    ai_model = initialize_ai_model(config['GOOGLE_API_KEY'])
    if not ai_model:
        st.warning("Modelo AI não disponível. Algumas funcionalidades podem estar limitadas.")
except Exception as e:
    ai_model = None
    st.warning("Modelo AI não disponível. Algumas funcionalidades podem estar limitadas.")

# Navegação principal
selected_page = create_navigation()

# Lógica principal baseada na navegação
if selected_page == "Home":
    show_welcome_page(lottie_fitness)
    
    if st.button("Começar Agora!", help="Clique para criar seu perfil"):
        st.session_state.navigation = "Perfil"
        st.experimental_rerun()

elif selected_page == "Perfil":
    st.markdown("<h2>Seu Perfil</h2>", unsafe_allow_html=True)
    
    submit_button, profile_data = create_user_profile_form()
    
    if submit_button and all([
        profile_data['nome'], profile_data['idade'], profile_data['altura'],
        profile_data['peso'], profile_data['objetivo']
    ]):
        st.session_state.profile = profile_data
        
        # Cálculos iniciais
        bmr = calculate_bmr(
            profile_data['peso'],
            profile_data['altura'],
            profile_data['idade'],
            profile_data['sexo']
        )
        
        tdee = calculate_tdee(bmr, profile_data['nivel_atividade'], config)
        
        # Gerar plano alimentar
        meal_plan = generate_meal_plan(
            tdee,
            profile_data['objetivo'],
            profile_data['restricoes']
        )
        
        # Gerar plano de treino
        workout_plan = generate_workout_plan(
            profile_data['preferencias'],
            None,  # limitações físicas (a ser implementado)
            profile_data['objetivo'],
            30  # dias do plano
        )
        
        # Formatar dados do plano
        plan_df = format_plan_data(
            workout_plan,
            datetime.now(),
            profile_data['peso'],
            profile_data['objetivo']
        )
        
        # Salvar planos na sessão
        st.session_state.plan = plan_df
        st.session_state.meal_plan = meal_plan
        
        st.success("Perfil salvo com sucesso! Seu plano personalizado está pronto.")
        st.balloons()
    
    elif submit_button:
        st.warning("Por favor, preencha todos os campos obrigatórios.")

elif selected_page == "Plano":
    if st.session_state.profile is None:
        st.warning("Por favor, complete seu perfil primeiro.")
        if st.button("Ir para Perfil"):
            st.session_state.navigation = "Perfil"
            st.experimental_rerun()
    else:
        st.markdown("<h2>Seu Plano Personalizado</h2>", unsafe_allow_html=True)
        
        if st.session_state.plan is not None and st.session_state.meal_plan is not None:
            display_plan(st.session_state.plan, st.session_state.meal_plan)
            
            # Botão para exportar o plano
            if st.download_button(
                label="📥 Baixar Plano Completo",
                data=st.session_state.plan.to_csv(index=False),
                file_name="plano_fitia.csv",
                mime="text/csv"
            ):
                st.success("Plano baixado com sucesso!")
        else:
            st.error("Erro ao carregar o plano. Por favor, tente gerar novamente.")

elif selected_page == "Progresso":
    if st.session_state.profile is None:
        st.warning("Por favor, complete seu perfil primeiro.")
    else:
        st.markdown("<h2>Seu Progresso</h2>", unsafe_allow_html=True)
        
        # Aqui você pode implementar a lógica para mostrar o progresso
        # Por enquanto, vamos mostrar apenas dados simulados
        historical_data = {
            'peso_inicial': st.session_state.profile['peso'],
            'peso_atual': st.session_state.profile['peso'] - 0.5  # Simulação
        }
        
        show_progress(historical_data)

elif selected_page == "Sobre":
    show_about()

# Sidebar
with st.sidebar:
    st.markdown("---")
    if st.session_state.profile:
        st.markdown(f"👤 **{st.session_state.profile['nome']}**")
        st.markdown(f"🎯 Objetivo: {st.session_state.profile['objetivo']}")
        
        if st.button("Limpar Dados", help="Remove todos os dados salvos"):
            st.session_state.profile = None
            st.session_state.plan = None
            st.session_state.meal_plan = None
            st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("""
        ### Versão
        Fit-IA v2.0.0
        
        ### Desenvolvido por
        [AperData](https://aperdata.com)
        
        ### Contato
        📱 WhatsApp: (11) 98854-3437  
        📧 Email: gabriel@aperdata.com
    """)
