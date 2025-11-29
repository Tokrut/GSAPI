"""
Макеты и страницы пользовательского интерфейса
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from report.generators import generate_full_report, create_download_link, generate_docx_report, create_docx_download_link
from config import TEXT_CONTENT, STATUS_MESSAGES
from report.generators import generate_full_report, create_download_link, generate_docx_report, create_docx_download_link, safe_get

def show_enhanced_welcome_message():
    """Улучшенное приветственное сообщение"""
    
    st.markdown(f"## {TEXT_CONTENT['welcome_title']}")
    
    # Вкладки в главном меню
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Главная", "Пример отчета", "История", "Сравнение", "Глубокий AI-анализ", "Как использовать"])
    
    with tab1:
        show_main_tab()
    
    with tab2:
        show_sample_report()
    
    with tab3:
        show_history_tab()
    
    with tab4:
        show_comparison_tab()
    
    with tab5:
        show_instructions_tab()

def show_main_tab():
    """Главная вкладка"""
    st.markdown("""
    Расширенный инструмент для анализа дружелюбности вашего сайта для генеративного поиска и AI-поисковых систем.

    ### Новые возможности:
    - **Расширенный анализ** - 70+ параметров качества
    - **Производительность** - оценка скорости загрузки
    - **Безопасность** - проверка HTTPS и заголовков
    - **Доступность** - анализ ARIA и семантики
    - **История анализов** - отслеживание прогресса
    - **Сравнительные отчеты** - анализ динамики изменений
    - **Интерактивные графики** - визуализация данных
    - **Полные отчеты** - скачивание детального анализа

    ### Что вы получите:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Детальный аудит сайта**")
        st.write("**Приоритетные рекомендации**")
        st.write("**Анализ производительности**")
        st.write("**Проверка безопасности**")
        st.write("**Оценка доступности**")
    
    with col2:
        st.write("**Анализ семантики**")
        st.write("**Технический анализ**")
        st.write("**Сравнение с лучшими практиками**")
        st.write("**Готовый план улучшений**")
        st.write("**Визуализация прогресса**")

    st.markdown("""
    ### Начните анализ:
    1. Введите URL сайта в поле слева
    2. Нажмите кнопку "Анализировать"
    3. Изучите результаты и скачайте полный отчет

    *Перейдите на вкладку "Пример отчета" чтобы увидеть образец анализа*
    """)

