"""
Главный файл приложения GEO Analyzer Pro
"""

import streamlit as st
import time
from datetime import datetime
from analyzer.enhanced_analyzer import EnhancedWebsiteAnalyzer
from analyzer.threaded_analyzer import ThreadedWebsiteAnalyzer, BatchAnalysisManager
from ui.components import display_enhanced_results
from ui.layouts import show_enhanced_welcome_message, show_comparison_tab
from ui.auth_components import show_login_form, show_register_form, show_user_profile, show_auth_sidebar
from ui.subscription_components import show_subscription_selection, show_subscription_sidebar
from ui.sidebar_components import display_enhanced_sidebar
from ui.navigation_components import display_main_menu_button
from auth.service import AuthService
from config import setup_page_config, apply_custom_styles, TEXT_CONTENT, STATUS_MESSAGES, AUTH_CONFIG, LLM_CONFIG

def check_session_timeout():
    """Проверка времени сессии"""
    if 'login_time' in st.session_state:
        session_duration = datetime.now() - st.session_state.login_time
        if session_duration.total_seconds() > AUTH_CONFIG['session_timeout']:
            st.session_state.pop('user', None)
            st.session_state.pop('login_time', None)
            st.session_state.analysis_history = []
            st.warning("Время сессии истекло. Пожалуйста, войдите снова.")
            return False
    return True

def reset_to_main_menu():
    """Сброс состояния приложения к главному меню"""
    st.session_state.current_analysis = None
    st.rerun()

def load_user_history(auth_service: AuthService, username: str):
    """Загрузка истории анализов пользователя с миграцией старых данных"""
    try:
        history = auth_service.get_user_analysis_history(username)
        # Мигрируем старые данные
        migrated_history = []
        for item in history:
            migrated_item = migrate_old_analysis_data(item)
            migrated_history.append(migrated_item)
        
        st.session_state.analysis_history = migrated_history
    except Exception as e:
        st.error(f"Ошибка загрузки истории: {e}")
        st.session_state.analysis_history = []

def save_current_analysis(auth_service: AuthService, username: str, analysis_data: dict):
    """Сохранение текущего анализа в историю пользователя"""
    try:
        # Сохраняем анализ в базу данных
        success = auth_service.save_user_analysis(username, analysis_data)
        if success:
            # Обновляем локальную историю
            if 'analysis_history' not in st.session_state:
                st.session_state.analysis_history = []
            st.session_state.analysis_history.append(analysis_data)
        return success
    except Exception as e:
        st.error(f"Ошибка сохранения анализа: {e}")
        return False

def migrate_old_analysis_data(analysis_data):
    """Миграция старых данных анализа для совместимости с новой структурой"""
    if 'security' not in analysis_data:
        analysis_data['security'] = {
            'https': {
                'enabled': analysis_data.get('basic_info', {}).get('is_https', False),
                'mixed_content': False
            },
            'headers': {
                'hsts': False,
                'x_frame_options': False,
                'x_content_type_options': False,
                'x_xss_protection': False,
                'content_security_policy': False,
                'referrer_policy': False
            }
        }
    
    if 'accessibility' not in analysis_data:
        analysis_data['accessibility'] = {
            'aria': {
                'labels': 0,
                'roles': 0,
                'describedby': 0
            },
            'semantic_html': {
                'header': 0,
                'footer': 0,
                'nav': 0,
                'main': 0,
                'article': 0,
                'section': 0,
                'aside': 0
            },
            'forms': {
                'total': 0,
                'with_labels': 0,
                'with_placeholders': 0
            }
        }
    
    if 'recommendations' not in analysis_data:
        from report.generators import generate_additional_recommendations
        recommendations_text = generate_additional_recommendations(analysis_data)
        analysis_data['recommendations'] = [rec[2:] for rec in recommendations_text.split('\n') if rec.startswith('• ')]
    # Миграция старых рекомендаций в новый формат
    if 'recommendations' in analysis_data and analysis_data['recommendations']:
        if isinstance(analysis_data['recommendations'][0], str):
            # Конвертируем старые строковые рекомендации в новый формат
            new_recommendations = []
            for rec_text in analysis_data['recommendations']:
                # Сопоставляем старые тексты с новыми ключами примеров
                example_mapping = {
                    'Добавить title тег': 'missing_title',
                    'Создать уникальный meta description': 'missing_description', 
                    'Увеличить объем текстового контента': 'low_content',
                    'Добавить alt-тексты': 'poor_alt_texts',
                    'Оптимизировать время загрузки': 'slow_loading',
                    'Уменьшить размер страницы': 'slow_loading'
                }
                
                rec_type = 'other'
                example_key = None
                
                for key_pattern, ex_key in example_mapping.items():
                    if key_pattern in rec_text:
                        example_key = ex_key
                        break
                
                new_recommendations.append({
                    'text': rec_text,
                    'type': rec_type,
                    'example_key': example_key
                })
            
            analysis_data['recommendations'] = new_recommendations
    
    return analysis_data

