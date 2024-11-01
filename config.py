import yaml
from typing import Dict, List

# Constantes de Configuração
APP_TITLE = "🌟 Fit-IA | Seu Coach Digital de Bem-estar"
APP_ICON = "🍎"
APP_LAYOUT = "wide"

# Cores do tema
COLORS = {
    'primary': '#FF6B6B',     # Coral vibrante
    'secondary': '#4ECDC4',   # Turquesa
    'accent': '#45B7D1',      # Azul claro
    'success': '#96CEB4',     # Verde suave
    'warning': '#FFEEAD',     # Amarelo suave
    'error': '#D4726A'        # Vermelho suave
}

# Opções de seleção
ACTIVITY_LEVELS = {
    'Sedentário 🛋️': 1.2,
    'Levemente ativo 🚶': 1.375,
    'Moderadamente ativo 🏃': 1.55,
    'Muito ativo 🏋️': 1.725,
    'Extremamente ativo 🏊‍♂️': 1.9
}

GOALS = {
    'Emagrecimento 📉': {'protein': 30, 'carbs': 40, 'fats': 30},
    'Ganho de Massa 💪': {'protein': 35, 'carbs': 50, 'fats': 15},
    'Manutenção ⚖️': {'protein': 25, 'carbs': 50, 'fats': 25},
    'Performance 🎯': {'protein': 30, 'carbs': 55, 'fats': 15}
}

DIETARY_RESTRICTIONS = [
    'Nenhuma 🍽️',
    'Vegetariano 🥗',
    'Vegano 🌱',
    'Sem Glúten 🌾',
    'Sem Lactose 🥛',
    'Baixo Carboidrato 🥩',
    'Alergia a Nozes 🥜',
    'Alergia a Frutos do Mar 🦐'
]

PHYSICAL_ACTIVITIES = [
    'Caminhada 🚶‍♂️',
    'Corrida 🏃‍♀️',
    'Natação 🏊‍♂️',
    'Ciclismo 🚴‍♀️',
    'Musculação 🏋️‍♀️',
    'Yoga 🧘‍♀️',
    'Pilates 🤸‍♀️',
    'Esportes Coletivos ⚽',
    'Dança 💃',
    'Artes Marciais 🥋'
]

# Função para carregar configuração do YAML
def load_config() -> Dict:
    try:
        with open('config.yaml', 'r') as config_file:
            return yaml.safe_load(config_file)
    except Exception as e:
        raise Exception(f"Erro ao carregar a configuração: {e}")

# Configuração de estilo CSS personalizado
CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
        color: white;
        border-radius: 30px;
        padding: 0.5rem 2rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 15px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
    }
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.95);
    }
</style>
"""
