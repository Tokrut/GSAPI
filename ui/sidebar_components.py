"""
Компоненты для улучшенной боковой панели GEO Analyzer Pro
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import COLOR_SCHEME, TEXT_CONTENT, STATUS_MESSAGES

def display_user_profile_compact(user):
    """Компактное отображение профиля пользователя"""
    if not user:
        return
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLOR_SCHEME['primary']}, {COLOR_SCHEME['secondary']}); 
                color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 2rem;">👤</div>
            <div>
                <h4 style="margin: 0; font-weight: bold;">{user.username}</h4>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.9;">{user.email}</p>
                <p style="margin: 0; font-size: 0.7rem; opacity: 0.7;">Анализов: {len(st.session_state.analysis_history)}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_quick_stats():
    """Быстрая статистика анализов"""
    if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
        st.info("История анализов пуста")
        return
    
    history = st.session_state.analysis_history
    total_analyses = len(history)
    avg_score = sum(item['score'] for item in history) / total_analyses
    best_score = max(item['score'] for item in history)
    
    # Анализы за последнюю неделю
    week_ago = datetime.now() - timedelta(days=7)
    recent_analyses = [
        item for item in history 
        if datetime.strptime(item['basic_info']['analysis_date'], '%Y-%m-%d %H:%M:%S') > week_ago
    ]
    
    st.markdown("### Быстрая статистика")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего анализов", total_analyses)
        st.metric("За неделю", len(recent_analyses))
    
    with col2:
        st.metric("Средний балл", f"{avg_score:.1f}")
        st.metric("Лучший", f"{best_score}")

def display_analysis_insights():
    """Инсайты и рекомендации на основе истории анализов"""
    if 'analysis_history' not in st.session_state or len(st.session_state.analysis_history) < 2:
        return
    
    history = st.session_state.analysis_history
    last_analysis = history[-1]
    previous_analysis = history[-2] if len(history) >= 2 else None
    
    if not previous_analysis:
        return
    
    st.markdown("### Инсайты")
    
    # Сравнение с предыдущим анализом
    score_diff = last_analysis['score'] - previous_analysis['score']
    if score_diff > 0:
        st.success(f"Улучшение на +{score_diff} баллов")
    elif score_diff < 0:
        st.error(f"Снижение на {score_diff} баллов")
    else:
        st.info("Без изменений")
    
    # Самые частые проблемы
    all_issues = []
    for analysis in history[-3:]:  # Последние 3 анализа
        all_issues.extend(analysis.get('critical_issues', []))
        all_issues.extend(analysis.get('warnings', []))
    
    if all_issues:
        from collections import Counter
        common_issues = Counter(all_issues).most_common(3)
        
        st.markdown("**Частые проблемы:**")
        for issue, count in common_issues:
            st.write(f"• {issue} ({count} раз)")

def display_recent_activity():
    """Недавняя активность"""
    if 'analysis_history' not in st.session_state or not st.session_state.analysis_history:
        return
    
    st.markdown("### Недавняя активность")
    
    # Последние 3 анализа
    recent = st.session_state.analysis_history[-3:]
    
    for i, analysis in enumerate(reversed(recent)):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                url_short = analysis['basic_info']['url'][:30] + "..." if len(analysis['basic_info']['url']) > 30 else analysis['basic_info']['url']
                st.write(f"**{url_short}**")
                
                # Дата анализа
                analysis_date = analysis['basic_info']['analysis_date']
                st.caption(f"{analysis_date}")
            
            with col2:
                score = analysis['score']
                color = COLOR_SCHEME['excellent'] if score >= 80 else COLOR_SCHEME['good'] if score >= 60 else COLOR_SCHEME['average'] if score >= 40 else COLOR_SCHEME['critical']
                st.markdown(f"<div style='color: {color}; font-weight: bold; text-align: center;'>{score}</div>", unsafe_allow_html=True)
            
            if i < len(recent) - 1:
                st.markdown("---")

def display_quick_actions():
    """Красивая панель быстрых действий с улучшенным дизайном"""
    
    # Заголовок панели с иконкой
    st.markdown("""
    <div class="quick-action-panel fade-in-up">
        <div class="quick-actions-title">⚡ Быстрые действия</div>
        <div class="action-grid">
    """, unsafe_allow_html=True)
    
    # Создаем контейнер для кнопок в сетке 2x2
    cols = st.columns(2)
    
    # Кнопка "Главное меню"
    with cols[0]:
        if st.button("🏠\nГлавное меню", key="main_menu_sidebar", help="Вернуться к главному экрану", use_container_width=True):
            st.session_state.current_analysis = None
            st.session_state.show_comparison = False
            st.session_state.show_profile = False
            st.session_state.show_stats = False
            st.session_state.show_sample = False
            st.rerun()
        
    # Кнопка "Новый анализ"
    with cols[1]:
        if st.button("🔍\nНовый анализ", key="new_analysis_sidebar", help="Запустить анализ нового сайта", use_container_width=True):
            st.session_state.current_analysis = None
            st.rerun()
    
    # Кнопка "Статистика"
    with cols[0]:
        if st.button("📊\nСтатистика", key="stats_sidebar", help="Посмотреть детальную статистику", use_container_width=True):
            st.session_state.show_stats = True
            st.rerun()

    # Кнопка "Пример отчета"
    with cols[1]:
        if st.button("📄\nПример отчета", key="sample_report_sidebar", help="Посмотреть пример анализа", use_container_width=True):
            st.session_state.show_sample = True
            st.rerun()

    # Закрываем сетку основных кнопок
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Добавляем разделитель
    st.markdown("---")
    
    # Кнопка "Очистить историю" (на всю ширину) с улучшенным стилем
    if st.button("🗑️\nОчистить историю анализов", key="clear_history_sidebar", help="Удалить всю историю анализов", use_container_width=True):
        # Создаем модальное окно подтверждения
        st.markdown("""
        <div class="confirmation-modal">
            <h4 style="color: #d32f2f; text-align: center; margin-bottom: 15px;">⚠️ Подтвердите действие</h4>
            <p style="text-align: center; margin-bottom: 20px;">Вы уверены, что хотите удалить всю историю анализов? Это действие нельзя отменить.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Да, очистить", key="confirm_clear_history", type="primary", use_container_width=True):
                try:
                    if st.session_state.user:
                        from auth.service import AuthService
                        auth_service = AuthService()
                        success = auth_service.clear_user_analysis_history(st.session_state.user.username)
                        if success:
                            st.session_state.analysis_history = []
                            st.success("✅ История очищена успешно!")
                        else:
                            st.error("❌ Ошибка при очистке истории")
                    else:
                        st.session_state.analysis_history = []
                        st.success("✅ История очищена успешно!")
                    
                    # Небольшая задержка для показа сообщения
                    import time
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Произошла ошибка: {str(e)}")
        
        with col2:
            if st.button("❌ Отменить", key="cancel_clear_history", use_container_width=True):
                st.rerun()
    
    # Закрываем панель
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Добавляем информационную подсказку
    with st.expander("💡 Подсказки по использованию", expanded=False):
        st.info("""
        **Полезные советы:**
        
        🏠 **Главное меню** - возврат к основному экрану анализа
        
        🔍 **Новый анализ** - быстрый запуск анализа другого сайта
        
        📊 **Статистика** - детальная аналитика ваших анализов
        
        📄 **Пример отчета** - посмотрите, как выглядит полный отчет
        
        🗑️ **Очистить историю** - удаление всех сохраненных анализов
        """)


