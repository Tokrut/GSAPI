"""
Вспомогательные функции для GEO Analyzer
"""

import base64
import pandas as pd
from datetime import datetime

def get_score_color(score):
    """Получить цвет для оценки"""
    if score >= 80:
        return "#00C853"  # Зеленый
    elif score >= 60:
        return "#64DD17"  # Светло-зеленый
    elif score >= 40:
        return "#FFD600"  # Желтый
    else:
        return "#D50000"  # Красный

def format_file_size(size_bytes):
    """Форматирование размера файла"""
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} B"

def create_progress_bar(score, label):
    """Создание прогресс-бара с цветовой индикацией"""
    color = get_score_color(score)
    return f"""
    <div style="background-color: #f0f0f0; border-radius: 10px; padding: 3px; margin: 5px 0;">
        <div style="background-color: {color}; width: {score}%; border-radius: 8px; padding: 5px; text-align: center; color: white;">
            {label}: {score}%
        </div>
    </div>
    """

def validate_url(url):
    """Валидация URL"""
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def create_sample_dataframe(data):
    """Создание DataFrame для отображения данных"""
    if isinstance(data, dict):
        return pd.DataFrame(list(data.items()), columns=['Параметр', 'Значение'])
    elif isinstance(data, list):
        return pd.DataFrame(data)
    else:
        return pd.DataFrame([data])
