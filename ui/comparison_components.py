"""
Компоненты для сравнительного анализа и трендов
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config import COLOR_SCHEME, TEXT_CONTENT

def display_comparison_analysis(history):
    """Отображение сравнительного анализа"""
    if len(history) < 2:
        st.info("Для сравнения необходимо как минимум 2 анализа")
        return
    
    st.markdown(f"## {TEXT_CONTENT['comparison_title']}")
    
    # Выбор анализов для сравнения
    col1, col2 = st.columns(2)
    with col1:
        analysis1_index = st.selectbox(
            "Первый анализ:",
            range(len(history)),
            format_func=lambda x: f"{history[x]['basic_info']['url']} - {history[x]['basic_info']['analysis_date']}"
        )
    with col2:
        analysis2_index = st.selectbox(
            "Второй анализ:",
            range(len(history)),
            index=min(1, len(history)-1),
            format_func=lambda x: f"{history[x]['basic_info']['url']} - {history[x]['basic_info']['analysis_date']}"
        )
    
    analysis1 = history[analysis1_index]
    analysis2 = history[analysis2_index]
    
    # Сравнительные метрики
    st.markdown("###Сравнение оценок")
    
    metrics = [
        ("Общая оценка", analysis1['score'], analysis2['score']),
        ("Производительность", analysis1['performance']['score'], analysis2['performance']['score']),
        ("Количество слов", analysis1['content_structure']['word_count'], analysis2['content_structure']['word_count']),
        ("Alt-тексты", analysis1['content_structure']['images']['alt_percentage'], analysis2['content_structure']['images']['alt_percentage']),
        ("Время загрузки", analysis1['basic_info']['response_time'], analysis2['basic_info']['response_time']),
    ]
    
    for name, val1, val2 in metrics:
        diff = val2 - val1
        trend_icon = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
        trend_color = COLOR_SCHEME['success'] if diff > 0 else COLOR_SCHEME['error'] if diff < 0 else COLOR_SCHEME['warning']
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric(f"{name} (1)", f"{val1:.1f}" if isinstance(val1, float) else val1)
        with col2:
            st.metric(f"{name} (2)", f"{val2:.1f}" if isinstance(val2, float) else val2)
        with col3:
            st.markdown(f"<div style='color: {trend_color}; font-size: 1.2rem;'>{trend_icon} {diff:+.1f}</div>", unsafe_allow_html=True)

def display_trends_analysis(history):
    """Отображение анализа трендов"""
    if len(history) < 3:
        st.info("Для анализа трендов необходимо как минимум 3 анализа")
        return
    
    st.markdown(f"## {TEXT_CONTENT['trends_title']}")
    
    # Подготовка данных для графиков
    dates = [datetime.strptime(item['basic_info']['analysis_date'], '%Y-%m-%d %H:%M:%S') for item in history]
    scores = [item['score'] for item in history]
    performance_scores = [item['performance']['score'] for item in history]
    word_counts = [item['content_structure']['word_count'] for item in history]
    
    # График изменения общей оценки
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Scatter(
        x=dates, y=scores,
        mode='lines+markers',
        name='Общая оценка',
        line=dict(color=COLOR_SCHEME['primary'], width=3)
    ))
    fig_scores.update_layout(
        title='Динамика общей оценки',
        xaxis_title='Дата анализа',
        yaxis_title='Оценка',
        template='plotly_white'
    )
    
    st.plotly_chart(fig_scores, width='stretch')
    
    # Сравнительные графики
    col1, col2 = st.columns(2)
    
    with col1:
        fig_performance = go.Figure()
        fig_performance.add_trace(go.Scatter(
            x=dates, y=performance_scores,
            mode='lines+markers',
            name='Производительность',
            line=dict(color=COLOR_SCHEME['success'], width=2)
        ))
        fig_performance.update_layout(
            title='Динамика производительности',
            xaxis_title='Дата анализа',
            yaxis_title='Оценка'
        )
        st.plotly_chart(fig_performance, width='stretch')
    
    with col2:
        fig_words = go.Figure()
        fig_words.add_trace(go.Scatter(
            x=dates, y=word_counts,
            mode='lines+markers',
            name='Количество слов',
            line=dict(color=COLOR_SCHEME['warning'], width=2)
        ))
        fig_words.update_layout(
            title='Динамика объема контента',
            xaxis_title='Дата анализа',
            yaxis_title='Количество слов'
        )
        st.plotly_chart(fig_words, width='stretch')

def display_improvement_recommendations(history):
    """Рекомендации по улучшению на основе истории"""
    if len(history) < 2:
        return
    
    current = history[-1]
    previous = history[-2]
    
    st.markdown("###Рекомендации на основе динамики")
    
    recommendations = []
    
    # Анализ изменений
    score_diff = current['score'] - previous['score']
    performance_diff = current['performance']['score'] - previous['performance']['score']
    content_diff = current['content_structure']['word_count'] - previous['content_structure']['word_count']
    
    if score_diff < 0:
        recommendations.append("Общая оценка снизилась. Проанализируйте изменения на сайте.")
    
    if performance_diff < -5:
        recommendations.append("Производительность значительно ухудшилась. Проверьте оптимизацию загрузки.")
    
    if content_diff < -50:
        recommendations.append("Объем контента уменьшился. Рассмотрите добавление нового качественного контента.")
    
    if current['content_structure']['images']['alt_percentage'] < 80:
        recommendations.append("Многие изображения все еще не имеют alt-текстов. Это важный фактор доступности.")
    
    if not recommendations:
        recommendations.append("Продолжайте текущую стратегию оптимизации. Все показатели стабильны или улучшаются.")
    
    for rec in recommendations:
        st.info(f"• {rec}")

def display_competitive_analysis(history):
    """Сравнительный анализ с лучшими практиками"""
    st.markdown("###Сравнение с лучшими практиками")
    
    if not history:
        return
    
    current = history[-1]
    
    best_practices = [
        ("Общая оценка > 80", current['score'] >= 80, 80),
        ("Title 50-60 символов", current['metadata']['title']['optimal'], 10),
        ("Description 120-160 символов", current['metadata']['description']['optimal'], 10),
        ("Время загрузки < 2с", current['basic_info']['response_time'] < 2, 15),
        ("Alt-тексты > 80%", current['content_structure']['images']['alt_percentage'] > 80, 10),
        ("HTTPS включен", current['basic_info']['is_https'], 5),
    ]
    
    achieved = sum(1 for _, condition, _ in best_practices if condition)
    total = len(best_practices)
    
    st.metric("Соответствие лучшим практикам", f"{achieved}/{total}")
    
    for practice, condition, weight in best_practices:
        status = "✅" if condition else "❌"
        st.write(f"{status} {practice}")