def display_quick_actions_compact():
    """Компактная версия панели быстрых действий для мобильных устройств"""
    
    st.markdown("### ⚡ Действия")
    
    # Горизонтальная компоновка кнопок
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Главное", key="main_menu_compact"):
            st.session_state.current_analysis = None
            st.session_state.show_comparison = False
            st.session_state.show_profile = False
            st.session_state.show_stats = False
            st.session_state.show_sample = False
            st.rerun()
        
        if st.button("📊 Статистика", key="stats_compact"):
            st.session_state.show_stats = True
            st.rerun()
    
    with col2:
        if st.button("🔍 Новый", key="new_analysis_compact"):
            st.session_state.current_analysis = None
            st.rerun()
        
        if st.button("📄 Пример", key="sample_compact"):
            st.session_state.show_sample = True
            st.rerun()
    
    # Кнопка очистки в отдельной строке
    if st.button("🗑️ Очистить историю", key="clear_compact", type="secondary"):
        if st.session_state.user:
            from auth.service import AuthService
            auth_service = AuthService()
            success = auth_service.clear_user_analysis_history(st.session_state.user.username)
            if success:
                st.session_state.analysis_history = []
                st.success("История очищена!")
                st.rerun()
            else:
                st.error("Ошибка при очистке истории")
        else:
            st.session_state.analysis_history = []
            st.success("История очищена!")
            st.rerun()