def show_sample_report():
    """Показ примера отчета"""
    
    sample_result = {
        'basic_info': {
            'analysis_date': '2024-01-15 14:30:00',
            'url': 'https://example.com',
            'final_url': 'https://example.com',
            'status_code': 200,
            'response_time': 1.2,
            'redirects': 0,
            'content_length': 145000,
            'is_https': True,
            'domain': 'example.com',
            'protocol': 'https'
        },
        'metadata': {
            'title': {
                'value': 'Пример компании - Услуги и решения для бизнеса',
                'length': 52,
                'optimal': True
            },
            'description': {
                'value': 'Профессиональные услуги для бизнеса. Решения под ключ. Опыт работы более 10 лет. Гарантия качества.',
                'length': 98,
                'optimal': False
            },
            'open_graph': {
                'exists': True,
                'count': 4,
                'tags': ['og:title', 'og:description', 'og:image', 'og:url'],
                'detailed': {
                    'og:title': 'Пример компании - Услуги и решения для бизнеса',
                    'og:description': 'Профессиональные услуги для бизнеса',
                    'og:image': 'https://example.com/image.jpg',
                    'og:url': 'https://example.com/'
                },
                'essential_count': 4
            },
            'twitter_cards': {
                'exists': True,
                'tags': {
                    'twitter:card': 'summary',
                    'twitter:title': 'Пример компании'
                },
                'count': 2
            },
            'canonical': {
                'exists': True, 
                'value': 'https://example.com/',
                'self_referencing': True
            },
            'robots': {
                'exists': True, 
                'value': 'index, follow',
                'noindex': False,
                'nofollow': False
            },
            'viewport': {
                'exists': True, 
                'value': 'width=device-width, initial-scale=1.0',
                'mobile_friendly': True
            },
            'charset': {
                'exists': True, 
                'value': 'UTF-8'
            }
        },
        'semantic_markup': {
            'schema_org': {
                'exists': True,
                'scripts': 2,
                'content': ['{"@context":"https://schema.org","@type":"Organization"...}'],
                'parsed': [{'@context': 'https://schema.org', '@type': 'Organization'}],
                'types': ['Organization']
            },
            'microdata': {
                'exists': True,
                'elements': 8,
                'types': ['https://schema.org/Organization', 'https://schema.org/BreadcrumbList'],
                'detailed': [
                    {
                        'type': 'https://schema.org/Organization',
                        'properties': {'name': 'Пример компании'}
                    }
                ]
            },
            'rdfa': {
                'elements': 2,
                'exists': True
            },
            'headings': {'h1': 1, 'h2': 4, 'h3': 8, 'h4': 0, 'h5': 0, 'h6': 0},
            'heading_hierarchy': {
                'h1_count': 1,
                'has_single_h1': True,
                'hierarchy_correct': True
            },
            'headings_structure': [
                {'level': 1, 'text': 'Главный заголовок', 'length': 18},
                {'level': 2, 'text': 'Подзаголовок 1', 'length': 14}
            ]
        },
        'content_structure': {
            'word_count': 850,
            'lists': {'ul': 3, 'ol': 1, 'total': 4},
            'tables': 1,
            'images': {'total': 12, 'with_alt': 10, 'alt_percentage': 83.33},
            'text_ratio': 45.5,
            'readability': {
                'score': 78.5,
                'level': 'Достаточно легко',
                'avg_sentence_length': 18.2,
                'avg_word_length': 5.1,
                'words': 850,
                'sentences': 47,
                'paragraphs': 15
            },
            'keyword_analysis': {
                'top_words': [('услуги', 15), ('бизнес', 12), ('решения', 10), ('компания', 8), ('опыт', 7)],
                'unique_words': 420,
                'keyword_density': 6.2
            },
            'multimedia': {
                'videos': 1,
                'iframes': 2,
                'audio': 0
            },
            'interactive': {
                'forms': 1,
                'buttons': 5,
                'inputs': 3
            }
        },
        'technical_seo': {
            'links': {
                'total': 45,
                'internal': 35,
                'external': 10,
                'with_anchor': 32
            },
            'enhanced_links': {
                'total': 45,
                'internal': 35,
                'external': 10,
                'nofollow': 3,
                'dofollow': 42,
                'with_anchor': 32,
                'empty_anchor': 13,
                'anchor_lengths': [5, 8, 12],
                'broken_links': 0
            },
            'images_analysis': {
                'total': 12,
                'with_alt': 10,
                'with_src': 12,
                'lazy_loaded': 2,
                'responsive': 8,
                'average_size': 0
            },
            'important_tags': {
                'canonical': True,
                'robots_txt': True,
                'sitemap': True,
                'favicon': True,
                'manifest': False,
                'amp_html': False
            },
            'url_structure': {
                'depth': 1,
                'has_trailing_slash': True,
                'has_uppercase': False,
                'has_parameters': False
            }
        },
        'performance': {
            'response_time': 1.2,
            'page_size': 145000,
            'html_size': 85000,
            'image_count': 12,
            'script_count': 8,
            'stylesheet_count': 3,
            'score': 88,
            'level': 'Хорошая',
            'html_complexity': 120000,
            'dom_elements': 150,
            'dom_depth': 5,
            'resource_requests': 23,
            'inline_styles': 5,
            'external_scripts': 6,
            'inline_scripts': 2
        },
        'security': {
            'https': {
                'enabled': True,
                'mixed_content': False
            },
            'headers': {
                'hsts': True,
                'x_frame_options': True,
                'x_content_type_options': True,
                'x_xss_protection': True,
                'content_security_policy': False,
                'referrer_policy': True
            }
        },
        'accessibility': {
            'aria': {
                'labels': 5,
                'roles': 3,
                'describedby': 2
            },
            'semantic_html': {
                'header': 1,
                'footer': 1,
                'nav': 1,
                'main': 1,
                'article': 2,
                'section': 3,
                'aside': 0
            },
            'forms': {
                'total': 1,
                'with_labels': 1,
                'with_placeholders': 1
            }
        },
        'score': 82,
        'warnings': [
            "Meta description короче рекомендованного (98 из 120-160 символов)",
            "13 ссылок без анкор-текста",
            "Отсутствует Content Security Policy"
        ],
        'critical_issues': [],
        'recommendations': [
            "Увеличить длину meta description до 120-160 символов",
            "Добавить анкор-тексты ко всем ссылкам",
            "Внедрить Content Security Policy"
        ]
    }
    
    st.markdown(f"## {TEXT_CONTENT['sample_report_title']}")
    st.markdown("---")
    
    # Показываем сокращенную версию примера отчета
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ключевые метрики")
        st.metric("Общая оценка", "82/100", "Хорошо")
        st.metric("Производительность", "88/100", "Отлично")
        st.metric("Объем контента", "850 слов", "Достаточно")
        st.metric("Изображения с alt", "83%", "Хорошо")
        st.metric("Безопасность", "HTTPS", "")
    
    with col2:
        st.subheader("Сильные стороны")
        st.success("• Оптимальный title тег")
        st.success("• Наличие Schema.org разметки")
        st.success("• Корректная иерархия заголовков")
        st.success("• Хорошая структура контента")
        st.success("• Высокая производительность")
        st.success("• Настройки безопасности")
    
    st.markdown("---")
    st.subheader("Области для улучшения")
    
    col_warn1, col_warn2 = st.columns(2)
    with col_warn1:
        st.warning("**Meta Description**")
        st.write("Текущая длина: 98 символов")
        st.write("Рекомендуется: 120-160 символов")
        
        st.warning("**Анкор-тексты ссылок**")
        st.write("13 ссылок без анкор-текста")
        st.write("Рекомендуется добавить описательные анкоры")
    
    with col_warn2:
        st.warning("**Content Security Policy**")
        st.write("Заголовок CSP отсутствует")
        st.write("Рекомендуется внедрить политику безопасности")
        
        st.warning("**Семантическая разметка**")
        st.write("Можно добавить больше микроразметки")
        st.write("Рекомендуется расширить Schema.org")
    
    st.markdown("---")
    st.subheader("Пример полного отчета")
    
    # Показываем часть полного отчета
    sample_report = generate_full_report(sample_result)
    report_preview = "\n".join(sample_report.split("\n")[:50]) + "\n\n... [полный отчет содержит еще 150+ строк анализа]"
    
    with st.expander("Просмотреть часть полного отчета", expanded=False):
        st.text_area("Пример отчета", report_preview, height=300, label_visibility="collapsed")
    
    # DOCX отчет (текстовые отчеты отключены)
    docx_report = generate_docx_report(sample_result)
    if docx_report:
        st.markdown(create_docx_download_link(docx_report, "geo_sample_report.docx"), unsafe_allow_html=True)
    else:
        st.info("Пример отчета в формате DOCX временно недоступен")

