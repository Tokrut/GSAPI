import streamlit as st
from config import TEXT_CONTENT

def display_main_menu_button():
    """Отображение кнопки возврата в главное меню, которая всегда видна"""
    
    # Используем абсолютное позиционирование для фиксированного расположения
    st.markdown("""
    <style>
    .main-menu-button {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background-color: #ff6b6b;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 25px;
        cursor: pointer;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .main-menu-button:hover {
        background-color: #ff5252;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Создаем контейнер для кнопки
    button_container = st.container()
    
    with button_container:
        # Используем columns для позиционирования кнопки справа
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col3:
            if st.button(
                f"{TEXT_CONTENT.get('main_menu_button', 'Главное меню')}",
                key="fixed_main_menu_button",
                width='stretch',
                type="secondary"
            ):
                # Сбрасываем состояние приложения к главному меню
                st.session_state.current_analysis = None
                st.session_state.show_comparison = False
                st.session_state.show_profile = False
                st.session_state.show_stats = False
                st.session_state.show_sample = False
                st.rerun()