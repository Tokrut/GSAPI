"""
Конфигурация GEO Analyzer Pro
Настройки приложения, константы и параметры
"""

import streamlit as st
from datetime import datetime
import os

# Настройки LLM-анализа
LLM_CONFIG = {
    'enabled': True,
    'models': ['bert_nebulon', 'grok', 'deepseek'],
    'api_key': "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",
    'base_url': "https://openrouter.ai/api/v1",
    'timeout': 30,
    'max_tokens': 2000
}

# Настройки Streamlit
STREAMLIT_CONFIG = {
    'page_title': 'GEO Analyzer Pro',
    'page_icon': '🔍',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Настройки анализа
ANALYSIS_CONFIG = {
    'timeout': 15,
    'max_retries': 3,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'retry_status_codes': [429, 500, 502, 503, 504],
    'backoff_factor': 1,
    'follow_redirects': True,
    'verify_ssl': True,
    'max_threads': 5,
    'llm_timeout': 60,
    'parallel_llm_enabled': True
}

# Критерии оценки
SCORING_CONFIG = {
    'metadata_weight': 20,
    'semantic_weight': 20,
    'content_weight': 20,
    'technical_weight': 20,
    'performance_weight': 10,
    'penalty_critical': 5,
    'penalty_warning': 2,
    'bonus_optimal': 3
}

# Оптимальные значения
OPTIMAL_VALUES = {
    'title_length': {'min': 50, 'max': 60},
    'description_length': {'min': 120, 'max': 160},
    'word_count_good': 500,
    'word_count_min': 300,
    'alt_text_percentage_good': 80,
    'alt_text_percentage_min': 50,
    'response_time_good': 1.0,
    'response_time_max': 3.0,
    'page_size_good': 1 * 1024 * 1024,  # 1MB
    'page_size_max': 2 * 1024 * 1024,   # 2MB
    'internal_links_good': 10,
    'internal_links_min': 5,
    'readability_score_good': 70,
    'text_ratio_good': 25
}

# Цветовые схемы
COLOR_SCHEME = {
    'excellent': '#00C853',  # Зеленый
    'good': '#64DD17',       # Светло-зеленый
    'average': '#FFD600',    # Желтый
    'poor': '#FF9100',       # Оранжевый
    'critical': '#D50000',   # Красный
    'primary': '#2962FF',    # Синий
    'secondary': '#6200EA',   # Фиолетовый
    'success': '#00C853',    # Успех
    'warning': '#FF9100',    # Предупреждение
    'error': '#D50000',      # Ошибка
    'info': '#2196F3',       # Информация
    'background': '#0F1116', # Темный фон
    'surface': '#1E1E1E',    # Поверхность
    'text_primary': '#FFFFFF' # Основной текст
}

# Текстовые константы
TEXT_CONTENT = {
    'app_title': 'GEO Analyzer Pro + LLM',
    'app_subtitle': 'Расширенный анализ дружелюбности сайтов для генеративного поиска с AI',
    'welcome_title': 'Добро пожаловать в GEO Analyzer Pro с LLM-анализом!',
    'app_title': 'GEO Analyzer Pro',
    'app_subtitle': 'Расширенный анализ дружелюбности сайтов для генеративного поиска',
    'welcome_title': 'Добро пожаловать в GEO Analyzer Pro!',
    'analyze_button': 'Анализировать',
    'clear_history_button': 'Очистить историю',
    'main_menu_button': 'Главное меню',
    'sample_report_title': 'Пример отчета GEO Analyzer Pro',
    'history_title': 'История анализов',
    'instructions_title': 'Инструкция по использованию',
    'login_title': 'Вход в систему',
    'register_title': 'Регистрация',
    'profile_title': 'Профиль пользователя',
    'comparison_title': 'Сравнительный анализ',
    'trends_title': 'Тренды и аналитика',
    'subscription_title': 'Управление подпиской',
    'current_subscription': 'Текущая подписка',
    'available_subscriptions': 'Доступные подписки'
}

# Статусные сообщения
STATUS_MESSAGES = {
    'analyzing': 'Анализируем сайт... Это займет несколько секунд',
    'llm_analyzing': 'Запускаем AI-анализ с помощью Bert-Nebulon, Grok и DeepSeek...',
    'analysis_failed': 'Не удалось проанализировать сайт. Проверьте URL и попробуйте снова.',
    'llm_analysis_failed': 'LLM-анализ временно недоступен. Показаны результаты структурного анализа.',
    'analyzing': 'Анализируем сайт... Это займет несколько секунд',
    'analysis_failed': 'Не удалось проанализировать сайт. Проверьте URL и попробуйте снова.',
    'no_history': 'История анализов пуста. Проведите первый анализ, чтобы увидеть историю здесь.',
    'report_generated': 'Отчет успешно сгенерирован',
    'docx_not_available': 'Библиотека python-docx не установлена',
    'return_to_main': 'Возврат в главное меню...',
    'login_success': 'Успешный вход в систему',
    'login_failed': 'Ошибка входа. Проверьте имя пользователя и пароль.',
    'register_success': 'Регистрация прошла успешно. Теперь вы можете войти в систему.',
    'register_failed': 'Ошибка регистрации.',
    'logout_success': 'Вы успешно вышли из системы',
    'saving_analysis': 'Сохраняем анализ...',
    'comparison_ready': 'Сравнительный отчет готов',
    'export_ready': 'Экспорт завершен'
}

# Настройки аутентификации
AUTH_CONFIG = {
    'session_timeout': 24 * 60 * 60,  # 24 часа в секундах
    'max_login_attempts': 5,
    'password_min_length': 6,
    'username_min_length': 3,
    'password_requirements': 'Пароль должен содержать минимум 6 символов, включая буквы и цифры'
}

# Подробные примеры для рекомендаций
RECOMMENDATION_EXAMPLES = {
    'missing_title': {
        'bad': '<title>Главная страница | Сайт</title>',
        'good': '<title>Веб-студия Разработка сайтов под ключ в Москве | Создание и продвижение</title>',
        'explanation': 'Title должен содержать основные ключевые слова, быть уникальным и длиной 50-60 символов'
    },
    'missing_description': {
        'bad': '<meta name="description" content="Наша компания предлагает услуги">',
        'good': '<meta name="description" content="Профессиональная веб-студия: создаем сайты под ключ за 30 дней. ⭐ 150+ успешных проектов ⭐ SEO-оптимизация ⭐ Поддержка 24/7. Закажите бесплатную консультацию!">',
        'explanation': 'Description должен быть уникальным, содержать ключевые слова и призыв к действию (120-160 символов)'
    },
    'low_content': {
        'bad': '<div class="content"><p>Мы делаем сайты. Быстро и качественно. Обращайтесь!</p></div>',
        'good': '''<div class="content">
  <h2>Профессиональная разработка сайтов в Москве</h2>
  <p>Наша веб-студия специализируется на создании эффективных сайтов... [300+ слов качественного текста]</p>
  <h3>Почему выбирают нас</h3>
  <ul>
    <li><strong>Полный цикл разработки</strong> - от анализа до запуска</li>
    <li><strong>SEO-оптимизация</strong> - сайты готовы к продвижению</li>
  </ul>
</div>''',
        'explanation': 'Оптимальный объем текста - 300+ слов для информационных страниц, 500+ для коммерческих'
    },
    'poor_alt_texts': {
        'bad': '<img src="project1.jpg" alt="project1">',
        'good': '<img src="razrabotka-korporativnogo-sajta.jpg" alt="Разработка корпоративного сайта для строительной компании">',
        'explanation': 'Alt-текст должен описывать содержание изображения и содержать ключевые слова'
    },
    'slow_loading': {
        'bad': '// Большие изображения (2.3 MB), не минифицированные CSS/JS, отсутствие кэширования',
        'good': '// Оптимизированные изображения (156 KB WebP), минифицированные ресурсы, включенное кэширование',
        'explanation': 'Оптимальное время загрузки - до 2 секунд. Используйте сжатие изображений, кэширование и CDN'
    },
    'missing_schema': {
        'bad': '// Отсутствует семантическая разметка',
        'good': '''<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Веб-студия ПрофиСайт",
  "description": "Профессиональная разработка сайтов в Москве",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "ул. Тверская, д. 15",
    "addressLocality": "Москва"
  }
}
</script>''',
        'explanation': 'Schema.org разметка помогает поисковым системам понять содержание страницы'
    },
    'poor_heading_structure': {
        'bad': '<h1>Главная</h1>\n<h3>О компании</h3>\n<h4>Услуги</h4>',
        'good': '<h1>Веб-разработка и создание сайтов</h1>\n<h2>Профессиональная разработка</h2>\n<h3>Корпоративные сайты</h3>',
        'explanation': 'Соблюдайте иерархию заголовков: один H1, затем H2, H3 и т.д. без пропусков уровней'
    },
    'no_https': {
        'bad': 'http://example.com',
        'good': 'https://example.com',
        'explanation': 'HTTPS обязателен для безопасности и ранжирования в поисковых системах'
    },
    'missing_canonical': {
        'bad': '// Отсутствует canonical',
        'good': '<link rel="canonical" href="https://example.com/main-page">',
        'explanation': 'Canonical URL предотвращает дублирование контента и указывает на основную версию страницы'
    },
    'poor_internal_linking': {
        'bad': '<a href="/page1">Подробнее</a>\n<a href="/page2">Тут</a>',
        'good': '<a href="/uslugi/sozdanie-sajtov" title="Создание сайтов">Услуги разработки сайтов</a>',
        'explanation': 'Используйте описательные анкор-тексты для внутренних ссылок'
    }
}

def setup_page_config():
    """Настройка конфигурации страницы Streamlit"""
    st.set_page_config(
        page_title=STREAMLIT_CONFIG['page_title'],
        page_icon=STREAMLIT_CONFIG['page_icon'],
        layout=STREAMLIT_CONFIG['layout'],
        initial_sidebar_state=STREAMLIT_CONFIG['initial_sidebar_state']
    )

def apply_custom_styles():
    """Применение пользовательских стилей"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #2962FF;
            text-align: center;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 15px;
            border-left: 5px solid #2962FF;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
        }
        .critical-issue {
            background-color: #ffebee;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #D50000;
            margin: 0.5rem 0;
            animation: pulse 2s infinite;
        }
        .warning-item {
            background-color: #fff3e0;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #FF9100;
            margin: 0.5rem 0;
        }
        .success-item {
            background-color: #e8f5e8;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #00C853;
            margin: 0.5rem 0;
        }
        .tab-content {
            padding: 1rem 0;
        }
        .status-optimal {
            color: #00C853;
            font-weight: bold;
            background-color: #e8f5e8;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .status-good {
            color: #64DD17;
            font-weight: bold;
            background-color: #f1f8e9;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .status-warning {
            color: #FF9100;
            font-weight: bold;
            background-color: #fff3e0;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .status-error {
            color: #D50000;
            font-weight: bold;
            background-color: #ffebee;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .status-info {
            color: #2962FF;
            font-weight: bold;
            background-color: #e3f2fd;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        .main-menu-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.7rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .main-menu-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
        }
        .auth-form {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .user-profile {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sidebar-section {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid #2962FF;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .quick-action-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.7rem 1rem;
            border-radius: 12px;
            width: 100%;
            margin: 0.2rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .quick-action-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .quick-action-btn:hover::before {
            left: 100%;
        }
        
        .quick-action-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        
        .quick-action-btn-danger {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff5252 100%);
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }
        
        .quick-action-btn-danger:hover {
            background: linear-gradient(135deg, #ff5252 0%, #ff4444 100%);
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
        }
        .insight-positive {
            background-color: #e8f5e8;
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #00C853;
            margin: 0.3rem 0;
        }
        .insight-warning {
            background-color: #fff3e0;
            padding: 0.8rem;
            border-radius: 8px;
            border-left: 4px solid #FF9100;
            margin: 0.3rem 0;
        }
        .activity-item {
            padding: 0.8rem;
            border-radius: 8px;
            background-color: #f8f9fa;
            margin: 0.3rem 0;
            border-left: 3px solid #2962FF;
            transition: all 0.3s ease;
        }
        .activity-item:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .comparison-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .trend-indicator {
            font-size: 1.2rem;
            font-weight: bold;
            padding: 0.5rem;
            border-radius: 10px;
            text-align: center;
        }
        .trend-up {
            background-color: #e8f5e8;
            color: #00C853;
        }
        .trend-down {
            background-color: #ffebee;
            color: #D50000;
        }
        .trend-stable {
            background-color: #fff3e0;
            color: #FF9100;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        .pulse-animation {
            animation: pulse 2s infinite;
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #2962FF 0%, #6200EA 100%);
        }
        
        /* Стили для модального окна подтверждения */
        .confirmation-modal {
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border: 2px solid #ff6b6b;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(255, 107, 107, 0.3);
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Улучшенные стили для кнопок в Streamlit */
        .stButton > button {
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Стили для основных кнопок */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
        }
        
        /* Стили для кнопок с иконками */
        .icon-button {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(102, 126, 234, 0.2) !important;
            border-radius: 12px !important;
            padding: 15px 10px !important;
            text-align: center !important;
            color: #2c3e50 !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        }
        
        .icon-button:hover {
            background: rgba(255, 255, 255, 1) !important;
            border-color: rgba(102, 126, 234, 0.4) !important;
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Стили для кнопки очистки */
        .clear-button {
            background: rgba(255, 107, 107, 0.95) !important;
            border: 2px solid rgba(255, 107, 107, 0.3) !important;
            color: white !important;
            font-weight: 700 !important;
        }
        
        .clear-button:hover {
            background: rgba(255, 107, 107, 1) !important;
            border-color: rgba(255, 107, 107, 0.5) !important;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
        }
        
        /* Анимации для плавного появления */
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Улучшенные стили для метрик */
        .stMetric {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px !important;
            padding: 15px !important;
            border: 1px solid rgba(102, 126, 234, 0.1) !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        
        .stMetric:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
        }
        
        /* Стили для колонок */
        .css-1d86834 {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 10px;
        }
        
        /* Стили для панели быстрых действий */
        .quick-action-panel {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .quick-action-panel::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .quick-actions-title {
            color: white;
            font-size: 1.3rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
            position: relative;
            z-index: 1;
        }
        
        .action-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 15px;
            position: relative;
            z-index: 1;
        }
        
        /* Стили для кнопок в панели быстрых действий */
        .stButton > button[href*="main_menu_sidebar"],
        .stButton > button[href*="new_analysis_sidebar"],
        .stButton > button[href*="stats_sidebar"],
        .stButton > button[href*="sample_report_sidebar"] {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 12px !important;
            padding: 15px 10px !important;
            text-align: center !important;
            color: #2c3e50 !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        
        .stButton > button[href*="main_menu_sidebar"]::before,
        .stButton > button[href*="new_analysis_sidebar"]::before,
        .stButton > button[href*="stats_sidebar"]::before,
        .stButton > button[href*="sample_report_sidebar"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }
        
        .stButton > button[href*="main_menu_sidebar"]:hover::before,
        .stButton > button[href*="new_analysis_sidebar"]:hover::before,
        .stButton > button[href*="stats_sidebar"]:hover::before,
        .stButton > button[href*="sample_report_sidebar"]:hover::before {
            left: 100%;
        }
        
        .stButton > button[href*="main_menu_sidebar"]:hover,
        .stButton > button[href*="new_analysis_sidebar"]:hover,
        .stButton > button[href*="stats_sidebar"]:hover,
        .stButton > button[href*="sample_report_sidebar"]:hover {
            transform: translateY(-3px) scale(1.02) !important;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2) !important;
            background: rgba(255, 255, 255, 1) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Стили для кнопки очистки */
        .stButton > button[href*="clear_history_sidebar"] {
            background: rgba(255, 107, 107, 0.95) !important;
            border: 2px solid rgba(255, 107, 107, 0.3) !important;
            border-radius: 12px !important;
            color: white !important;
            font-weight: 700 !important;
            padding: 15px !important;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[href*="clear_history_sidebar"]:hover {
            background: rgba(255, 107, 107, 1) !important;
            box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Анимации для появления кнопок */
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .stButton > button {
            animation: slideInUp 0.5s ease-out !important;
        }
        
        /* Специальные стили для expander */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
            border-radius: 8px !important;
            padding: 10px 15px !important;
            margin: 10px 0 !important;
            transition: all 0.3s ease !important;
        }
        
        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%) !important;
            transform: translateX(5px) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def get_status_class(status):
    """Получить CSS класс для статуса"""
    status_classes = {
        'optimal': 'status-optimal',
        'good': 'status-good',
        'warning': 'status-warning',
        'error': 'status-error',
        'info': 'status-info',
        'success': 'status-optimal'
    }
    return status_classes.get(status, 'status-info')

def get_trend_indicator(current, previous):
    """Получить индикатор тренда"""
    if current > previous:
        return "📈", "trend-up", f"+{current - previous}"
    elif current < previous:
        return "📉", "trend-down", f"{current - previous}"
    else:
        return "➡️", "trend-stable", "0"