def show_history_tab():
    """Вкладка с историей запросов"""
    st.markdown(f"## {TEXT_CONTENT['history_title']}")
    
    if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
        st.info(STATUS_MESSAGES['no_history'])
        return
    
    # Статистика по истории
    total_analyses = len(st.session_state.analysis_history)
    avg_score = sum(safe_get(item, ['score'], 0) for item in st.session_state.analysis_history) / total_analyses
    best_score = max(safe_get(item, ['score'], 0) for item in st.session_state.analysis_history)
    worst_score = min(safe_get(item, ['score'], 0) for item in st.session_state.analysis_history)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Всего анализов", total_analyses)
    with col2:
        st.metric("Средняя оценка", f"{avg_score:.1f}/100")
    with col3:
        st.metric("Лучший результат", f"{best_score}/100")
    with col4:
        st.metric("Худший результат", f"{worst_score}/100")
    
    st.markdown("---")
    
    # Список анализов
    for i, history_item in enumerate(reversed(st.session_state.analysis_history)):
        with st.expander(f"{safe_get(history_item, ['basic_info', 'url'], 'URL не доступен')} - {safe_get(history_item, ['score'], 0)}/100 - {safe_get(history_item, ['basic_info', 'analysis_date'], 'Дата не доступна')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Основная информация с безопасным доступом
                st.write(f"**URL:** {safe_get(history_item, ['basic_info', 'url'], 'Не доступен')}")
                st.write(f"**Дата анализа:** {safe_get(history_item, ['basic_info', 'analysis_date'], 'Не доступна')}")
                st.write(f"**Оценка:** {safe_get(history_item, ['score'], 0)}/100")
                
                score = safe_get(history_item, ['score'], 0)
                status = 'Отлично' if score >= 80 else 'Хорошо' if score >= 60 else 'Требует улучшений' if score >= 40 else 'Критически низкий'
                st.write(f"**Статус:** {status}")
                
                # Ключевые метрики с безопасным доступом
                st.write("**Ключевые метрики:**")
                col_metrics1, col_metrics2 = st.columns(2)
                with col_metrics1:
                    st.write(f"• Время загрузки: {safe_get(history_item, ['basic_info', 'response_time'], 0)}с")
                    st.write(f"• Слов в тексте: {safe_get(history_item, ['content_structure', 'word_count'], 0)}")
                    st.write(f"• Изображения с alt: {safe_get(history_item, ['content_structure', 'images', 'alt_percentage'], 0)}%")
                with col_metrics2:
                    st.write(f"• Внутренние ссылки: {safe_get(history_item, ['technical_seo', 'links', 'internal'], 0)}")
                    st.write(f"• H1 заголовки: {safe_get(history_item, ['semantic_markup', 'heading_hierarchy', 'h1_count'], 0)}")
                    st.write(f"• Производительность: {safe_get(history_item, ['performance', 'score'], 0)}/100")
            
            with col2:
                # Кнопки действий
                if st.button("Просмотреть", key=f"view_{i}", width='stretch'):
                    st.session_state.current_analysis = history_item
                    st.rerun()
                
                # Скачивание отчетов
                full_report = generate_full_report(history_item)
                analysis_date = safe_get(history_item, ['basic_info', 'analysis_date'], 'unknown').replace(' ', '_').replace(':', '')
                st.markdown(create_download_link(full_report, f"geo_report_{analysis_date}.txt"), 
                           unsafe_allow_html=True)
                
                docx_report = generate_docx_report(history_item)
                if docx_report:
                    st.markdown(create_docx_download_link(docx_report, f"geo_report_{analysis_date}.docx"), 
                               unsafe_allow_html=True)
            
            # Разделитель между элементами истории
            if i < len(st.session_state.analysis_history) - 1:
                st.markdown("---")
                
def show_deep_analysis_tab():
    """Вкладка глубокого AI-анализа с конкурентами"""
    st.markdown("##  Глубокий AI-анализ с конкурентами")
    
    st.info("""
    ###  Что такое глубокий AI-анализ?
    
    Эта функция использует современные LLM-модели (DeepSeek, Grok, Bert-Nebulon) для:
    - **Поиска конкурентов** - автоматический поиск аналогичных сайтов в вашей нише
    - **Сравнительного анализа** - детальное сравнение с 3-5 конкурентами
    - **Стратегических рекомендаций** - AI-рекомендации для улучшения позиций
    - **Рыночной позиции** - определение вашего места среди конкурентов
    
     **Внимание:** Этот анализ требует больше времени (2-5 минут) и API-запросов к LLM
    """)

    # Форма для глубокого анализа
    with st.form("deep_analysis_form"):
        url = st.text_input("Введите URL для глубокого анализа:", 
                           placeholder="https://example.com",
                           help="URL вашего сайта для анализа и поиска конкурентов")
        
        max_competitors = st.slider("Количество конкурентов для поиска:", 
                                   min_value=1, max_value=5, value=3,
                                   help="Сколько аналогичных сайтов найти для сравнения")
        
        # Дополнительные настройки
        with st.expander("Расширенные настройки"):
            use_selenium = st.checkbox("Использовать расширенный анализ (Selenium)", 
                                      value=False,
                                      help="Для сайтов с JavaScript")
            enable_llm = st.checkbox("Включить стандартный AI-анализ", 
                                   value=True,
                                   help="Базовый GEO анализ перед глубоким")
        
        analyze_button = st.form_submit_button("Запустить глубокий AI-анализ", 
                                             type="primary",
                                             help="Запуск комплексного анализа с поиском конкурентов")
    
    # Обработка запуска анализа
    if analyze_button and url:
        with st.spinner("Запускаем глубокий AI-анализ... Это займет 2-5 минут"):
            try:
                from analyzer.enhanced_analyzer import EnhancedWebsiteAnalyzer
                
                # Создаем анализатор с включенным глубоким анализом
                analyzer = EnhancedWebsiteAnalyzer(
                    use_selenium=use_selenium,
                    enable_llm_analysis=enable_llm,
                    enable_deep_analysis=True
                )
                
                # Выполняем глубокий анализ
                deep_result = analyzer.deep_analyze_with_competitors(
                    target_url=url,
                    max_competitors=max_competitors
                )
                
                # Сохраняем результат в session state
                st.session_state.deep_analysis_result = deep_result
                st.session_state.deep_analysis_url = url
                
                st.success("Глубокий AI-анализ завершен успешно!")
                
            except Exception as e:
                st.error(f"Ошибка глубокого анализа: {str(e)}")
                st.info("Попробуйте уменьшить количество конкурентов или проверьте URL")
    
    # Показываем результаты если они есть
    if 'deep_analysis_result' in st.session_state:
        display_deep_analysis_results(st.session_state.deep_analysis_result)


def display_deep_analysis_results(deep_result):
    """Отображение результатов глубокого анализа"""
    
    if 'error' in deep_result:
        st.error(f"Ошибка анализа: {deep_result['error']}")
        return
    
    st.markdown("---")
    st.markdown("##  Результаты глубокого AI-анализа")
    
    # Основная информация
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Целевой сайт", deep_result.get('target_url', 'N/A'))
    with col2:
        competitors_count = deep_result.get('competitors_count', 0)
        st.metric("Проанализировано конкурентов", competitors_count)
    with col3:
        if 'deep_analysis' in deep_result and 'target_ranking' in deep_result['deep_analysis']:
            ranking = deep_result['deep_analysis']['target_ranking']
            position = ranking.get('position', 'N/A')
            total = ranking.get('total_sites', 'N/A')
            st.metric("Позиция в рейтинге", f"{position} из {total}")
    
    # Детальное отображение результатов
    if 'deep_analysis' in deep_result:
        deep_analysis = deep_result['deep_analysis']
        
        # Рейтинг сайтов
        st.subheader("Рейтинг сайтов")
        if 'ranking' in deep_analysis and deep_analysis['ranking']:
            for i, site in enumerate(deep_analysis['ranking'][:5], 1):
                status = "Ваш сайт" if site.get('is_target') else "🏁 Конкурент"
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.write(f"**{i}.**")
                with col2:
                    st.write(f"{site.get('url', 'N/A')}")
                with col3:
                    st.write(f"**{site.get('overall_score', 0):.1f}/100** {status}")
        
        # Анализ конкурентной позиции
        if 'strengths_weaknesses' in deep_analysis:
            st.subheader("Конкурентная позиция")
            sw = deep_analysis['strengths_weaknesses']
            
            col_sw1, col_sw2 = st.columns(2)
            with col_sw1:
                if sw.get('strengths'):
                    st.success("**Сильные стороны:**")
                    for strength in sw['strengths']:
                        st.write(f"• {strength}")
            with col_sw2:
                if sw.get('weaknesses'):
                    st.error("**Слабые стороны:**")
                    for weakness in sw['weaknesses']:
                        st.write(f"• {weakness}")
            
            if sw.get('opportunities'):
                st.info("**Возможности для улучшения:**")
                for opportunity in sw['opportunities']:
                    st.write(f"• {opportunity}")
        
        # Стратегические рекомендации
        if 'strategic_recommendations' in deep_analysis:
            st.subheader("Стратегические рекомендации")
            for rec in deep_analysis['strategic_recommendations']:
                st.info(f"• {rec}")
    
    # Кнопка сохранения отчета
    if st.button("Сохранить отчет о глубоком анализе"):
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
        st.session_state.analysis_history.append(deep_result)
        st.success("Отчет сохранен в истории анализов!")


def show_comparison_tab():
    """Вкладка сравнительного анализа"""
    st.markdown("##  Сравнительный анализ")
    
    if 'analysis_history' not in st.session_state or len(st.session_state.analysis_history) < 2:
        st.info("Для сравнительного анализа необходимо как минимум 2 завершенных анализа")
        return
    
    try:
        from ui.comparison_components import (
            display_comparison_analysis,
            display_trends_analysis,
            display_improvement_recommendations,
            display_competitive_analysis
        )
        
        # Сравнительный анализ
        display_comparison_analysis(st.session_state.analysis_history)
        
        st.markdown("---")
        
        # Анализ трендов
        display_trends_analysis(st.session_state.analysis_history)
        
        st.markdown("---")
        
        # Рекомендации по улучшению
        display_improvement_recommendations(st.session_state.analysis_history)
        
        st.markdown("---")
        
        # Сравнение с лучшими практиками
        display_competitive_analysis(st.session_state.analysis_history)
        
    except ImportError as e:
        st.warning("Функции сравнительного анализа временно недоступны")
        st.info("""
        **Доступные возможности сравнительного анализа:**
        - Сравнение оценок между разными анализами
        - Визуализация трендов изменений
        - Рекомендации на основе динамики
        - Сравнение с лучшими отраслевыми практиками
        """)
        
def show_instructions_tab():
    """Вкладка с инструкциями"""
    st.markdown(f"## {TEXT_CONTENT['instructions_title']}")
    
    st.markdown("""
    ### Шаг 1: Подготовка
    - Убедитесь, что сайт доступен из публичной сети
    - Подготовьте список ключевых страниц для анализа
    - Имейте доступ к CMS для внедрения изменений

    ### Шаг 2: Анализ
    1. Введите полный URL страницы (включая https://)
    2. Дождитесь завершения анализа (обычно 10-30 секунд)
    3. Изучите результаты по категориям

    ### Шаг 3: Интерпретация результатов

    **Оценки:**
    - 🟢 80-100: Отличные показатели
    - 🟡 60-79: Хорошие показатели
    - 🟠 40-59: Требует улучшений
    - 🔴 0-39: Критически низкие показатели

    **Категории анализа:**
    - **Мета-данные** - title, description, Open Graph, Twitter Cards
    - **Семантическая разметка** - Schema.org, микроразметка, заголовки
    - **Структура контента** - объем текста, читаемость, ключевые слова
    - **Техническое SEO** - ссылки, изображения, URL структура
    - **Производительность** - скорость загрузки, оптимизация
    - **Безопасность** - HTTPS, заголовки безопасности
    - **Доступность** - ARIA атрибуты, семантические теги

    **Приоритеты исправлений:**
    1. Критические проблемы - исправьте в первую очередь
    2. Предупреждения - улучшите в ближайшее время
    3. Рекомендации - опциональные улучшения

    ### Шаг 4: Внедрение улучшений
    - Скачайте полный отчет для детального плана
    - Внедряйте изменения поэтапно
    - Проверяйте результаты через 2-4 недели
    - Используйте сравнительный анализ для отслеживания прогресса

    ### Советы по использованию:
    - Анализируйте ключевые страницы сайта
    - Сравнивайте результаты с конкурентами
    - Регулярно проводите аудит (раз в 1-3 месяца)
    - Фокусируйтесь на пользовательском опыте
    - Используйте историю анализов для отслеживания трендов
    """)

def setup_sidebar():
    """Настройка боковой панели"""
    with st.sidebar:
        st.header("🔧 Настройки анализа")
        url = st.text_input("Введите URL для анализа:", placeholder="https://example.com")
        
        # Дополнительные опции
        with st.expander("Дополнительные настройки"):
            use_selenium = st.checkbox("Использовать расширенный анализ (Selenium)", value=False, 
                                     help="Для сайтов с большим количеством JavaScript")
            timeout = st.slider("Таймаут анализа (секунды)", 10, 60, 15)
        
        # Кнопки в двух колонках
        col1, col2 = st.columns(2)
        with col1:
            analyze_button = st.button(TEXT_CONTENT['analyze_button'], type="primary", width='stretch')
        with col2:
            main_menu_button = st.button(TEXT_CONTENT['main_menu_button'], width='stretch')
        
        # Отдельная кнопка для очистки истории
        clear_history = st.button(TEXT_CONTENT['clear_history_button'], width='stretch')
        
        if clear_history:
            st.session_state.analysis_history = []
            st.success("История анализов очищена!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### Что анализируется:
        - **Мета-данные** - title, description, Open Graph, Twitter Cards
        - **Семантика** - Schema.org, микроразметка, заголовки
        - **Контент** - структура, читаемость, ключевые слова
        - **Техника** - ссылки, производительность, SEO-теги
        - **Производительность** - скорость, оптимизация
        - **Безопасность** - HTTPS, заголовки безопасности
        - **Доступность** - ARIA, семантические теги
        """)
        
        # История анализов
        if 'analysis_history' in st.session_state and st.session_state.analysis_history:
            st.markdown("---")
            st.markdown("### Быстрый доступ к истории")
            for i, history_item in enumerate(st.session_state.analysis_history[-5:]):
                if st.button(f"{history_item['basic_info']['url'][:30]}... - {history_item['score']}/100", 
                           key=f"sidebar_history_{i}", width='stretch'):
                    st.session_state.current_analysis = history_item
                    st.rerun()
        
        return url, analyze_button, main_menu_button, use_selenium, timeout