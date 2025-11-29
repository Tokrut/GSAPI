import streamlit as st
import pandas as pd
from report.generators import generate_full_report, create_download_link, generate_docx_report, create_docx_download_link
from config import COLOR_SCHEME, TEXT_CONTENT

def display_enhanced_results(result):
    """Улучшенное отображение результатов анализа с LLM и глубоким анализом"""
    
    # Проверяем, есть ли глубокий анализ с конкурентами
    has_deep_analysis = 'deep_analysis' in result and result['deep_analysis'] and 'error' not in result['deep_analysis']
    
    # Верхняя панель с ключевыми метриками
    st.markdown("---")
    
    # Добавляем кнопку скачивания отчета в верхнюю часть
    col_download, col_space, col1, col2, col3, col4 = st.columns([2, 1, 1, 1, 1, 1])
    
    with col_download:
        # Скачивание отчета в формате DOCX (текстовые отчеты отключены)
        docx_report = generate_docx_report(result)
        if docx_report:
            st.markdown(create_docx_download_link(docx_report, f"geo_report_{result['basic_info']['analysis_date'].replace(' ', '_').replace(':', '')}.docx"), 
                       unsafe_allow_html=True)
        else:
            st.info("Отчет в формате DOCX временно недоступен")
    
    with col1:
        st.metric("Общая оценка", f"{result['score']}/100")
    
    with col2:
        # GEO оценка от LLM
        llm_score = result.get('llm_analysis', {}).get('overall_geo_score', 0)
        st.metric("GEO оценка (AI)", f"{llm_score}/100")
    
    with col3:
        if has_deep_analysis:
            deep_analysis = result['deep_analysis']
            ranking = deep_analysis.get('target_ranking', {})
            position = ranking.get('position', 'N/A')
            st.metric("Позиция среди конкурентов", f"{position}")
        else:
            st.metric("Производительность", f"{result['performance']['score']}/100")
    
    with col4:
        st.metric("Время загрузки", f"{result['basic_info']['response_time']}с")
    
    # Остальные колонки
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Размер страницы", f"{result['performance']['page_size'] // 1024} KB")
    with col6:
        status = "Хорошо" if result['score'] >= 70 else "Средне" if result['score'] >= 40 else "Требует улучшений"
        st.metric("Статус", status)
    
    # Прогресс-бар с цветовой индикацией
    progress_value = result['score'] / 100
    st.progress(progress_value, text=f"Общий показатель качества: {result['score']}%")
    
    # GEO прогресс-бар от LLM
    llm_progress = llm_score / 100
    st.progress(llm_progress, text=f"GEO оптимизация (AI): {llm_score}%")
    
    # Индикатор конкурентной позиции
    if has_deep_analysis:
        deep_analysis = result['deep_analysis']
        ranking = deep_analysis.get('target_ranking', {})
        position = ranking.get('position', 'N/A')
        total_sites = ranking.get('total_sites', 0)
        percentile = ranking.get('percentile', 0)
        
        if position != 'N/A' and total_sites > 0:
            position_progress = (total_sites - position + 1) / total_sites
            st.progress(position_progress, text=f"Конкурентная позиция: {position} из {total_sites} ({percentile:.1f}% перцентиль)")
    
    # Критические проблемы и предупреждения
    if result['critical_issues'] or result['warnings']:
        st.markdown("---")
        col_crit, col_warn = st.columns(2)
        
        with col_crit:
            if result['critical_issues']:
                st.error("### Критические проблемы")
                for issue in result['critical_issues']:
                    st.write(f"• {issue}")
        
        with col_warn:
            if result['warnings']:
                st.warning("### Предупреждения")
                for warning in result['warnings']:
                    st.write(f"• {warning}")
    
    # Вкладки для детального анализа
    st.markdown("---")
    tab_names = ["Обзор", "AI Анализ", "Мета-данные", "Структура", "Техника", "Рекомендации"]
    
    # Добавляем вкладку для глубокого анализа если есть данные
    if has_deep_analysis:
        tab_names.append("Сравнение с конкурентами")
    
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        display_overview_tab(result)
    with tabs[1]:
        display_llm_analysis_tab(result)
    with tabs[2]:
        display_metadata(result['metadata'])
    with tabs[3]:
        display_enhanced_content_structure(result['content_structure'])
    with tabs[4]:
        display_enhanced_technical_seo(result['technical_seo'])
    with tabs[5]:
        display_enhanced_recommendations(result)
    
    # Вкладка сравнения с конкурентами
    if has_deep_analysis:
        with tabs[-1]:
            display_deep_comparison_tab(result['deep_analysis'])

def display_llm_analysis_tab(result):
    """Вкладка с LLM-анализом для GEO с развернутыми ответами"""
    llm_analysis = result.get('llm_analysis', {})
    
    if not llm_analysis or 'error' in llm_analysis:
        st.warning("LLM-анализ временно недоступен")
        return
    
    st.subheader("AI-Анализ для генеративного поиска")
    
    # Основные метрики GEO
    col1, col2, col3 = st.columns(3)
    
    with col1:
        geo_score = llm_analysis.get('overall_geo_score', 0)
        st.metric("Общая GEO оценка", f"{geo_score}/100")
    
    with col2:
        citation_potential = llm_analysis.get('citation_potential', 0)
        st.metric("Потенциал цитирования", f"{citation_potential}/100")
    
    with col3:
        analysis_summary = llm_analysis.get('analysis_summary', 'Нет сводки')
        st.metric("Статус анализа", "Завершен")
    
    # Сводка анализа
    if analysis_summary:
        st.info(f"**Сводка:** {analysis_summary}")
    
    # Детальные анализы от каждой модели
    detailed_analysis = llm_analysis.get('detailed_analysis', {})
    
    for model_name, analysis_text in detailed_analysis.items():
        if analysis_text and len(analysis_text.strip()) > 100:
            with st.expander(f"Полный анализ от {model_name.upper()}", expanded=False):
                st.text_area(
                    f"Анализ {model_name}",
                    analysis_text,
                    height=300,
                    label_visibility="collapsed"
                )
    
    # Инсайты от моделей
    st.subheader("Ключевые инсайты")
    insights = llm_analysis.get('llm_insights', [])
    
    if insights:
        for insight in insights:
            # Обрезаем слишком длинные инсайты
            display_insight = insight[:500] + "..." if len(insight) > 500 else insight
            st.info(display_insight)
    else:
        st.write("Ключевые инсайты не сгенерированы")

    """Вкладка с LLM-анализом для GEO"""
    llm_analysis = result.get('llm_analysis', {})
    
    if not llm_analysis or 'error' in llm_analysis:
        st.warning("LLM-анализ временно недоступен")
        return
    
    st.subheader("AI-Анализ для генеративного поиска")
    
    # Основные метрики GEO
    col1, col2, col3 = st.columns(3)
    
    with col1:
        geo_score = llm_analysis.get('overall_geo_score', 0)
        st.metric("Общая GEO оценка", f"{geo_score}/100")
    
    with col2:
        citation_potential = llm_analysis.get('citation_potential', 0)
        st.metric("Потенциал цитирования", f"{citation_potential}/100")
    
    with col3:
        clear_answer_quality = llm_analysis.get('clear_answer_quality', 0)
        st.metric("Качество clear answers", f"{clear_answer_quality}/100")
    
    # Использованные модели
    st.subheader("Использованные AI-модели")
    models_used = llm_analysis.get('models_used', [])
    
    for model in models_used:
        model_display = {
            'bert_nebulon': 'Bert-Nebulon Alpha',
            'grok': 'Grok 4.1 Fast', 
            'deepseek': 'DeepSeek R1T2 Chimera'
        }.get(model, model)
        
        st.write(f"• {model_display}")
    
    # Инсайты от моделей
    st.subheader("Инсайты от AI-моделей")
    insights = llm_analysis.get('llm_insights', [])
    
    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.write("Инсайты не сгенерированы")
    
    # Детальные результаты по моделям
    st.subheader("Детальный анализ по моделям")
    llm_findings = llm_analysis.get('llm_specific_findings', {})
    
    for model_name, findings in llm_findings.items():
        with st.expander(f"{model_name.upper()} Analysis", expanded=False):
            if isinstance(findings, dict):
                for key, value in findings.items():
                    if key not in ['error']:
                        if isinstance(value, list):
                            st.write(f"**{key}:**")
                            for item in value:
                                st.write(f"• {item}")
                        else:
                            st.write(f"**{key}:** {value}")
            else:
                st.write(findings)
                        
def display_overview_tab(result):
    """Вкладка с общим обзором"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Быстрый обзор")
        
        # Мини-метрики
        metrics_data = [
            ["Title", "✅" if result['metadata']['title']['value'] else "❌"],
            ["Description", "✅" if result['metadata']['description']['value'] else "❌"],
            ["H1", f"✅ {result['semantic_markup']['heading_hierarchy']['h1_count']}"],
            ["Schema.org", "✅" if result['semantic_markup']['schema_org']['exists'] else "❌"],
            ["Canonical", "✅" if result['metadata']['canonical']['exists'] else "❌"],
            ["Alt тексты", f"{result['content_structure']['images']['alt_percentage']}%"]
        ]
        
        for label, value in metrics_data:
            st.write(f"**{label}:** {value}")
    
    with col2:
        st.subheader("Ключевые показатели")
        
        # Простая визуализация прогресс-барами
        categories = ['Мета-данные', 'Семантика', 'Контент', 'Техника', 'Производительность']
        scores = [
            min(20, result['score']), 
            min(20, result['score']), 
            min(20, result['score']),
            min(20, result['score']),
            result['performance']['score'] / 5
        ]
        
        for category, score in zip(categories, scores):
            st.write(f"**{category}**")
            st.progress(score / 20)

def display_metadata(metadata):
    """Отображение мета-данных"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Основные мета-теги")
        
        # Title
        st.write("**Title:**")
        if metadata['title']['value']:
            status = "Оптимально" if metadata['title']['optimal'] else "Требует оптимизации"
            st.write(f"{status} ({metadata['title']['length']} символов)")
            st.code(metadata['title']['value'])
        else:
            st.error("Отсутствует")
        
        # Description
        st.write("**Description:**")
        if metadata['description']['value']:
            status = "Оптимально" if metadata['description']['optimal'] else "Требует оптимизации"
            st.write(f"{status} ({metadata['description']['length']} символов)")
            st.code(metadata['description']['value'])
        else:
            st.warning("Отсутствует")
    
    with col2:
        st.subheader("🔧 Технические мета-теги")
        
        tech_meta = [
            ["Canonical", metadata['canonical']['exists'], metadata['canonical']['value']],
            ["Robots", metadata['robots']['exists'], metadata['robots']['value']],
            ["Viewport", metadata['viewport']['exists'], metadata['viewport']['value']],
            ["Charset", metadata['charset']['exists'], metadata['charset']['value']]
        ]
        
        for name, exists, value in tech_meta:
            status = "✅" if exists else "❌"
            st.write(f"**{name}:** {status}")
            if value:
                st.code(str(value))

