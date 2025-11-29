"""
Компоненты для управления подписками
"""

import streamlit as st
from datetime import datetime, timedelta
from auth.service import AuthService
from config import TEXT_CONTENT, STATUS_MESSAGES, COLOR_SCHEME

def show_subscription_selection(auth_service: AuthService, username: str):
    """Отображение выбора подписки"""
    st.markdown("## Выбор подписки")
    
    # Получаем текущую информацию о подписке
    subscription_info = auth_service.get_user_subscription_info(username)
    
    # Отображаем текущую подписку
    st.markdown("### Текущая подписка")
    
    status_color = COLOR_SCHEME['success'] if subscription_info['status'] == 'active' else COLOR_SCHEME['error']
    
    st.markdown(f"""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 5px solid {status_color};">
        <h3 style="color: {status_color}; margin-top: 0;">{subscription_info['type'].upper()}</h3>
        <p><strong>Статус:</strong> <span style="color: {status_color}">{'Активна' if subscription_info['status'] == 'active' else 'Неактивна'}</span></p>
        <p><strong>Описание:</strong> {subscription_info['description']}</p>
        <p><strong>Осталось анализов:</strong> {'Неограниченно' if subscription_info['remaining_analyses'] == float('inf') else subscription_info['remaining_analyses']}</p>
        <p><strong>Глубокий анализ:</strong> {'✅ Доступен' if subscription_info['can_use_deep_analysis'] else '❌ Недоступен'}</p>
        {f"<p><strong>Действует до:</strong> {subscription_info['end_date'].strftime('%d.%m.%Y') if subscription_info['end_date'] else 'Бессрочно'}</p>" if subscription_info['end_date'] else ''}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Доступные подписки")
    
    # Создаем три колонки для подписок
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_free_subscription(auth_service, username, subscription_info)
    
    with col2:
        show_pro_subscription(auth_service, username, subscription_info)
    
    with col3:
        show_pro_plus_subscription(auth_service, username, subscription_info)

def show_free_subscription(auth_service: AuthService, username: str, current_subscription: dict):
    """Отображение бесплатной подписки"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; min-height: 400px;">
        <h3 style="color: white; margin-top: 0;">Бесплатный</h3>
        <h1 style="color: white; font-size: 3rem; margin: 1rem 0;">0 ₽</h1>
        <p style="font-size: 0.9rem;">навсегда</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <ul style="text-align: left; padding-left: 1rem;">
            <li>✅ 5 анализов всего</li>
            <li>✅ Базовый анализ сайтов</li>
            <li>❌ Глубокий анализ с конкурентами</li>
            <li>❌ Расширенная статистика</li>
            <li>❌ Приоритетная обработка</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if current_subscription['type'] == 'free':
        st.button("✅ Текущая подписка", disabled=True, key="current_free")
    else:
        if st.button("Выбрать бесплатный", key="select_free"):
            success, message = auth_service.upgrade_user_subscription(username, "free")
            if success:
                st.success("Переход на бесплатную подписку выполнен!")
                st.rerun()
            else:
                st.error(f"Ошибка: {message}")

def show_pro_subscription(auth_service: AuthService, username: str, current_subscription: dict):
    """Отображение Pro подписки"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; min-height: 400px; border: 3px solid #ff6b6b;">
        <h3 style="color: white; margin-top: 0;">Профессиональный</h3>
        <h1 style="color: white; font-size: 3rem; margin: 1rem 0;">999 ₽</h1>
        <p style="font-size: 0.9rem;">в месяц</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <ul style="text-align: left; padding-left: 1rem;">
            <li>✅ Неограниченное число анализов</li>
            <li>✅ Базовый анализ сайтов</li>
            <li>❌ Глубокий анализ с конкурентами</li>
            <li>✅ Расширенная статистика</li>
            <li>✅ Приоритетная обработка</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if current_subscription['type'] == 'pro':
        st.button("✅ Текущая подписка", disabled=True, key="current_pro")
    else:
        if st.button("Купить Pro за 999₽", key="buy_pro"):
            success, message = auth_service.upgrade_user_subscription(username, "pro", 30)
            if success:
                st.success("Pro подписка активирована на 30 дней!")
                st.rerun()
            else:
                st.error(f"Ошибка: {message}")

def show_pro_plus_subscription(auth_service: AuthService, username: str, current_subscription: dict):
    """Отображение Pro+ подписки"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffd93d 0%, #ff6b6b 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; min-height: 400px; border: 3px solid #ffd93d;">
        <h3 style="color: white; margin-top: 0;">Профессиональный+</h3>
        <h1 style="color: white; font-size: 3rem; margin: 1rem 0;">1999 ₽</h1>
        <p style="font-size: 0.9rem;">в месяц</p>
        <hr style="border-color: rgba(255,255,255,0.3);">
        <ul style="text-align: left; padding-left: 1rem;">
            <li>✅ Неограниченное число анализов</li>
            <li>✅ Базовый анализ сайтов</li>
            <li>✅ Глубокий анализ с конкурентами</li>
            <li>✅ Расширенная статистика</li>
            <li>✅ Приоритетная обработка</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if current_subscription['type'] == 'pro_plus':
        st.button("✅ Текущая подписка", disabled=True, key="current_pro_plus")
    else:
        if st.button("Купить Pro+ за 1999₽", key="buy_pro_plus"):
            success, message = auth_service.upgrade_user_subscription(username, "pro_plus", 30)
            if success:
                st.success("Pro+ подписка активирована на 30 дней!")
                st.rerun()
            else:
                st.error(f"Ошибка: {message}")

def show_subscription_sidebar(auth_service: AuthService):
    """Отображение информации о подписке в боковой панели"""
    if 'user' in st.session_state and st.session_state.user:
        user = st.session_state.user
        subscription_info = auth_service.get_user_subscription_info(user.username)
        
        st.markdown("### Подписка")
        
        status_color = COLOR_SCHEME['success'] if subscription_info['status'] == 'active' else COLOR_SCHEME['error']
        
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid {status_color};">
            <p style="margin: 0; font-weight: bold; color: {status_color};">{subscription_info['type'].upper()}</p>
            <p style="margin: 0.2rem 0; font-size: 0.8rem;">{'Активна' if subscription_info['status'] == 'active' else 'Неактивна'}</p>
            <p style="margin: 0.2rem 0; font-size: 0.8rem;">Анализов: {'∞' if subscription_info['remaining_analyses'] == float('inf') else subscription_info['remaining_analyses']}</p>
            {'<p style="margin: 0.2rem 0; font-size: 0.8rem;">До: ' + subscription_info['end_date'].strftime('%d.%m.%Y') + '</p>' if subscription_info['end_date'] else ''}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Управление подпиской", key="manage_subscription_sidebar"):
            st.session_state.show_subscription = True
            st.rerun()