def display_system_status(login_time):
    """Статус системы и время в системе"""
    st.markdown("### Статус системы")
    
    # Время в системе
    if login_time:
        current_time = datetime.now()
        session_duration = current_time - login_time
        
        # Форматируем время в читаемый вид
        hours = int(session_duration.total_seconds() // 3600)
        minutes = int((session_duration.total_seconds() % 3600) // 60)
        seconds = int(session_duration.total_seconds() % 60)
        
        if hours > 0:
            time_str = f"{hours} ч {minutes} м {seconds} с"
        elif minutes > 0:
            time_str = f"{minutes} м {seconds} с"
        else:
            time_str = f"{seconds} с"
        
        st.write(f"**Время в системе:** {time_str}")
        
        # Прогресс-бар сессии (максимум 24 часа)
        session_progress = min(session_duration.total_seconds() / (24 * 3600) * 100, 100)
        st.progress(session_progress / 100, text=f"Сессия: {session_progress:.1f}%")
    
    # Информация о системе
    try:
        import psutil
        memory = psutil.virtual_memory()
        st.write(f"**Память:** {memory.percent}% использовано")
        
        # Загрузка CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        st.write(f"**Загрузка CPU:** {cpu_percent}%")
        
    except ImportError:
        st.write("**Память:** Информация недоступна")
        st.write("**Загрузка CPU:** Информация недоступна")
    
    # Статус анализатора
    st.success("Анализатор активен")
    
    # Статус сохранения истории
    if st.session_state.user:
        st.success("История сохраняется")
    else:
        st.warning("История временная")

def display_tips():
    """Полезные советы"""
    tips = [
        "Регулярно проверяйте ключевые страницы сайта",
        "Анализируйте сайты конкурентов для сравнения",
        "Отслеживайте динамику изменений во времени",
        "Обращайте внимание на производительность",
        "Исправляйте критические проблемы в первую очередь",
        "Фокусируйтесь на пользовательском опыте",
        "Сохраняйте историю для отслеживания прогресса",
        "Используйте рекомендации для улучшения SEO"
    ]
    
    st.markdown("### Советы")
    
    import random
    tip = random.choice(tips)
    st.info(tip)

def display_calendar_insights():
    """Календарные инсайты и напоминания"""
    today = datetime.now()
    
    st.markdown("### Календарь")
    
    # Ближайшие действия
    st.write("**Сегодня:**")
    st.write(f"• {today.strftime('%d %B %Y')}")
    
    # Рекомендации по расписанию
    if today.weekday() == 0:  # Понедельник
        st.info("Отличный день для планового аудита!")
    elif today.weekday() == 4:  # Пятница
        st.info("Подведите итоги недели")

def display_enhanced_sidebar(user, login_time=None):
    """Улучшенная боковая панель"""
    
    # Профиль пользователя
    if user:
        display_user_profile_compact(user)
    
    # Быстрая статистика
    display_quick_stats()
    
    # Разделитель
    st.markdown("---")
    
    # Быстрые действия
    display_quick_actions()
    
    # Разделитель
    st.markdown("---")
    
    # Инсайты и рекомендации
    display_analysis_insights()
    
    # Недавняя активность
    display_recent_activity()
    
    # Разделитель
    st.markdown("---")
    
    # Календарь и напоминания
    display_calendar_insights()
    
    # Советы
    display_tips()
    
    # Статус системы с реальным временем сессии
    display_system_status(login_time)
    
    # Футер
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "GEO Analyzer Pro v2.0<br>"
        "© 2025 Все права защищены"
        "</div>",
        unsafe_allow_html=True
    )