def _handle_batch_analysis(url, max_threads, enable_llm, use_selenium, enable_deep_analysis, auth_service):
    """Обработка пакетного анализа нескольких URL"""
    try:
        # Разделяем URL по запятым или переносам строк
        urls = [u.strip() for u in url.split(',') if u.strip()]
        
        if not urls:
            st.error("Не указаны URL для пакетного анализа")
            return
        
        st.info(f"Запуск пакетного анализа {len(urls)} URL...")
        
        # Создаем менеджер пакетного анализа
        batch_manager = BatchAnalysisManager(max_concurrent_analyses=max_threads)
        
        # Конфигурация анализа
        analysis_config = {
            'enable_llm_analysis': enable_llm,
            'enable_deep_analysis': enable_deep_analysis,
            'use_selenium': use_selenium
        }
        
        # Запускаем пакетный анализ
        batch_id = batch_manager.start_batch_analysis(urls, analysis_config)
        
        # Отображаем прогресс
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.empty()
        
        # Мониторим прогресс
        while True:
            status = batch_manager.get_batch_status(batch_id)
            
            if status['status'] == 'completed':
                progress_bar.progress(100)
                status_text.success("Пакетный анализ завершен!")
                
                # Показываем результаты
                results = batch_manager.get_batch_results(batch_id)
                successful = status['successful_analyses']
                failed = status['total_urls'] - successful
                
                with results_container.container():
                    st.success(f"Результаты: {successful} успешно, {failed} с ошибками")
                    
                    # Сохраняем результаты в историю
                    for url, result in results.items():
                        if 'error' not in result:
                            result = migrate_old_analysis_data(result)
                            if st.session_state.user:
                                save_current_analysis(auth_service, st.session_state.user.username, result)
                            else:
                                if 'analysis_history' not in st.session_state:
                                    st.session_state.analysis_history = []
                                st.session_state.analysis_history.append(result)
                
                break
                
            elif status['status'] == 'running':
                # Обновляем прогресс
                progress_data = status.get('progress')
                if progress_data:
                    progress = progress_data.get('percentage', 0)
                    progress_bar.progress(progress)
                    status_text.text(f"{progress_data.get('message', 'Анализируется...')} ({progress}%)")
                else:
                    # Fallback прогресс
                    progress = min(90, len(status.get('completed_urls', [])) / len(urls) * 100)
                    progress_bar.progress(int(progress))
                    status_text.text(f"Анализируется... {int(progress)}%")
                
            elif status['status'] == 'cancelled':
                progress_bar.progress(0)
                status_text.error("Пакетный анализ отменен")
                break
                
            elif 'error' in status:
                progress_bar.progress(0)
                status_text.error(f"Ошибка: {status['error']}")
                break
            
            time.sleep(1)  # Пауза между проверками
            
    except Exception as e:
        st.error(f"Ошибка пакетного анализа: {str(e)}")
        