def display_enhanced_content_structure(content):
    """Улучшенное отображение структуры контента"""
    st.subheader("Статистика контента")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Слов в тексте", content['word_count'])
        st.metric("Уникальных слов", content.get('keyword_analysis', {}).get('unique_words', 0))
    
    with col2:
        st.metric("Списки", content['lists']['total'])
        st.metric("Таблицы", content['tables'])
    
    with col3:
        st.metric("Изображения", content['images']['total'])
        st.metric("Alt-тексты", f"{content['images']['alt_percentage']}%")
    
    with col4:
        st.metric("Соотношение текст/HTML", f"{content['text_ratio']}%")
        if 'readability' in content:
            st.metric("Читаемость", f"{content['readability']['score']}/100")
    
    # Анализ читаемости
    if 'readability' in content:
        st.subheader("Анализ читаемости")
        col_read1, col_read2 = st.columns(2)
        
        with col_read1:
            st.write(f"**Средняя длина предложения:** {content['readability']['avg_sentence_length']} слов")
            st.write(f"**Средняя длина слова:** {content['readability']['avg_word_length']} символов")
        
        with col_read2:
            st.write(f"**Всего слов:** {content['readability']['words']}")
            st.write(f"**Всего предложений:** {content['readability']['sentences']}")
    
    # Ключевые слова
    if 'keyword_analysis' in content and content['keyword_analysis']['top_words']:
        st.subheader("Ключевые слова (топ-10)")
        
        keywords_df = pd.DataFrame(content['keyword_analysis']['top_words'], columns=['Слово', 'Частота'])
        st.dataframe(keywords_df, width='stretch')

