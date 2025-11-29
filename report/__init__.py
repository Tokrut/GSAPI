"""
Пакет генерации отчетов для GEO Analyzer Pro
"""

from .generators import (
    generate_full_report,
    generate_additional_recommendations,
    create_download_link,
    generate_docx_report,
    create_docx_download_link,
    generate_comparison_report,
    safe_get
)

from .formatters import (
    format_metadata_for_display,
    format_content_for_display,
    format_technical_for_display,
    format_performance_for_display,
    format_score_for_display,
    format_issues_for_display,
    create_analysis_summary
)

__all__ = [
    'generate_full_report',
    'generate_additional_recommendations',
    'create_download_link',
    'generate_docx_report',
    'create_docx_download_link',
    'generate_comparison_report',
    'safe_get',
    'format_metadata_for_display',
    'format_content_for_display',
    'format_technical_for_display',
    'format_performance_for_display',
    'format_score_for_display',
    'format_issues_for_display',
    'create_analysis_summary'
]