def main():
    """Основная функция приложения с LLM-интеграцией"""
    
    # Настройка страницы
    setup_page_config()
    apply_custom_styles()
    
    # Инициализация сервиса аутентификации
    auth_service = AuthService()
    
    # Заголовок приложения с указанием LLM-функций
    st.title(f"{TEXT_CONTENT['app_title']}")
    st.subheader(TEXT_CONTENT['app_subtitle'])  # ИСПРАВЛЕНО: subtitle -> subheader
    
    # Информация о LLM-интеграции
    st.info("""
    **Новые возможности с AI-анализом:**
    - Анализ дружелюбности контента для генеративного поиска (GEO)
    - Оценка потенциала цитирования в AI-ответах
    - Рекомендации от Bert-Nebulon, Grok и DeepSeek
    - Анализ структуры clear answers
    """)
    
    # Инициализация session state
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'current_analysis' not in st.session_state:
        st.session_state.current_analysis = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'show_profile' not in st.session_state:
        st.session_state.show_profile = False
    if 'show_stats' not in st.session_state:
        st.session_state.show_stats = False
    if 'show_sample' not in st.session_state:
        st.session_state.show_sample = False
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False
    if 'show_subscription' not in st.session_state:
        st.session_state.show_subscription = False
    if 'enable_llm_analysis' not in st.session_state:
        st.session_state.enable_llm_analysis = LLM_CONFIG['enabled']
    if 'use_threaded_analysis' not in st.session_state:
        st.session_state.use_threaded_analysis = True
    if 'analysis_progress' not in st.session_state:
        st.session_state.analysis_progress = None
    if 'batch_analysis_active' not in st.session_state:
        st.session_state.batch_analysis_active = False
    if 'batch_analysis_urls' not in st.session_state:
        st.session_state.batch_analysis_urls = []
    
    # Проверка времени сессии
    check_session_timeout()
    
    # Основной layout с двумя колонками
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        # Улучшенная боковая панель
        if st.session_state.user:
            login_time = st.session_state.get('login_time')
            display_enhanced_sidebar(st.session_state.user, login_time)
            # Информация о подписке
            show_subscription_sidebar(auth_service)
        else:
            # Для неавторизованных пользователей - упрощенная панель
            st.markdown("### Вход в систему")
            show_auth_sidebar(auth_service)
            
            st.markdown("---")
            st.markdown("### Преимущества с AI")
            st.info("""
            AI-анализ GEO оптимизации  
            Оценка цитирования в AI-поиске  
            Рекомендации от 3+ моделей  
            Приоритетная обработка
            """)
    
    with col_main:
        # Форма анализа сайта с LLM-опциями
        st.markdown("### Анализ сайта с AI")
        
        with st.form("analysis_form"):
            url = st.text_input(
                "Введите URL для анализа:",
                placeholder="https://example.com",
                help="Введите полный URL включая https://"
            )
            
            # Дополнительные настройки
            with st.expander("Расширенные настройки AI-анализа"):
                col1, col2 = st.columns(2)
                
                with col1:
                    use_selenium = st.checkbox(
                        "Использовать расширенный анализ", 
                        value=False,
                        help="Для сайтов с JavaScript (требуется больше времени)"
                    )
                    enable_llm = st.checkbox(
                        "Включить AI-анализ GEO", 
                        value=st.session_state.enable_llm_analysis,
                        help="Анализ с помощью Bert-Nebulon, Grok и DeepSeek"
                    )
                    enable_deep_analysis = st.checkbox(
                        "Включить глубокий анализ с конкурентами", 
                        value=False,
                        help="Поиск и сравнение с аналогичными сайтами (требует больше времени)"
                    )
                    
                with col2:
                    use_threaded = st.checkbox(
                        "🔧 Использовать многопоточность", 
                        value=st.session_state.use_threaded_analysis,
                        help="Параллельная обработка для ускорения анализа"
                    )
                    max_threads = st.slider("Макс. потоков", 1, 10, 3, 
                                         help="Количество параллельных запросов")
                    batch_mode = st.checkbox(
                        "Пакетный анализ (несколько сайтов)", 
                        value=False,
                        help="Анализ нескольких URL одновременно"
                    )
            
            col_analyze, col_clear = st.columns(2)
            with col_analyze:
                analyze_button = st.form_submit_button(
                    "Начать AI-анализ",
                    type="primary",
                    width='stretch',
                    key="analyze_button_main"
                )
            with col_clear:
                clear_button = st.form_submit_button(
                    "Очистить форму",
                    width='stretch',
                    key="clear_button_main"
                )
        
        # Обработка очистки формы
        if clear_button:
            st.rerun()
        
        # Сохраняем настройку LLM
        st.session_state.enable_llm_analysis = enable_llm
        
        # Обработка кнопки возврата в главное меню
        if st.session_state.current_analysis and st.button(f"{TEXT_CONTENT['main_menu_button']}", width='stretch', key="main_menu_button"):
            reset_to_main_menu()
        
        # Пакетный анализ
        if batch_mode and analyze_button:
            _handle_batch_analysis(url, max_threads, enable_llm, use_selenium, enable_deep_analysis, auth_service)
        
        # Основная логика приложения
        elif analyze_button and url and not batch_mode:
            # Проверка подписки для авторизованных пользователей
            if st.session_state.user:
                can_analyze, message = auth_service.can_user_perform_analysis(st.session_state.user.username)
                if not can_analyze:
                    st.error(f"Ошибка: {message}")
                    st.info("Перейдите в раздел 'Управление подпиской' для выбора подходящего тарифа")
                    return
            
            # Проверка возможности использования глубокого анализа
            if enable_deep_analysis and st.session_state.user:
                can_deep_analyze, message = auth_service.can_user_use_deep_analysis(st.session_state.user.username)
                if not can_deep_analyze:
                    st.error(f"Ошибка: {message}")
                    st.info("Для использования глубокого анализа требуется подписка Pro+")
                    return
            
            with st.spinner(STATUS_MESSAGES['analyzing']):
                try:
                    # Выбираем анализатор в зависимости от настроек многопоточности
                    if use_threaded:
                        # Используем многопоточный анализатор
                        threaded_analyzer = ThreadedWebsiteAnalyzer(
                            max_workers=max_threads,
                            enable_llm_analysis=st.session_state.enable_llm_analysis,
                            enable_deep_analysis=enable_deep_analysis
                        )
                        
                        # Функция для обновления прогресса
                        def update_progress(progress_data):
                            if 'step' in progress_data:
                                st.session_state.analysis_progress = progress_data
                            elif 'completed_count' in progress_data:
                                st.session_state.analysis_progress = {
                                    'step': 'parallel_analysis',
                                    'percentage': int((progress_data['completed_count'] / progress_data['total_count']) * 100),
                                    'message': f"Анализировано {progress_data['completed_count']} из {progress_data['total_count']} URL",
                                    'timestamp': datetime.now().isoformat()
                                }
                        
                        # Выполняем анализ с отслеживанием прогресса
                        if enable_deep_analysis:
                            result = threaded_analyzer.deep_analyze_with_competitors_threaded(url, max_competitors=3)
                        else:
                            result = threaded_analyzer.analyze_with_progress(
                                url, 
                                use_selenium=use_selenium,
                                enable_deep_analysis=enable_deep_analysis,
                                progress_callback=update_progress
                            )
                    else:
                        # Используем обычный анализатор
                        analyzer = EnhancedWebsiteAnalyzer(
                            use_selenium=use_selenium,
                            enable_llm_analysis=st.session_state.enable_llm_analysis,
                            enable_deep_analysis=enable_deep_analysis
                        )
                        
                        # Выполняем анализ в зависимости от настроек
                        if enable_deep_analysis:
                            result = analyzer.deep_analyze_with_competitors(url, max_competitors=3)
                        else:
                            result = analyzer.analyze_url(url)
                    
                    if result:
                        # Мигрируем данные если нужно
                        result = migrate_old_analysis_data(result)
                        
                        # Добавляем информацию о методе анализа
                        result['analysis_method'] = 'threaded' if use_threaded else 'standard'
                        if use_threaded:
                            result['thread_count'] = max_threads
                        
                        # Сохраняем анализ
                        if st.session_state.user:
                            # Для авторизованных пользователей сохраняем в базу
                            save_current_analysis(auth_service, st.session_state.user.username, result)
                        else:
                            # Для неавторизованных пользователей сохраняем только в сессию
                            if 'analysis_history' not in st.session_state:
                                st.session_state.analysis_history = []
                            st.session_state.analysis_history.append(result)
                        
                        st.session_state.current_analysis = result
                        
                        # Показываем успешное сообщение с информацией о LLM
                        success_message = "Анализ завершен успешно!"
                        if use_threaded:
                            success_message += f" Использовано потоков: {max_threads}"
                        if st.session_state.enable_llm_analysis:
                            success_message += " | AI-анализ: Bert-Nebulon, Grok, DeepSeek"
                        
                        st.success(success_message)
                        display_enhanced_results(result)
                    else:
                        st.error(STATUS_MESSAGES['analysis_failed'])
                except Exception as e:
                    st.error(f"Ошибка при анализе: {str(e)}")
                    st.info("Попробуйте использовать расширенный анализ для сайтов с JavaScript")
        
        elif st.session_state.current_analysis:
            # Показываем последний анализ
            display_enhanced_results(st.session_state.current_analysis)
        
        else:
            # Показываем приветственное сообщение или специальные страницы
            if st.session_state.get('show_comparison'):
                show_comparison_tab()
            elif st.session_state.get('show_profile'):
                st.markdown("---")
                show_user_profile(auth_service)
            elif st.session_state.get('show_subscription'):
                st.markdown("---")
                if st.session_state.user:
                    show_subscription_selection(auth_service, st.session_state.user.username)
                else:
                    st.error("Для управления подпиской необходимо войти в систему")
            elif st.session_state.get('show_stats'):
                st.markdown("---")
                st.subheader("Детальная статистика")
                # Здесь можно добавить расширенную статистику для авторизованных пользователей
            elif st.session_state.get('show_sample'):
                st.markdown("---")
                from ui.layouts import show_sample_report
                show_sample_report()
            else:
                # Показываем приветственное сообщение с информацией о LLM
                if st.session_state.user:
                    user = st.session_state.user
                    st.markdown(f"### Добро пожаловать, {user.username}!")
                    
                    # Быстрая статистика для авторизованных пользователей
                    total_analyses = len(st.session_state.analysis_history)
                    if total_analyses > 0:
                        avg_score = sum(item['score'] for item in st.session_state.analysis_history) / total_analyses
                        best_score = max(item['score'] for item in st.session_state.analysis_history)
                        
                        # Средняя GEO оценка от LLM
                        llm_scores = [item.get('llm_analysis', {}).get('overall_geo_score', 0) 
                                    for item in st.session_state.analysis_history 
                                    if item.get('llm_analysis')]
                        avg_geo_score = sum(llm_scores) / len(llm_scores) if llm_scores else 0
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Всего анализов", total_analyses)
                        with col2:
                            st.metric("Средняя оценка", f"{avg_score:.1f}/100")
                        with col3:
                            st.metric("Лучший результат", f"{best_score}/100")
                        with col4:
                            st.metric("Средняя GEO", f"{avg_geo_score:.1f}/100")
                
                show_enhanced_welcome_message()
                
                # Дополнительные возможности для авторизованных пользователей
                if st.session_state.user:
                    st.markdown("---")
                    st.subheader("Дополнительные возможности с AI")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("Управление профилем", width='stretch', key="profile_button_main"):
                            st.session_state.show_profile = True
                            st.rerun()
                    
                    with col2:
                        if st.button("Управление подпиской", width='stretch', key="subscription_button_main"):
                            st.session_state.show_subscription = True
                            st.rerun()

                    with col3:
                        if st.button("Сравнительный AI-анализ", width='stretch', key="comparison_button_main"):
                            st.session_state.show_comparison = True
                            st.rerun()
                    
                    with col4:
                        if st.button("Пример AI-отчета", width='stretch', key="sample_report_button_main"):
                            st.session_state.show_sample = True
                            st.rerun()
                else:
                    # Дополнительные кнопки для неавторизованных пользователей
                    st.markdown("---")
                    st.subheader("Дополнительные возможности")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Сравнительный анализ", width='stretch', key="comparison_button_guest"):
                            st.session_state.show_comparison = True
                            st.rerun()
                    
                    with col2:
                        if st.button("Пример отчета", width='stretch', key="sample_report_button_guest"):
                            st.session_state.show_sample = True
                            st.rerun()

if __name__ == "__main__":
    main()