def display_enhanced_technical_seo(technical):
    """Улучшенное отображение технического SEO"""
    st.subheader("Анализ ссылок")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Основные метрики:**")
        basic_links = [
            ["Всего ссылок", technical['links']['total']],
            ["Внутренние", technical['links']['internal']],
            ["Внешние", technical['links']['external']],
            ["С анкорами", technical['links']['with_anchor']]
        ]
        
        for label, value in basic_links:
            st.write(f"• {label}: **{value}**")
    
    with col2:
        st.write("**Детальный анализ:**")
        enhanced_links = [
            ["Nofollow ссылки", technical['enhanced_links']['nofollow']],
            ["Пустые анкоры", technical['enhanced_links']['empty_anchor']],
            ["С анкор-текстом", technical['enhanced_links']['with_anchor']]
        ]
        
        for label, value in enhanced_links:
            st.write(f"• {label}: **{value}**")
    
    # Технические теги
    st.subheader("Технические теги")
    tech_tags = technical['important_tags']
    
    col_tech1, col_tech2, col_tech3, col_tech4 = st.columns(4)
    
    with col_tech1:
        st.metric("Canonical", "✅" if tech_tags['canonical'] else "❌")
    with col_tech2:
        st.metric("Robots.txt", "✅" if tech_tags['robots_txt'] else "❌")
    with col_tech3:
        st.metric("Sitemap.xml", "✅" if tech_tags['sitemap'] else "❌")
    with col_tech4:
        st.metric("Favicon", "✅" if tech_tags['favicon'] else "❌")

