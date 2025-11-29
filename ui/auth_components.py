"""
Компоненты пользовательского интерфейса для аутентификации
"""

import streamlit as st
from datetime import datetime
from auth.service import AuthService
from config import TEXT_CONTENT, STATUS_MESSAGES

def show_login_form(auth_service: AuthService):
    """Отображение формы входа"""
    st.markdown(f"## {TEXT_CONTENT['login_title']}")
    
    with st.form("login_form"):
        username = st.text_input("Имя пользователя", placeholder="Введите ваше имя пользователя")
        password = st.text_input("Пароль", type="password", placeholder="Введите ваш пароль")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_submit = st.form_submit_button("Войти", width='stretch', key="login_submit")
        with col2:
            register_redirect = st.form_submit_button("Создать аккаунт", width='stretch', key="register_redirect")
        
        if login_submit:
            if not username or not password:
                st.error("Пожалуйста, заполните все поля")
                return False
            
            success, message, user = auth_service.authenticate_user(username, password)
            if success:
                st.session_state.user = user
                st.session_state.login_time = datetime.now()
                
                # Загружаем историю анализов пользователя
                from app import load_user_history
                load_user_history(auth_service, username)
                
                st.success(STATUS_MESSAGES['login_success'])
                st.rerun()
            else:
                st.error(f"{STATUS_MESSAGES['login_failed']} {message}")
        
        if register_redirect:
            st.session_state.show_register = True
            st.rerun()
    
    return False

def show_register_form(auth_service: AuthService):
    """Отображение формы регистрации"""
    st.markdown(f"## {TEXT_CONTENT['register_title']}")
    
    with st.form("register_form"):
        username = st.text_input("Имя пользователя", placeholder="Придумайте имя пользователя")
        email = st.text_input("Email", placeholder="Введите ваш email")
        password = st.text_input("Пароль", type="password", placeholder="Придумайте пароль")
        confirm_password = st.text_input("Подтверждение пароля", type="password", placeholder="Повторите пароль")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            register_submit = st.form_submit_button("Зарегистрироваться", width='stretch', key="register_submit")
        with col2:
            login_redirect = st.form_submit_button("Уже есть аккаунт", width='stretch', key="login_redirect")
        
        if register_submit:
            if not all([username, email, password, confirm_password]):
                st.error("Пожалуйста, заполните все поля")
                return False
            
            if password != confirm_password:
                st.error("Пароли не совпадают")
                return False
            
            success, message = auth_service.register_user(username, email, password)
            if success:
                st.success(STATUS_MESSAGES['register_success'])
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error(f"{STATUS_MESSAGES['register_failed']} {message}")
        
        if login_redirect:
            st.session_state.show_register = False
            st.rerun()
    
    return False

