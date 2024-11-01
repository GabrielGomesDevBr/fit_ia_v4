import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple
import os
from langchain_google_genai import ChatGoogleGenerativeAI

def initialize_ai_model(api_key: str) -> ChatGoogleGenerativeAI:
    """Inicializa o modelo AI do Google."""
    try:
        os.environ['GOOGLE_API_KEY'] = api_key
        return ChatGoogleGenerativeAI(model='gemini-pro')
    except Exception as e:
        raise Exception(f"Erro ao inicializar o modelo AI: {e}")

def calcular_tmb(peso: float, altura: float, idade: int, sexo: str) -> float:
    """Calcula a Taxa Metabólica Basal usando a fórmula de Harris-Benedict."""
    if sexo == 'Masculino':
        return 88.36 + (13.4 * peso) + (4.8 * altura) - (5.7 * idade)
    return 447.6 + (9.2 * peso) + (3.1 * altura) - (4.3 * idade)

def calcular_calorias_diarias(tmb: float, nivel_atividade: str, objetivo: str) -> float:
    """Calcula as calorias diárias baseadas no TMB, nível de atividade e objetivo."""
    fatores_atividade = {
        'Sedentário 🛋️': 1.2,
        'Levemente ativo 🚶': 1.375,
        'Moderadamente ativo 🏃': 1.55,
        'Muito ativo 🏋️': 1.725,
        'Extremamente ativo 🏊‍♂️': 1.9
    }
    
    calorias_base = tmb * fatores_atividade[nivel_atividade]
    
    ajustes_objetivo = {
        'Emagrecimento 📉': -500,
        'Ganho de Massa 💪': 500,
        'Manutenção ⚖️': 0,
        'Performance 🎯': 300
    }
    
    return calorias_base + ajustes_objetivo[objetivo]

def calcular_peso_projetado(peso_inicial: float, objetivo: str, dia: int) -> float:
    """Calcula o peso projetado baseado no objetivo e dia do plano."""
    if 'Emagrecimento' in objetivo:
        # Perda de 0.5kg por semana
        return peso_inicial - (0.5 * dia / 7)
    elif 'Ganho de Massa' in objetivo:
        # Ganho de 0.25kg por semana
        return peso_inicial + (0.25 * dia / 7)
    else:
        # Manutenção ou Performance
        return peso_inicial

def criar_plano_treino(
    preferencias: List[str], 
    duracao_plano: int, 
    objetivo: str,
    limitacoes: str,
    peso_inicial: float
) -> List[Dict]:
    """Cria um plano de treino personalizado."""
    plano_treino = []
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    for dia in range(duracao_plano):
        data = datetime.today() + timedelta(days=dia)
        dia_semana = dias_semana[data.weekday()]
        
        if dia_semana in ['Sábado', 'Domingo']:
            intensidade = 'Leve'
            duracao = random.randint(30, 45)
        else:
            intensidade = random.choice(['Moderada', 'Alta'])
            duracao = random.randint(45, 75)
        
        exercicio = random.choice(preferencias) if preferencias else 'Caminhada 🚶‍♂️'
        
        peso_projetado = calcular_peso_projetado(peso_inicial, objetivo, dia)
        
        plano_treino.append({
            'data': data.strftime('%d/%m/%Y'),
            'dia_semana': dia_semana,
            'exercicio': exercicio,
            'intensidade': intensidade,
            'duracao': duracao,
            'peso_projetado': round(peso_projetado, 2)
        })
    
    return plano_treino

def gerar_graficos_plano(
    plano_df: pd.DataFrame,
    peso_inicial: float,
    objetivo: str,
    macronutrientes: Dict
) -> Tuple[go.Figure, go.Figure, go.Figure]:
    """Gera os gráficos do plano."""
    # Gráfico de projeção de peso
    fig_peso = px.line(plano_df, x='data', y='peso_projetado',
                       title='📈 Projeção de Evolução do Peso',
                       template='plotly_white')
    fig_peso.update_layout(
        xaxis_title='Data',
        yaxis_title='Peso (kg)',
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Gráfico de macronutrientes
    fig_macro = go.Figure(data=[go.Pie(
        labels=list(macronutrientes.keys()),
        values=list(macronutrientes.values()),
        hole=.3,
        marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1']
    )])
    fig_macro.update_layout(
        title='🥗 Distribuição de Macronutrientes',
        template='plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Gráfico de intensidade dos treinos
    fig_treinos = px.bar(plano_df, x='data', y='duracao',
                        color='intensidade',
                        title='💪 Intensidade dos Treinos',
                        template='plotly_white')
    fig_treinos.update_layout(
        xaxis_title='Data',
        yaxis_title='Duração (minutos)',
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return fig_peso, fig_macro, fig_treinos