def display_performance_tab(performance):
    """Отображение вкладки производительности"""
    st.subheader("Производительность сайта")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Оценка производительности", f"{performance['score']}/100")
        st.metric("Время загрузки", f"{performance['response_time']:.2f}с")
    
    with col2:
        st.metric("Размер страницы", f"{performance['page_size'] // 1024} KB")
        st.metric("Размер HTML", f"{performance['html_size'] // 1024} KB")
    
    with col3:
        st.metric("Изображения", performance['image_count'])
        st.metric("Скрипты", performance['script_count'])
    
    # Рекомендации по производительности
    st.subheader("Рекомендации по производительности")
    
    if performance['response_time'] > 3:
        st.error("• **Время загрузки слишком велико** (> 3 сек) - оптимизируйте сервер и контент")
    elif performance['response_time'] > 1:
        st.warning("• **Время загрузки можно улучшить** (> 1 сек) - рассмотрите оптимизацию")
    else:
        st.success("• **Время загрузки отличное** (< 1 сек)")
    
    if performance['page_size'] > 2 * 1024 * 1024:
        st.error("• **Размер страницы слишком большой** (> 2MB) - оптимизируйте изображения")
    elif performance['page_size'] > 1 * 1024 * 1024:
        st.warning("• **Размер страницы можно уменьшить** (> 1MB) - сожмите ресурсы")
    else:
        st.success("• **Размер страницы оптимальный** (< 1MB)")
    
    if performance['image_count'] > 20:
        st.warning("• **Много изображений** - рассмотрите ленивую загрузку")
    
    if performance['script_count'] > 10:
        st.warning("• **Много скриптов** - объедините и минифицируйте JavaScript")

def display_enhanced_recommendations(result):
    """Улучшенное отображение рекомендаций с примерами"""
    from report.generators import generate_additional_recommendations
    
    st.subheader("Критические проблемы")
    if result['critical_issues']:
        for issue in result['critical_issues']:
            st.error(f"• {issue}")
    else:
        st.success("• Критические проблемы отсутствуют")
    
    st.subheader("Предупреждения") 
    if result['warnings']:
        for warning in result['warnings']:
            st.warning(f"• {warning}")
    else:
        st.success("• Предупреждения отсутствуют")
    
    st.subheader("Рекомендации по улучшению")
    if result['recommendations']:
        # Группируем рекомендации по типам
        recommendations_by_type = {}
        for rec in result['recommendations']:
            rec_type = rec.get('type', 'other')
            if rec_type not in recommendations_by_type:
                recommendations_by_type[rec_type] = []
            recommendations_by_type[rec_type].append(rec)
        
        # Отображаем рекомендации по категориям
        type_labels = {
            'metadata': 'Мета-данные',
            'content': 'Контент', 
            'semantic': 'Семантика',
            'technical': 'Техническое SEO',
            'performance': 'Производительность',
            'security': 'Безопасность',
            'other': 'Общие'
        }
        
        for rec_type, recs in recommendations_by_type.items():
            label = type_labels.get(rec_type, '💡 Общие')
            st.markdown(f"**{label}**")
            for rec in recs:
                display_recommendation_with_examples(rec)
            st.markdown("---")
    else:
        st.success("• Все рекомендации выполнены!")
    
    # GEO-рекомендации от LLM
    llm_analysis = result.get('llm_analysis', {})
    geo_recommendations = llm_analysis.get('geo_recommendations', [])
    
    if geo_recommendations:
        st.subheader("GEO-рекомендации от AI")
        for rec in geo_recommendations:
            st.info(f"• {rec}")
    
    # Дополнительные рекомендации
    st.subheader("Дополнительные улучшения")
    additional_recs = generate_additional_recommendations(result)
    if additional_recs:
        st.info(additional_recs)