def show_user_profile(auth_service: AuthService):
    """Отображение профиля пользователя"""
    st.markdown(f"## {TEXT_CONTENT['profile_title']}")
    
    user = st.session_state.user
    if not user:
        return
    
    # Информация о пользователе
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Время в системе
        if 'login_time' in st.session_state:
            current_time = datetime.now()
            session_duration = current_time - st.session_state.login_time
            hours = int(session_duration.total_seconds() // 3600)
            minutes = int((session_duration.total_seconds() % 3600) // 60)
            time_in_system = f"{hours} ч {minutes} м"
        else:
            time_in_system = "Неизвестно"
        
        st.markdown(f"""
        <div class="user-profile">
            <h3> {user.username}</h3>
            <p><strong> Email:</strong> {user.email}</p>
            <p><strong> Зарегистрирован:</strong> {user.created_at.strftime('%d.%m.%Y %H:%M')}</p>
            <p><strong> В системе:</strong> {time_in_system}</p>
            <p><strong> Сохраненных анализов:</strong> {len(st.session_state.analysis_history)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            if st.button("Управление подпиской", width='stretch', key="manage_subscription"):
                st.session_state.show_subscription = True
                st.rerun()
        with col2_2:
            if st.button(" Выйти", width='stretch', key="logout_button"):
                # Сохраняем текущую историю перед выходом
                if st.session_state.user and st.session_state.analysis_history:
                    try:
                        # Обновляем историю в базе данных
                        auth_service.clear_user_analysis_history(st.session_state.user.username)
                        for analysis in st.session_state.analysis_history:
                            auth_service.save_user_analysis(st.session_state.user.username, analysis)
                    except Exception as e:
                        st.error(f"Ошибка сохранения истории: {e}")
                
                st.session_state.pop('user', None)
                st.session_state.pop('login_time', None)
                st.session_state.analysis_history = []
                st.success(STATUS_MESSAGES['logout_success'])
                st.rerun()
            
    # Управление историей
    st.markdown("---")
    st.subheader("Управление историей анализов")
    
    col_clear, col_export = st.columns(2)
    
    with col_clear:
        if st.button("Очистить историю", width='stretch', key="clear_history_profile"):
            if st.session_state.user:
                success = auth_service.clear_user_analysis_history(st.session_state.user.username)
                if success:
                    st.session_state.analysis_history = []
                    st.success("История анализов очищена!")
                    st.rerun()
                else:
                    st.error("Ошибка при очистке истории")
    
    with col_export:
        if st.button("Экспорт истории", width='stretch', key="export_history"):
            st.info("Функция экспорта в разработке")
    
    # Смена пароля
    st.markdown("---")
    st.subheader("Смена пароля")
    
    with st.form("change_password_form"):
        current_password = st.text_input("Текущий пароль", type="password")
        new_password = st.text_input("Новый пароль", type="password")
        confirm_new_password = st.text_input("Подтверждение нового пароля", type="password")
        
        change_submit = st.form_submit_button("Сменить пароль", width='stretch', key="change_password_submit")
        
        if change_submit:
            if not all([current_password, new_password, confirm_new_password]):
                st.error("Пожалуйста, заполните все поля")
            elif new_password != confirm_new_password:
                st.error("Новые пароли не совпадают")
            else:
                success, message = auth_service.change_password(user.username, current_password, new_password)
                if success:
                    st.success("Пароль успешно изменен")
                else:
                    st.error(f"{message}")

def show_auth_sidebar(auth_service: AuthService):
    """Отображение аутентификации в боковой панели"""
    with st.sidebar:
        if 'user' in st.session_state and st.session_state.user:
            # Пользователь авторизован
            user = st.session_state.user
            
            # Время сессии
            if 'login_time' in st.session_state:
                session_duration = datetime.now() - st.session_state.login_time
                hours = int(session_duration.total_seconds() // 3600)
                minutes = int((session_duration.total_seconds() % 3600) // 60)
                session_time = f"{hours}ч {minutes}м"
            else:
                session_time = "Неизвестно"
            
            st.markdown(f"### {user.username}")
            st.markdown(f"*{user.email}*")
            st.caption(f"В системе: {session_time}")
            st.caption(f"Анализов: {len(st.session_state.analysis_history)}")
            
            # Кнопка возврата в главное меню
            if st.button("Главное меню", width='stretch', key="main_menu_sidebar"):
                # Сбрасываем состояние приложения к главному меню
                st.session_state.current_analysis = None
                st.session_state.show_comparison = False
                st.session_state.show_profile = False
                st.session_state.show_stats = False
                st.session_state.show_sample = False
                st.rerun()
            
            if st.button("Выйти", width='stretch', key="logout_sidebar"):
                # Сохраняем историю перед выходом
                if st.session_state.analysis_history:
                    try:
                        auth_service.clear_user_analysis_history(user.username)
                        for analysis in st.session_state.analysis_history:
                            auth_service.save_user_analysis(user.username, analysis)
                    except Exception as e:
                        st.error(f"Ошибка сохранения истории: {e}")
                
                st.session_state.pop('user', None)
                st.session_state.pop('login_time', None)
                st.session_state.analysis_history = []
                st.success(STATUS_MESSAGES['logout_success'])
                st.rerun()
            
            st.markdown("---")
            
        else:
            # Пользователь не авторизован
            st.markdown("### Аутентификация")
            
            auth_option = st.radio(
                "Выберите действие:",
                ["Вход", "Регистрация"],
                horizontal=True,
                key="auth_option_sidebar"
            )
            
            with st.form("sidebar_auth_form"):
                if auth_option == "Вход":
                    username = st.text_input("Имя пользователя", key="username_sidebar")
                    password = st.text_input("Пароль", type="password", key="password_sidebar")
                    
                    if st.form_submit_button("Войти", width='stretch', key="login_sidebar"):
                        if username and password:
                            success, message, user = auth_service.authenticate_user(username, password)
                            if success:
                                st.session_state.user = user
                                st.session_state.login_time = datetime.now()
                                
                                # Загружаем историю анализов
                                from app import load_user_history
                                load_user_history(auth_service, username)
                                
                                st.success(STATUS_MESSAGES['login_success'])
                                st.rerun()
                            else:
                                st.error(f"{STATUS_MESSAGES['login_failed']} {message}")
                
                else:  # Регистрация
                    username = st.text_input("Имя пользователя", key="username_register_sidebar")
                    email = st.text_input("Email", key="email_sidebar")
                    password = st.text_input("Пароль", type="password", key="password_register_sidebar")
                    
                    if st.form_submit_button("Зарегистрироваться", width='stretch', key="register_sidebar"):
                        if username and email and password:
                            success, message = auth_service.register_user(username, email, password)
                            if success:
                                st.success(STATUS_MESSAGES['register_success'])
                                st.rerun()
                            else:
                                st.error(f"{STATUS_MESSAGES['register_failed']} {message}")