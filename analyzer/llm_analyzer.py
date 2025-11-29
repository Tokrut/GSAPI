# [file name]: analyzer/llm_analyzer.py (обновленная версия)
"""
LLM-анализатор для GEO (Generative Engine Optimization)
Интеграция с Bert-Nebulon, Grok и DeepSeek для анализа дружелюбности контента к генеративному поиску
"""

import json
import re
from typing import Dict, List, Any, Optional
from openai import OpenAI
from config import ANALYSIS_CONFIG

class LLMAnalyzer:
    """Анализатор контента с использованием LLM для генеративного поиска"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        self.llm_models = {
            'bert_nebulon': 'openrouter/bert-nebulon-alpha',
            'grok': 'x-ai/grok-4.1-fast:free',  # Изменена модель на более стабильную
            'deepseek': 'tngtech/deepseek-r1t2-chimera:free'
        }
    
    def analyze_content_for_geo(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод анализа контента для генеративного поиска
        
        Args:
            content_data: Данные контента из анализатора
            
        Returns:
            Результаты LLM-анализа
        """
        try:
            # Подготавливаем данные для LLM
            llm_input = self._prepare_llm_input(content_data)
            
            # Запускаем анализ всеми моделями параллельно
            results = self._parallel_llm_analysis(llm_input)
            
            # Агрегируем результаты
            return self._aggregate_llm_results(results, content_data)
            
        except Exception as e:
            return self._get_fallback_analysis(content_data, str(e))
    
    def _parallel_llm_analysis(self, llm_input: str) -> Dict[str, Any]:
        """Параллельный анализ всеми LLM-моделями"""
        import concurrent.futures
        import threading
        
        results = {}
        
        # Функция для анализа одной моделью
        def analyze_model(model_name: str) -> tuple[str, Dict[str, Any]]:
            try:
                if model_name == 'bert_nebulon':
                    return model_name, self._analyze_with_bert_nebulon(llm_input)
                elif model_name == 'grok':
                    return model_name, self._analyze_with_grok(llm_input)
                elif model_name == 'deepseek':
                    return model_name, self._analyze_with_deepseek(llm_input)
                else:
                    return model_name, {'error': f'Unknown model: {model_name}'}
            except Exception as e:
                return model_name, {'error': f'{model_name} analysis failed: {str(e)}'}
        
        # Запускаем анализ всех моделей параллельно
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Создаем задачи для каждой модели
            future_to_model = {
                executor.submit(analyze_model, model): model 
                for model in ['bert_nebulon', 'grok', 'deepseek']
            }
            
            # Обрабатываем результаты по мере их готовности
            for future in concurrent.futures.as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    model_name, result = future.result(timeout=60)  # 60 секунд на модель
                    results[model_name] = result
                except concurrent.futures.TimeoutError:
                    results[model] = {'error': f'Timeout for {model} analysis'}
                except Exception as e:
                    results[model] = {'error': f'Error in {model} analysis: {str(e)}'}
        
        return results
    
    def _prepare_llm_input(self, content_data: Dict[str, Any]) -> str:
        """Подготовка данных для отправки в LLM"""
        
        # Извлекаем ключевые элементы контента
        basic_info = content_data.get('basic_info', {})
        metadata = content_data.get('metadata', {})
        content_structure = content_data.get('content_structure', {})
        semantic_markup = content_data.get('semantic_markup', {})
        
        # Формируем структурированный промпт
        llm_input = f"""
        Анализ веб-страницы для оптимизации под генеративный поиск (GEO):

        ОСНОВНАЯ ИНФОРМАЦИЯ:
        - URL: {basic_info.get('url', 'Неизвестно')}
        - Title: {metadata.get('title', {}).get('value', 'Отсутствует')}
        - Description: {metadata.get('description', {}).get('value', 'Отсутствует')}

        СТРУКТУРА КОНТЕНТА:
        - Объем текста: {content_structure.get('word_count', 0)} слов
        - Заголовки: H1: {semantic_markup.get('headings', {}).get('h1', 0)}, H2: {semantic_markup.get('headings', {}).get('h2', 0)}
        - Изображения: {content_structure.get('images', {}).get('total', 0)} всего, {content_structure.get('images', {}).get('with_alt', 0)} с alt-текстом
        - Списки: {content_structure.get('lists', {}).get('total', 0)}
        - Таблицы: {content_structure.get('tables', 0)}

        СЕМАНТИЧЕСКАЯ РАЗМЕТКА:
        - Schema.org: {'Присутствует' if semantic_markup.get('schema_org', {}).get('exists') else 'Отсутствует'}
        - Микроразметка: {'Присутствует' if semantic_markup.get('microdata', {}).get('exists') else 'Отсутствует'}
        - Open Graph: {'Присутствует' if metadata.get('open_graph', {}).get('exists') else 'Отсутствует'}

        ТЕКСТ КОНТЕНТА (первые 2000 символов):
        {self._extract_content_preview(content_data)}
        """
        
        return llm_input
    
    def _extract_content_preview(self, content_data: Dict[str, Any]) -> str:
        """Извлечение превью контента для анализа"""
        content_text = content_data.get('content_structure', {}).get('readability_sample_text', '')
        if not content_text:
            content_text = "Текст контента недоступен для анализа"
        
        # Ограничиваем длину для LLM
        return content_text[:2000]
    
    def _analyze_with_bert_nebulon(self, llm_input: str) -> Dict[str, Any]:
        """Анализ с помощью Bert-Nebulon с развернутым ответом и 100-балльной оценкой"""
        try:
            prompt = f"""
            Ты - эксперт по Generative Engine Optimization (GEO) и поисковой оптимизации для AI-ассистентов. 
            Проанализируй предоставленные данные веб-страницы и дай развернутую оценку её дружелюбности 
            к генеративным AI-моделям (ChatGPT, Claude, Gemini, Grok и др.).

            {llm_input}

            Пожалуйста, предоставь подробный анализ по следующим аспектам:

            ## 1. ОБЩАЯ ОЦЕНКА GEO-ОПТИМИЗАЦИИ (0-100 баллов)
            - Насколько хорошо страница подготовлена для генеративного поиска?
            - Каков потенциал для цитирования контента в ответах AI-ассистентов?
            - Насколько легко AI-модели могут извлекать и пересказывать информацию?

            ## 2. СТРУКТУРА CLEAR ANSWERS (0-100 баллов)
            - Есть ли на странице четкие, готовые ответы на потенциальные вопросы?
            - Насколько хорошо структурирована информация для формирования snippets?
            - Имеются ли явные Q&A разделы или структурированные данные?

            ## 3. СЕМАНТИЧЕСКАЯ НАСЫЩЕННОСТЬ (0-100 баллов)
            - Достаточно ли семантических маркеров для понимания контекста AI?
            - Насколько богат контент с точки зрения информационной плотности?
            - Есть ли проблемы с пониманием основной темы страницы?

            ## 4. ТЕХНИЧЕСКАЯ ОПТИМИЗАЦИЯ (0-100 баллов)
            - Качество метаданных (title, description)
            - Наличие и качество семантической разметки
            - Оптимизация для мобильных устройств

            ## 5. РЕКОМЕНДАЦИИ ПО УЛУЧШЕНИЮ
            - Конкретные шаги по улучшению видимости в генеративном поиске
            - Советы по структурированию контента для лучшего цитирования
            - Оптимизация метаданных и семантической разметки

            ## 6. ИТОГОВАЯ ОЦЕНКА
            Предоставь итоговую оценку по 100-балльной шкале, где:
            - 0-30: Критически низкая оптимизация
            - 31-60: Средний уровень, требует значительных улучшений
            - 61-80: Хорошая оптимизация
            - 81-100: Отличная оптимизация для генеративного поиска

            В конце анализа укажи: "ИТОГОВАЯ ОЦЕНКА: [число]/100"

            Предоставь развернутый, структурированный ответ на русском языке.
            """
            
            completion = self.client.chat.completions.create(
                model=self.llm_models['bert_nebulon'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            response_text = completion.choices[0].message.content
            return self._parse_100_point_response(response_text, 'bert_nebulon')
            
        except Exception as e:
            return {"error": f"Bert-Nebulon analysis failed: {str(e)}"}
    
    def _analyze_with_grok(self, llm_input: str) -> Dict[str, Any]:
        """Анализ с помощью Grok с развернутым ответом и 100-балльной оценкой"""
        try:
            prompt = f"""
            Ты - senior эксперт по Generative Engine Optimization (GEO) и поисковой оптимизации для AI-ассистентов, включая модели Grok.
            Проанализируй предоставленные данные веб-страницы и дай развернутую оценку её дружелюбности к генеративным AI-моделям.

            {llm_input}

            Пожалуйста, предоставь подробный анализ по следующим аспектам:

            ## 1. ОБЩАЯ ОЦЕНКА GEO-ОПТИМИЗАЦИИ ДЛЯ GROK (0-100 баллов)
            - Насколько хорошо страница подготовлена для генеративного поиска в Grok и аналогичных моделях?
            - Каков потенциал для цитирования контента в ответах Grok?
            - Насколько легко Grok может извлекать и пересказывать информацию?

            ## 2. СТРУКТУРА ДЛЯ REASONING АНАЛИЗА (0-100 баллов)
            - Есть ли на странице логические цепочки и причинно-следственные связи?
            - Насколько хорошо структурирована информация для формирования развернутых reasoning?
            - Имеются ли явные аргументы и доказательства?

            ## 3. СЕМАНТИЧЕСКАЯ ПЛОТНОСТЬ ДЛЯ GROK (0-100 баллов)
            - Достаточно ли семантических маркеров для глубокого понимания контекста Grok?
            - Насколько богат контент с точки зрения информационной глубины?
            - Есть ли проблемы с логической последовательностью?

            ## 4. ПОТЕНЦИАЛ ДЛЯ РАЗВЕРНУТЫХ ОТВЕТОВ (0-100 баллов)
            - Оценка потенциала контента для формирования комплексных ответов
            - Наличие материалов для формирования многоуровневых рассуждений
            - Потенциал для использования в RAG-системах

            ## 5. СПЕЦИФИЧЕСКИЕ РЕКОМЕНДАЦИИ ДЛЯ GROK
            - Конкретные шаги по улучшению видимости в Grok и аналогичных моделях
            - Советы по структурированию контента для лучшего reasoning
            - Оптимизация для формирования развернутых ответов

            ## 6. ИТОГОВАЯ ОЦЕНКА
            Предоставь итоговую оценку по 100-балльной шкале, где:
            - 0-30: Критически низкая оптимизация для Grok
            - 31-60: Средний уровень, требует значительных улучшений
            - 61-80: Хорошая оптимизация для reasoning-моделей
            - 81-100: Отличная оптимизация для Grok и аналогичных AI

            В конце анализа укажи: "ИТОГОВАЯ ОЦЕНКА: [число]/100"

            Предоставь развернутый, структурированный ответ на русском языке с акцентом на особенности Grok.
            """
            
            completion = self.client.chat.completions.create(
                model=self.llm_models['grok'],
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = completion.choices[0].message.content
            return self._parse_100_point_response(response_text, 'grok')
            
        except Exception as e:
            return {"error": f"Grok analysis failed: {str(e)}"}
    
    def _parse_100_point_response(self, response_text: str, model: str) -> Dict[str, Any]:
        """Парсинг ответов с 100-балльной оценкой"""
        try:
            result = {
                "raw_response": response_text,
                "model": model,
                "type": "100_point_analysis",
                "scores": {},
                "recommendations": [],
                "category_scores": {},
                "summary": ""
            }
    
            # Извлекаем итоговую оценку (100-балльная шкала)
            final_score_match = re.search(r'ИТОГОВАЯ ОЦЕНКА:\s*(\d+)/100', response_text, re.IGNORECASE)
            if final_score_match:
                try:
                    result["scores"]["overall"] = int(final_score_match.group(1))
                except (ValueError, IndexError):
                    pass
            
            # Извлекаем оценки по категориям
            category_patterns = {
                'general': r'ОБЩАЯ ОЦЕНКА.*?(\d+)/100',
                'citation': r'ЦИТИРОВАНИЯ.*?(\d+)/100|ПОТЕНЦИАЛ.*?ЦИТИРОВАНИЯ.*?(\d+)/100',
                'semantic': r'СЕМАНТИЧЕСКАЯ.*?(\d+)/100',
                'structure': r'СТРУКТУРА.*?(\d+)/100',
                'technical': r'ТЕХНИЧЕСКАЯ.*?(\d+)/100',
                'rag': r'RAG.*?(\d+)/100'
            }
            
            for key, pattern in category_patterns.items():
                matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    for match in matches:
                        score = match[0] if isinstance(match, tuple) and match[0] else match
                        if score and score.isdigit():
                            try:
                                result["category_scores"][key] = int(score)
                                break
                            except (ValueError, IndexError):
                                pass
            
            # Извлекаем рекомендации
            rec_section = re.search(r'РЕКОМЕНДАЦИИ.*?(?=ИТОГОВАЯ|$)', response_text, re.IGNORECASE | re.DOTALL)
            if rec_section:
                rec_text = rec_section.group(0)
                rec_points = re.findall(r'[•-]\s*([^\n]+)|\d+\.\s*([^\n]+)', rec_text)
                for point in rec_points:
                    text = point[0] if point[0] else point[1]
                    if text and len(text.strip()) > 15:
                        result["recommendations"].append(text.strip())
            
            # Если не нашли рекомендаций через паттерны, ищем в общем тексте
            if not result["recommendations"]:
                rec_matches = re.findall(r'-\s*(.+?)(?=\n-|\n\d+\.|\n##|$)', response_text, re.IGNORECASE)
                for match in rec_matches:
                    if len(match.strip()) > 20:
                        result["recommendations"].append(match.strip())
            
            # Создаем сводку
            overall_score = result["scores"].get("overall", 0)
            if overall_score >= 81:
                result["summary"] = "Отличная оптимизация для генеративного поиска"
            elif overall_score >= 61:
                result["summary"] = "Хорошая оптимизация, есть потенциал для улучшений"
            elif overall_score >= 31:
                result["summary"] = "Средний уровень, требует значительных улучшений"
            else:
                result["summary"] = "Критически низкая оптимизация"
            
            return result
            
        except Exception as e:
            return {
                "raw_response": response_text,
                "model": model,
                "error": f"Error parsing {model} response: {str(e)}"
            }
    
    def _analyze_with_deepseek(self, llm_input: str) -> Dict[str, Any]:
        """Анализ с помощью DeepSeek с развернутым ответом и 100-балльной оценкой"""
        try:
            prompt = f"""
            Как эксперт по семантическому поиску и AI-оптимизации, оцени этот контент для генеративного поиска.

            {llm_input}

            Пожалуйста, предоставь детальный анализ по следующим направлениям:

            ## 1. СЕМАНТИЧЕСКАЯ ПЛОТНОСТЬ (0-100 баллов)
            - Насколько богат контент с точки зрения смысловой нагрузки?
            - Достаточно ли контекста для понимания темы AI-моделями?
            - Есть ли проблемы с двусмысленностью или недостатком информации?

            ## 2. ПОТЕНЦИАЛ ДЛЯ ОТВЕТОВ НА ЗАПРОСЫ (0-100 баллов)
            - Насколько хорошо контент отвечает на потенциальные вопросы пользователей?
            - Есть ли coverage для различных типов запросов (информационные, коммерческие, навигационные)?
            - Какой потенциал для формирования featured snippets?

            ## 3. СТРУКТУРА ДЛЯ ИЗВЛЕЧЕНИЯ ИНФОРМАЦИИ (0-100 баллов)
            - Насколько легко AI может извлекать ключевые факты и данные?
            - Хорошо ли организована информация для машинного понимания?
            - Есть ли проблемы с логической структурой контента?

            ## 4. RAG-ОПТИМИЗАЦИЯ (0-100 баллов)
            - Пригодность контента для Retrieval-Augmented Generation систем
            - Потенциал для использования в векторных базах данных
            - Оптимизация для семантического поиска

            ## 5. РЕКОМЕНДАЦИИ ДЛЯ DEEPSEEK И АНАЛОГИЧНЫХ МОДЕЛЕЙ
            - Специфические улучшения для лучшего понимания DeepSeek-like моделями
            - Оптимизация для RAG (Retrieval-Augmented Generation) систем
            - Улучшения семантического ядра контента

            ## 6. ИТОГОВАЯ ОЦЕНКА
            Предоставь итоговую оценку по 100-балльной шкале, где:
            - 0-30: Критически низкая семантическая оптимизация
            - 31-60: Средний уровень, требует улучшений
            - 61-80: Хорошая семантическая плотность
            - 81-100: Отличная оптимизация для семантического поиска

            В конце анализа укажи: "ИТОГОВАЯ ОЦЕНКА: [число]/100"

            Предоставь развернутый, структурированный ответ на русском языке.
            """
            
            completion = self.client.chat.completions.create(
                model=self.llm_models['deepseek'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2500
            )
            
            response_text = completion.choices[0].message.content
            return self._parse_100_point_response(response_text, 'deepseek')
            
        except Exception as e:
            return {"error": f"DeepSeek analysis failed: {str(e)}"}
    
    def _parse_text_response(self, response_text: str, model: str) -> Dict[str, Any]:
        """Парсинг текстовых ответов LLM для извлечения структурированной информации"""
        try:
            result = {
                "raw_response": response_text,
                "model": model,
                "type": "text_analysis",
                "scores": {},
                "recommendations": []
            }
            
            # Извлекаем оценки из текста с помощью регулярных выражений
            score_patterns = {
                'overall': r'оценк[ауи]\s*[:\-]?\s*(\d+)(?:\s*\/\s*10)?',
                'general': r'общая\s+оценк[ауи]\s*[:\-]?\s*(\d+)(?:\s*\/\s*10)?',
                'citation': r'цитировани[ея]\s*[:\-]?\s*(\d+)(?:\s*\/\s*10)?',
                'semantic': r'семантич[а-я]+\s*[:\-]?\s*(\d+)(?:\s*\/\s*10)?',
                'structure': r'структур[а-я]+\s*[:\-]?\s*(\d+)(?:\s*\/\s*10)?'
            }
            
            for key, pattern in score_patterns.items():
                matches = re.findall(pattern, response_text.lower())
                if matches:
                    # Берем первую найденную оценку
                    try:
                        result["scores"][key] = int(matches[0])
                    except (ValueError, IndexError):
                        pass
            
            # Извлекаем рекомендации (ищем маркированные списки)
            recommendation_patterns = [
                r'[•\-]\s*(.+?)(?=\n[•\-]|\n\n|$)',
                r'\d+\.\s*(.+?)(?=\n\d+\.|\n\n|$)',
                r'рекомендаци[яи][^.•\n]*[.•]\s*(.+?)(?=\n[•\d]|\n\n|$)'
            ]
            
            for pattern in recommendation_patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    rec = match.strip()
                    if len(rec) > 10 and rec not in result["recommendations"]:
                        result["recommendations"].append(rec)
            
            # Если не нашли рекомендаций через паттерны, попробуем найти раздел с рекомендациями
            if not result["recommendations"]:
                rec_section = re.search(r'рекомендаци[яи][^•\n]*(.*?)(?=\n\n|\n[A-ZА-Я]|$)', 
                                      response_text, re.IGNORECASE | re.DOTALL)
                if rec_section:
                    # Разбиваем на предложения
                    sentences = re.split(r'[.!?]+', rec_section.group(1))
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 20 and not sentence.startswith(('http', 'www')):
                            result["recommendations"].append(sentence)
            
            return result
            
        except Exception as e:
            return {
                "raw_response": response_text,
                "model": model,
                "error": f"Error parsing response: {str(e)}"
            }
    
    def _aggregate_llm_results(self, results: Dict[str, Any], content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Улучшенная агрегация результатов от всех LLM с 100-балльной шкалой"""
        
        aggregated = {
            'models_used': list(results.keys()),
            'overall_geo_score': 0,
            'geo_analysis': {},
            'llm_insights': [],
            'geo_recommendations': [],
            'citation_potential': 0,
            'clear_answer_quality': 0,
            'rag_optimization_score': 0,
            'semantic_density_score': 0,
            'llm_specific_findings': {},
            'detailed_analysis': {},
            'category_scores': {},
            'model_scores': {}
        }
        
        # Обрабатываем результаты каждой модели
        total_overall_score = 0
        total_citation_score = 0
        total_semantic_score = 0
        total_structure_score = 0
        total_technical_score = 0
        total_rag_score = 0
        
        model_count = 0
        citation_count = 0
        semantic_count = 0
        structure_count = 0
        technical_count = 0
        rag_count = 0
        
        for model_name, result in results.items():
            if 'error' not in result:
                aggregated['llm_specific_findings'][model_name] = result
                aggregated['model_scores'][model_name] = {}
                
                # Извлекаем оценки из каждой модели
                scores = result.get('scores', {})
                category_scores = result.get('category_scores', {})
                
                # Общая оценка модели
                overall_score = scores.get('overall')
                if overall_score:
                    total_overall_score += overall_score
                    aggregated['model_scores'][model_name]['overall'] = overall_score
                    model_count += 1
                
                # Оценки по категориям
                citation_score = category_scores.get('citation') or scores.get('citation')
                if citation_score:
                    total_citation_score += citation_score
                    citation_count += 1
                    aggregated['model_scores'][model_name]['citation'] = citation_score
                
                semantic_score = category_scores.get('semantic') or scores.get('semantic')
                if semantic_score:
                    total_semantic_score += semantic_score
                    semantic_count += 1
                    aggregated['model_scores'][model_name]['semantic'] = semantic_score
                
                structure_score = category_scores.get('structure') or scores.get('structure')
                if structure_score:
                    total_structure_score += structure_score
                    structure_count += 1
                    aggregated['model_scores'][model_name]['structure'] = structure_score
                
                technical_score = category_scores.get('technical') or scores.get('technical')
                if technical_score:
                    total_technical_score += technical_score
                    technical_count += 1
                    aggregated['model_scores'][model_name]['technical'] = technical_score
                
                rag_score = category_scores.get('rag') or scores.get('rag')
                if rag_score:
                    total_rag_score += rag_score
                    rag_count += 1
                    aggregated['model_scores'][model_name]['rag'] = rag_score
                
                # Добавляем рекомендации от каждой модели
                recommendations = result.get('recommendations', [])
                aggregated['geo_recommendations'].extend(recommendations)
                
                # Сохраняем детальный анализ
                aggregated['detailed_analysis'][model_name] = result.get('raw_response', '')
                
                # Добавляем инсайты
                summary = result.get('summary', '')
                if summary:
                    aggregated['llm_insights'].append(f"{model_name}: {summary}")
        
        # Рассчитываем средние оценки
        if model_count > 0:
            aggregated['overall_geo_score'] = total_overall_score / model_count
        else:
            aggregated['overall_geo_score'] = self._calculate_fallback_geo_score(content_data)
        
        if citation_count > 0:
            aggregated['citation_potential'] = total_citation_score / citation_count
        else:
            aggregated['citation_potential'] = aggregated['overall_geo_score'] * 0.8
        
        if semantic_count > 0:
            aggregated['semantic_density_score'] = total_semantic_score / semantic_count
        else:
            aggregated['semantic_density_score'] = aggregated['overall_geo_score'] * 0.7
        
        if structure_count > 0:
            aggregated['clear_answer_quality'] = total_structure_score / structure_count
        else:
            aggregated['clear_answer_quality'] = aggregated['overall_geo_score'] * 0.75
        
        if rag_count > 0:
            aggregated['rag_optimization_score'] = total_rag_score / rag_count
        else:
            aggregated['rag_optimization_score'] = aggregated['overall_geo_score'] * 0.6
        
        # Собираем категорийные оценки
        aggregated['category_scores'] = {
            'citation': aggregated['citation_potential'],
            'semantic': aggregated['semantic_density_score'],
            'structure': aggregated['clear_answer_quality'],
            'technical': total_technical_score / technical_count if technical_count > 0 else aggregated['overall_geo_score'] * 0.7,
            'rag': aggregated['rag_optimization_score']
        }
        
        # Уникализируем и сортируем рекомендации по приоритету
        unique_recommendations = list(set(aggregated['geo_recommendations']))
        # Сортируем рекомендации по длине (более длинные обычно более детальные)
        aggregated['geo_recommendations'] = sorted(unique_recommendations, key=len, reverse=True)[:10]  # Ограничиваем до 10 лучших
        
        # Создаем расширенную сводку анализа
        aggregated['analysis_summary'] = self._create_detailed_analysis_summary(aggregated)
        
        return aggregated
    
    def _create_detailed_analysis_summary(self, aggregated: Dict[str, Any]) -> str:
        """Создание детальной сводки анализа на основе обновленной агрегации"""
        summary_parts = []
        
        geo_score = aggregated.get('overall_geo_score', 0)
        category_scores = aggregated.get('category_scores', {})
        model_scores = aggregated.get('model_scores', {})
        
        # Общая оценка
        if geo_score >= 85:
            summary_parts.append(f"Отличная оптимизация для генеративного поиска ({geo_score:.1f}/100)")
        elif geo_score >= 70:
            summary_parts.append(f"Хорошая оптимизация, но есть возможности для улучшения ({geo_score:.1f}/100)")
        elif geo_score >= 50:
            summary_parts.append(f"Средняя оптимизация, требуется значительная доработка ({geo_score:.1f}/100)")
        else:
            summary_parts.append(f"Низкая оптимизация, необходим комплексный подход к улучшению ({geo_score:.1f}/100)")
        
        # Оценки по категориям
        citation_score = category_scores.get('citation', 0)
        if citation_score >= 80:
            summary_parts.append("Отличный потенциал для цитирования")
        elif citation_score >= 60:
            summary_parts.append("Хороший потенциал цитирования")
        else:
            summary_parts.append("Требуется улучшение потенциала цитирования")
        
        semantic_score = category_scores.get('semantic', 0)
        if semantic_score >= 75:
            summary_parts.append("Высокая семантическая плотность")
        elif semantic_score >= 50:
            summary_parts.append("Удовлетворительная семантическая плотность")
        else:
            summary_parts.append("Требуется улучшение семантической плотности")
        
        # Информация о моделях
        if model_scores:
            active_models = list(model_scores.keys())
            model_count = len(active_models)
            summary_parts.append(f"Анализ выполнен {model_count} моделями: {', '.join(active_models)}")
        
        # Рекомендации
        recommendations_count = len(aggregated.get('geo_recommendations', []))
        if recommendations_count > 0:
            summary_parts.append(f"Предложено {recommendations_count} ключевых рекомендаций")
        
        # Добавляем общую оценку по моделям
        model_scores_str = []
        for model_name, scores in model_scores.items():
            overall = scores.get('overall')
            if overall:
                model_scores_str.append(f"{model_name}: {overall}/100")
        
        if model_scores_str:
            summary_parts.append(f"Оценки моделей: {', '.join(model_scores_str)}")
        
        return ". ".join(summary_parts)
    
    def _create_analysis_summary(self, aggregated: Dict[str, Any]) -> str:
        """Короткая сводка для совместимости с старой версией"""
        return self._create_detailed_analysis_summary(aggregated)
    
    def _calculate_fallback_geo_score(self, content_data: Dict[str, Any]) -> int:
        """Расчет GEO-оценки на основе структурных данных (fallback)"""
        score = 50  # Базовый балл
        
        # Бонусы за хорошие практики
        if content_data.get('metadata', {}).get('title', {}).get('value'):
            score += 10
        if content_data.get('metadata', {}).get('description', {}).get('value'):
            score += 10
        if content_data.get('semantic_markup', {}).get('schema_org', {}).get('exists'):
            score += 15
        if content_data.get('content_structure', {}).get('word_count', 0) > 300:
            score += 10
        if content_data.get('content_structure', {}).get('images', {}).get('alt_percentage', 0) > 50:
            score += 5
        
        return min(score, 100)
    
    def _get_fallback_analysis(self, content_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Fallback анализ при ошибках LLM"""
        return {
            'models_used': [],
            'overall_geo_score': self._calculate_fallback_geo_score(content_data),
            'geo_analysis': {'error': error_msg},
            'llm_insights': ['LLM анализ временно недоступен. Используется структурный анализ.'],
            'geo_recommendations': [
                "Добавьте четкие ответы на частые вопросы",
                "Структурируйте контент для легкого извлечения информации",
                "Используйте семантическую разметку Schema.org",
                "Оптимизируйте заголовки и мета-описания",
                "Создавайте контент с явными выводами и заключениями"
            ],
            'citation_potential': 50,
            'clear_answer_quality': 50,
            'llm_specific_findings': {},
            'fallback_analysis': True,
            'analysis_summary': 'Используется fallback-анализ на основе структурных метрик'
        }