# [file name]: ui/components.py (дополнение)
def display_deep_comparison_tab(deep_analysis):
    """Расширенное отображение вкладки сравнения с конкурентами"""
    
    st.markdown("## Комплексный конкурентный анализ")
    
    # Исполнительное резюме
    if 'executive_summary' in deep_analysis:
        display_executive_summary(deep_analysis['executive_summary'])
    
    st.markdown("---")
    
    # Основные метрики и позиционирование
    display_positioning_analysis(deep_analysis)
    
    st.markdown("---")
    
    # Детальный анализ конкурентной позиции
    display_competitive_analysis(deep_analysis)
    
    st.markdown("---")
    
    # Матрица сравнения и метрики
    display_comparison_matrix(deep_analysis)
    
    st.markdown("---")
    
    # План улучшений
    display_improvement_plan(deep_analysis)
    
    st.markdown("---")
    
    # Комплексная сводка
    if 'comprehensive_summary' in deep_analysis:
        display_comprehensive_summary(deep_analysis['comprehensive_summary'])

def display_executive_summary(executive_summary):
    """Отображение исполнительного резюме"""
    st.subheader("Исполнительное резюме")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'overview' in executive_summary:
            st.info("**Обзор:**")
            st.write(executive_summary['overview'])
        
        if 'competitive_position' in executive_summary:
            st.success("**Конкурентная позиция:**")
            st.write(executive_summary['competitive_position'])
    
    with col2:
        if 'key_recommendations' in executive_summary:
            st.warning("**Ключевые рекомендации:**")
            for rec in executive_summary['key_recommendations']:
                st.write(f"• {rec}")
        
        if 'expected_outcomes' in executive_summary:
            st.info("**Ожидаемые результаты:**")
            for outcome in executive_summary['expected_outcomes']:
                st.write(f"• {outcome}")

