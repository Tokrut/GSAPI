"""
Пакет пользовательского интерфейса для GEO Analyzer Pro
"""

from .components import (
    display_enhanced_results,
    display_overview_tab,
    display_metadata,
    display_enhanced_content_structure,
    display_enhanced_technical_seo,
    display_performance_tab,
    display_enhanced_recommendations
)

from .layouts import (
    show_enhanced_welcome_message,
    show_main_tab,
    show_sample_report,
    show_history_tab,
    show_instructions_tab,
    show_comparison_tab,
    setup_sidebar
)

from .auth_components import (
    show_login_form,
    show_register_form,
    show_user_profile,
    show_auth_sidebar
)

from .sidebar_components import (
    display_enhanced_sidebar,
    display_user_profile_compact,
    display_quick_stats,
    display_analysis_insights,
    display_recent_activity,
    display_quick_actions,
    display_system_status,
    display_tips,
    display_calendar_insights
)

from .navigation_components import (
    display_main_menu_button
)

# Импортируем компоненты сравнения с обработкой ошибок
try:
    from .comparison_components import (
        display_comparison_analysis,
        display_trends_analysis,
        display_improvement_recommendations,
        display_competitive_analysis
    )
    COMPARISON_AVAILABLE = True
except ImportError as e:
    # Создаем заглушки если компоненты сравнения недоступны
    def display_comparison_analysis(*args, **kwargs):
        pass
    
    def display_trends_analysis(*args, **kwargs):
        pass
    
    def display_improvement_recommendations(*args, **kwargs):
        pass
    
    def display_competitive_analysis(*args, **kwargs):
        pass
    
    COMPARISON_AVAILABLE = False

__all__ = [
    'display_enhanced_results',
    'display_overview_tab',
    'display_metadata',
    'display_enhanced_content_structure',
    'display_enhanced_technical_seo',
    'display_performance_tab',
    'display_enhanced_recommendations',
    'show_enhanced_welcome_message',
    'show_main_tab',
    'show_sample_report',
    'show_history_tab',
    'show_instructions_tab',
    'show_comparison_tab',
    'setup_sidebar',
    'show_login_form',
    'show_register_form',
    'show_user_profile',
    'show_auth_sidebar',
    'display_enhanced_sidebar',
    'display_user_profile_compact',
    'display_quick_stats',
    'display_analysis_insights',
    'display_recent_activity',
    'display_quick_actions',
    'display_system_status',
    'display_tips',
    'display_calendar_insights',
    'display_comparison_analysis',
    'display_trends_analysis',
    'display_improvement_recommendations',
    'display_competitive_analysis',
    'display_main_menu_button',
    'COMPARISON_AVAILABLE'
]