import yaml
import streamlit as st
import requests
from datetime import datetime, timedelta
import random
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
import os

def load_config():
    """Carrega as configurações do arquivo YAML"""
    try:
        with open('config.yaml', 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {e}")
        return None

def load_lottie_url(url: str):
    """Carrega animação Lottie da URL"""
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def initialize_ai_model(api_key):
    """Inicializa o modelo AI"""
    try:
        os.environ['GOOGLE_API_KEY'] = api_key
        return ChatGoogleGenerativeAI(model='gemini-pro')
    except Exception as e:
        st.error(f"Erro ao inicializar modelo AI: {e}")
        return None

def calculate_bmr(weight, height, age, gender):
    """Calcula Taxa Metabólica Basal (BMR) usando fórmula de Harris-Benedict"""
    if gender == 'Masculino':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def calculate_tdee(bmr, activity_level, config):
    """Calcula Gasto Energético Total Diário (TDEE)"""
    factors = config['activity_levels']
    return bmr * factors.get(activity_level, 1.2)

def generate_meal_plan(tdee, goal, restrictions):
    """Gera plano alimentar básico baseado no TDEE"""
    if goal == 'Emagrecimento':
        calories = tdee - 500
    elif goal == 'Ganho de Massa Muscular':
        calories = tdee + 300
    else:
        calories = tdee
    
    # Distribuição de macronutrientes
    if goal == 'Emagrecimento':
        protein = 0.3  # 30% das calorias
        carbs = 0.4    # 40% das calorias
        fats = 0.3     # 30% das calorias
    elif goal == 'Ganho de Massa Muscular':
        protein = 0.35 # 35% das calorias
        carbs = 0.5    # 50% das calorias
        fats = 0.15    # 15% das calorias
    else:
        protein = 0.25 # 25% das calorias
        carbs = 0.5    # 50% das calorias
        fats = 0.25    # 25% das calorias
    
    return {
        'calories': round(calories),
        'protein': round((calories * protein) / 4),  # 4 calorias por grama de proteína
        'carbs': round((calories * carbs) / 4),      # 4 calorias por grama de carboidrato
        'fats': round((calories * fats) / 9)         # 9 calorias por grama de gordura
    }

def generate_workout_plan(preferences, limitations, goal, days):
    """Gera plano de treino personalizado"""
    available_exercises = preferences if preferences else ['Caminhada', 'Alongamento']
    
    workout_plan = []
    for _ in range(days):
        exercise = random.choice(available_exercises)
        duration = random.randint(30, 60)
        workout_plan.append({
            'exercise': exercise,
            'duration': duration,
            'intensity': 'Moderada'
        })
    
    return workout_plan

def format_plan_data(workouts, start_date, initial_weight, goal):
    """Formata dados do plano para DataFrame"""
    dates = [start_date + timedelta(days=i) for i in range(len(workouts))]
    
    # Simula progressão de peso baseada no objetivo
    weight_progression = []
    for i in range(len(workouts)):
        if goal == 'Emagrecimento':
            weight = initial_weight - (0.5 * i / 7)  # Perda de 0.5kg por semana
        elif goal == 'Ganho de Massa Muscular':
            weight = initial_weight + (0.25 * i / 7)  # Ganho de 0.25kg por semana
        else:
            weight = initial_weight
        weight_progression.append(round(weight, 2))
    
    return pd.DataFrame({
        'Data': [d.strftime('%d/%m/%Y') for d in dates],
        'Peso Estimado': weight_progression,
        'Exercício': [w['exercise'] for w in workouts],
        'Duração (min)': [w['duration'] for w in workouts],
        'Intensidade': [w['intensity'] for w in workouts]
    })