def display_positioning_analysis(deep_analysis):
    """Отображение анализа позиционирования"""
    st.subheader("Анализ позиционирования")
    
    target_ranking = deep_analysis.get('target_ranking', {})
    market_position = deep_analysis.get('market_position_analysis', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        position = target_ranking.get('position', 'N/A')
        total = target_ranking.get('total_sites', 0)
        st.metric("Позиция в рейтинге", f"{position}/{total}")
    
    with col2:
        percentile = target_ranking.get('percentile', 0)
        st.metric("Процентиль", f"{percentile:.1f}%")
    
    with col3:
        level = target_ranking.get('competitive_level', 'N/A')
        st.metric("Уровень конкурентоспособности", level)
    
    with col4:
        market_share = market_position.get('market_share_estimate', 'N/A')
        st.metric("Оценка доли рынка", market_share)
    
    # Дополнительная информация о позиции
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.write("**Стратегический приоритет:**")
        st.success(market_position.get('strategic_priority', 'N/A'))
        
        st.write("**Потенциал роста:**")
        st.info(market_position.get('growth_potential', 'N/A'))
    
    with col_info2:
        st.write("**Интенсивность конкуренции:**")
        st.warning(market_position.get('competitive_intensity', 'N/A'))
        
        st.write("**Всего проанализировано конкурентов:**")
        st.info(deep_analysis.get('competitors_analyzed', 0))

def display_recommendation_with_examples(recommendation):
    """Отображение рекомендации с примерами"""
    from config import RECOMMENDATION_EXAMPLES
    
    if isinstance(recommendation, dict) and 'example_key' in recommendation:
        example_key = recommendation['example_key']
        text = recommendation['text']
        
        if example_key in RECOMMENDATION_EXAMPLES:
            example = RECOMMENDATION_EXAMPLES[example_key]
            
            # Создаем expander для рекомендации с примером
            with st.expander(f"• {text}", expanded=False):
                st.markdown("**Плохой пример:**")
                st.code(example['bad'], language='html')
                
                st.markdown("**Хороший пример:**") 
                st.code(example['good'], language='html')
                
                st.markdown("**Пояснение:**")
                st.info(example['explanation'])
        else:
            st.info(f"• {text}")
    else:
        # Для обратной совместимости со старым форматом
        st.info(f"• {recommendation}")

def display_competitive_analysis(deep_analysis):
    """Отображение детального конкурентного анализа"""
    st.subheader("Детальный конкурентный анализ")
    
    strengths_weaknesses = deep_analysis.get('strengths_weaknesses', {})
    performance_metrics = deep_analysis.get('performance_metrics', {})
    
    # SWOT анализ
    col_swot1, col_swot2 = st.columns(2)
    
    with col_swot1:
        st.subheader("Сильные стороны")
        strengths = strengths_weaknesses.get('strengths', [])
        if strengths:
            for strength in strengths:
                st.success(f"• {strength}")
        else:
            st.info("• Сильные стороны не выявлены")
        
        st.subheader("Возможности")
        opportunities = strengths_weaknesses.get('opportunities', [])
        if opportunities:
            for opportunity in opportunities:
                st.info(f"• {opportunity}")
        else:
            st.info("• Возможности не выявлены")
    
    with col_swot2:
        st.subheader("Слабые стороны")
        weaknesses = strengths_weaknesses.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.error(f"• {weakness}")
        else:
            st.info("• Слабые стороны не выявлены")
        
        st.subheader("Угрозы")
        threats = strengths_weaknesses.get('threats', [])
        if threats:
            for threat in threats:
                st.warning(f"• {threat}")
        else:
            st.info("• Угрозы не выявлены")
    
    # Анализ разрывов
    st.subheader("Анализ производительности")
    gaps = performance_metrics.get('performance_gaps', {})
    
    if gaps:
        col_gap1, col_gap2, col_gap3, col_gap4 = st.columns(4)
        
        metrics_display = {
            'geo_score': ('GEO оценка', ''),
            'citation_potential': ('Потенциал цитирования', ''),
            'semantic_density': ('Семантическая плотность', ''),
            'content_quality': ('Качество контента', ''),
            'rag_optimization': ('RAG оптимизация', '')
        }
        
        for i, (metric, (name, icon)) in enumerate(metrics_display.items()):
            gap_value = gaps.get(metric, 0)
            col = [col_gap1, col_gap2, col_gap3, col_gap4][i % 4]
            with col:
                if gap_value > 0:
                    st.metric(f"{icon} {name}", f"+{gap_value:.1f}")
                else:
                    st.metric(f"{icon} {name}", f"{gap_value:.1f}")

def display_comparison_matrix(deep_analysis):
    """Отображение матрицы сравнения"""
    st.subheader("Матрица сравнения")
    
    ranking = deep_analysis.get('ranking', [])
    detailed_comparison = deep_analysis.get('detailed_comparison', {})
    
    # Рейтинг сайтов
    if ranking:
        st.write("**Рейтинг сайтов:**")
        
        # Создаем DataFrame для таблицы
        ranking_data = []
        for i, site in enumerate(ranking[:10], 1):  # Ограничиваем 10 сайтами
            ranking_data.append({
                'Позиция': i,
                'URL': site['url'][:50] + "..." if len(site['url']) > 50 else site['url'],
                'Общий скор': site['overall_score'],
                'GEO оценка': site['geo_score'],
                'Уровень': site['performance_tier'],
                'Целевой': '' if site['is_target'] else ''
            })
        
        df = pd.DataFrame(ranking_data)
        st.dataframe(df, width='stretch')
    
    # Бенчмарк анализ
    benchmark = detailed_comparison.get('benchmark_analysis', {})
    if benchmark:
        st.subheader("Отраслевые бенчмарки")
        
        col_bm1, col_bm2, col_bm3 = st.columns(3)
        
        with col_bm1:
            st.metric("Среднее по отрасли", f"{benchmark.get('industry_average', 0):.1f}")
        with col_bm2:
            st.metric("Лидер отрасли", f"{benchmark.get('industry_leader', 0):.1f}")
        with col_bm3:
            range_val = benchmark.get('gap_analysis', {}).get('competitive_range', 0)
            st.metric("Диапазон конкуренции", f"{range_val:.1f}")

def display_improvement_plan(deep_analysis):
    """Отображение плана улучшений"""
    st.subheader("План улучшений")
    
    improvement_potential = deep_analysis.get('improvement_potential', {})
    estimated_impact = improvement_potential.get('estimated_impact', {})
    
    col_imp1, col_imp2 = st.columns(2)
    
    with col_imp1:
        st.subheader("Быстрые победы")
        quick_wins = improvement_potential.get('quick_wins', [])
        if quick_wins:
            for win in quick_wins:
                st.success(f"• {win}")
        else:
            st.info("• Быстрые победы не идентифицированы")
        
        st.subheader("⚡ Немедленные улучшения")
        immediate = improvement_potential.get('immediate_improvements', [])
        if immediate:
            for imp in immediate:
                st.info(f"• {imp}")
        else:
            st.info("• Немедленные улучшения не идентифицированы")
    
    with col_imp2:
        st.subheader("Стратегические инициативы")
        strategic = improvement_potential.get('strategic_improvements', [])
        if strategic:
            for initiative in strategic:
                st.warning(f"• {initiative}")
        else:
            st.info("• Стратегические инициативы не идентифицированы")
        
        st.subheader("Долгосрочные цели")
        long_term = improvement_potential.get('long_term_initiatives', [])
        if long_term:
            for goal in long_term:
                st.error(f"• {goal}")
        else:
            st.info("• Долгосрочные цели не идентифицированы")
    
    # Оценка влияния
    if estimated_impact:
        st.subheader("Оценка влияния улучшений")
        
        col_est1, col_est2, col_est3 = st.columns(3)
        
        with col_est1:
            st.metric("Текущий скор", estimated_impact.get('current_position', 'N/A'))
        with col_est2:
            st.metric("Скор лидера", estimated_impact.get('leader_score', 'N/A'))
        with col_est3:
            st.metric("Временные рамки", estimated_impact.get('estimated_improvement_timeline', 'N/A'))
        
        col_est4, col_est5 = st.columns(2)
        with col_est4:
            st.write("**Потенциал улучшения позиции:**")
            st.info(estimated_impact.get('potential_position_improvement', 'N/A'))
        with col_est5:
            st.write("**Оценка ROI:**")
            st.success(estimated_impact.get('roi_estimate', 'N/A'))

def display_comprehensive_summary(comprehensive_summary):
    """Отображение комплексной сводки"""
    st.subheader("Комплексная сводка анализа")
    
    # Общая оценка
    overall = comprehensive_summary.get('overall_assessment', '')
    if overall:
        st.info("**Общая оценка:**")
        st.write(overall)
    
    # Ключевые находки
    key_findings = comprehensive_summary.get('key_findings', [])
    if key_findings:
        st.success("**Ключевые находки:**")
        for finding in key_findings:
            st.write(f"• {finding}")
    
    # Стратегические импликации
    implications = comprehensive_summary.get('strategic_implications', [])
    if implications:
        st.warning("**Стратегические импликации:**")
        for implication in implications:
            st.write(f"• {implication}")
    
    # План действий
    action_plan = comprehensive_summary.get('action_plan', {})
    if action_plan:
        st.info("**Рекомендуемый план действий:**")
        
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            st.write("**Немедленные действия:**")
            for action in action_plan.get('immediate_actions', []):
                st.write(f"• {action}")
            
            st.write("**Стратегические инициативы:**")
            for initiative in action_plan.get('strategic_initiatives', []):
                st.write(f"• {initiative}")
        
        with col_act2:
            st.write("**Быстрые победы:**")
            for win in action_plan.get('quick_wins', []):
                st.write(f"• {win}")
            
            st.write("**Долгосрочные цели:**")
            for goal in action_plan.get('long_term_goals', []):
                st.write(f"• {goal}")
    
    # Метрики успеха и риски
    col_final1, col_final2 = st.columns(2)
    
    with col_final1:
        success_metrics = comprehensive_summary.get('success_metrics', [])
        if success_metrics:
            st.success("**Метрики успеха:**")
            for metric in success_metrics:
                st.write(f"• {metric}")
    
    with col_final2:
        risks = comprehensive_summary.get('risk_assessment', [])
        if risks:
            st.error("**Оценка рисков:**")
            for risk in risks:
                st.write(f"• {risk}")
    
    # Следующие шаги
    next_steps = comprehensive_summary.get('next_steps', [])
    if next_steps:
        st.info("**Рекомендуемые следующие шаги:**")
        for step in next_steps:
            st.write(f"• {step}")