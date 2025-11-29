# [file name]: analyzer/deep_llm_analyzer.py
"""
Глубокий LLM-анализатор для GEO с поиском конкурентов
Расширенная версия с сравнительным анализом аналогичных сайтов и комплексными итогами
"""

import json
import re
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime
from analyzer.llm_analyzer import LLMAnalyzer
from config import ANALYSIS_CONFIG

# Настройка логирования
logger = logging.getLogger(__name__)


class DeepLLMAnalyzer(LLMAnalyzer):
    """Расширенный анализатор с поиском конкурентов и комплексным сравнительным анализом"""
    
    def __init__(self):
        super().__init__()
        self.competitor_cache = {}
        self.comparative_analysis_cache = {}
    
    def deep_analyze_with_competitors(self, target_url: str, max_competitors: int = 5) -> Dict[str, Any]:
        """
        Глубокий анализ сайта с поиском и оценкой конкурентов
        
        Args:
            target_url: URL целевого сайта для анализа
            max_competitors: максимальное количество конкурентов для поиска
            
        Returns:
            Результаты сравнительного анализа с комплексными итогами
        """
        try:
            logger.info(f"🚀 Начинаем глубокий анализ для: {target_url}")
            
            # Проверяем кэш
            cache_key = f"{target_url}_{max_competitors}"
            if cache_key in self.comparative_analysis_cache:
                logger.info("📁 Используем кэшированные результаты анализа")
                return self.comparative_analysis_cache[cache_key]
            
            # Шаг 1: Получаем конкурентов через DeepSeek
            logger.info("🔍 Поиск аналогичных сайтов...")
            competitors = self._find_competitors_with_deepseek(target_url, max_competitors)
            
            # Шаг 2: Собираем все URL для анализа
            all_urls = [target_url] + competitors
            logger.info(f"📊 Анализируем {len(all_urls)} сайтов: {all_urls}")
            
            # Шаг 3: Анализируем каждый URL
            analysis_results = {}
            for url in all_urls:
                logger.info(f"🔄 Анализ {url}...")
                content_data = self._fetch_content_data(url)
                if content_data:
                    analysis_results[url] = self.analyze_content_for_geo(content_data)
                    time.sleep(2)  # Задержка между запросами
                else:
                    logger.warning(f"⚠️ Не удалось получить данные для {url}")
                    analysis_results[url] = self._get_fallback_analysis({})
            
            # Шаг 4: Сравнительный анализ с комплексными итогами
            logger.info("📈 Выполняем комплексный сравнительный анализ...")
            comparative_analysis = self._perform_comprehensive_comparative_analysis(
                analysis_results, target_url, competitors
            )
            
            # Шаг 5: Генерация итогового отчета
            logger.info("📋 Генерируем итоговый отчет...")
            comparative_analysis['comprehensive_summary'] = self._generate_comprehensive_summary(
                comparative_analysis
            )
            
            # Сохраняем в кэш
            self.comparative_analysis_cache[cache_key] = comparative_analysis
            
            return comparative_analysis
            
        except Exception as e:
            logger.error(f"❌ Ошибка в глубоком анализе: {str(e)}")
            return self._get_deep_fallback_analysis(target_url, str(e))
    
    def _perform_comprehensive_comparative_analysis(self, analysis_results: Dict[str, Any], 
                                              target_url: str, competitors: List[str]) -> Dict[str, Any]:
        """Комплексный сравнительный анализ с исправлениями доступа к позициям"""
        comparative = {
            'target_url': target_url,
            'competitors_list': competitors,
            'competitors_analyzed': len(competitors),
            'total_sites_analyzed': len(analysis_results),
            'analysis_timestamp': datetime.now().isoformat(),
            'ranking': [],
            'competitive_analysis': {},
            'strengths_weaknesses': {},
            'strategic_recommendations': [],
            'performance_metrics': {},
            'market_position_analysis': {},
            'improvement_potential': {},
            'detailed_comparison': {},
            'executive_summary': {}
        }
        
        # Создаем рейтинг сайтов
        rankings = self._create_comprehensive_ranking(analysis_results, target_url)
        comparative['ranking'] = rankings
        
        # Определяем позицию целевого сайта с исправлением
        target_rank = next((r for r in rankings if r['is_target']), None)
        if target_rank:
            target_position = target_rank.get('position', 0)
            total_sites = len(rankings)
            
            comparative['target_ranking'] = {
                'position': target_position,
                'total_sites': total_sites,
                'percentile': ((total_sites - target_position) / total_sites) * 100 if target_position > 0 else 0,
                'competitive_level': self._get_competitive_level(target_position, total_sites)
            }
        else:
            comparative['target_ranking'] = {
                'position': 'N/A',
                'total_sites': len(rankings),
                'percentile': 0,
                'competitive_level': 'Не определено'
            }
        
        # Комплексный анализ конкурентной позиции
        comparative['strengths_weaknesses'] = self._analyze_comprehensive_competitive_position(
            analysis_results[target_url], rankings, analysis_results
        )
        
        # Анализ метрик производительности
        comparative['performance_metrics'] = self._analyze_performance_metrics(analysis_results, target_url)
        
        # Анализ рыночной позиции
        comparative['market_position_analysis'] = self._analyze_market_position(rankings, target_url)
        
        # Потенциал улучшений
        comparative['improvement_potential'] = self._analyze_improvement_potential(
            analysis_results[target_url], rankings
        )
        
        # Детальное сравнение
        comparative['detailed_comparison'] = self._create_detailed_comparison_matrix(analysis_results)
        
        # Стратегические рекомендации
        comparative['strategic_recommendations'] = self._generate_strategic_recommendations(
            comparative, analysis_results
        )
        
        # Исполнительное резюме
        comparative['executive_summary'] = self._generate_executive_summary(comparative)
    
        return comparative
    
    def _create_comprehensive_ranking(self, analysis_results: Dict[str, Any], target_url: str) -> List[Dict]:
        """Создание комплексного рейтинга сайтов с добавлением позиций"""
        rankings = []
        
        for url, analysis in analysis_results.items():
            # Берем GEO оценку как основную метрику
            geo_score = analysis.get('overall_geo_score', 0)
            
            # Если GEO оценки нет, используем общую оценку
            if geo_score == 0:
                geo_score = analysis.get('score', 0) * 0.8  # Приводим к шкале GEO
            
            # Дополнительные метрики для рейтинга
            citation_score = analysis.get('citation_potential', geo_score * 0.8)
            semantic_score = analysis.get('semantic_density_score', geo_score * 0.7)
            structure_score = analysis.get('clear_answer_quality', geo_score * 0.75)
            rag_score = analysis.get('rag_optimization_score', geo_score * 0.6)
            
            # Композитный скор (взвешенная сумма)
            composite_score = (
                geo_score * 0.4 +
                citation_score * 0.2 +
                semantic_score * 0.15 +
                structure_score * 0.15 +
                rag_score * 0.1
            )
            
            rankings.append({
                'url': url,
                'overall_score': round(composite_score, 1),
                'geo_score': round(geo_score, 1),
                'citation_potential': round(citation_score, 1),
                'semantic_density': round(semantic_score, 1),
                'clear_answers': round(structure_score, 1),
                'rag_score': round(rag_score, 1),
                'is_target': url == target_url,
                'performance_tier': self._get_performance_tier(composite_score)
            })
        
        # Сортируем по убыванию общего скора
        rankings.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Добавляем позиции в рейтинге
        for index, rank in enumerate(rankings):
            rank['position'] = index + 1
        
        return rankings
    
    def _get_performance_tier(self, score: float) -> str:
        """Определение уровня производительности"""
        if score >= 85:
            return "Лидер"
        elif score >= 70:
            return "Сильный игрок"
        elif score >= 55:
            return "Средний уровень"
        elif score >= 40:
            return "Требует улучшений"
        else:
            return "Отстающий"
    
    def _get_competitive_level(self, position: int, total: int) -> str:
        """Определение уровня конкурентоспособности"""
        if position == 0:
            return "Лидер рынка"
        elif position == 1:
            return "Близкий преследователь"
        elif position < total * 0.2:
            return "Верхний сегмент"
        elif position < total * 0.5:
            return "Средний сегмент"
        else:
            return "Нижний сегмент"
    
    def _analyze_comprehensive_competitive_position(self, target_analysis: Dict[str, Any], 
                                              rankings: List[Dict], 
                                              all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Комплексный анализ конкурентной позиции с исправлением доступа к позиции"""
        if not rankings:
            return {}
        
        target_rank = next((r for r in rankings if r['is_target']), None)
        if not target_rank:
            return {}
        
        # Используем корректное получение позиции
        target_position = target_rank.get('position', 0)
        
        # Находим лидера (не целевого сайта)
        leader = next((r for r in rankings if not r['is_target']), None)
        
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        target_score = target_rank['overall_score']
        avg_score = sum(r['overall_score'] for r in rankings) / len(rankings)
        leader_score = leader['overall_score'] if leader else target_score
        
        # Анализ сильных сторон
        if target_rank['citation_potential'] > avg_score:
            strengths.append("Высокий потенциал цитирования в AI-ответах")
        if target_rank['semantic_density'] > avg_score:
            strengths.append("Отличная семантическая плотность контента")
        if target_rank['clear_answers'] > avg_score:
            strengths.append("Качественные готовые ответы для snippets")
        if target_rank['rag_score'] > avg_score:
            strengths.append("Хорошая оптимизация для RAG-систем")
        
        # Анализ слабых сторон
        if target_rank['citation_potential'] < avg_score:
            weaknesses.append("Низкий потенциал цитирования по сравнению с конкурентами")
        if target_rank['rag_score'] < avg_score:
            weaknesses.append("Слабая оптимизация для RAG-систем")
        if target_rank['semantic_density'] < avg_score:
            weaknesses.append("Недостаточная семантическая плотность")
        
        # Анализ возможностей
        if leader and target_score < leader_score:
            score_gap = leader_score - target_score
            opportunities.append(f"Возможность улучшить оценку на {score_gap:.1f} баллов для достижения лидерства")
        
        # Анализ угроз
        if target_position > len(rankings) * 0.7:
            threats.append("Риск потери позиций в поисковой выдаче AI-систем")
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'opportunities': opportunities,
            'threats': threats,
            'competitive_gap': leader_score - target_score if leader else 0,
            'market_position': self._determine_market_position(target_rank, rankings),
            'improvement_priority': self._determine_improvement_priority(weaknesses, target_rank),
            'target_position': target_position
        }
        
    def _analyze_performance_metrics(self, analysis_results: Dict[str, Any], target_url: str) -> Dict[str, Any]:
        """Анализ ключевых метрик производительности"""
        metrics = {
            'target_performance': {},
            'competitor_averages': {},
            'performance_gaps': {},
            'key_insights': []
        }
        
        if target_url not in analysis_results:
            return metrics
        
        target_data = analysis_results[target_url]
        competitor_data = [data for url, data in analysis_results.items() if url != target_url]
        
        # Метрики целевого сайта
        metrics['target_performance'] = {
            'geo_score': target_data.get('overall_geo_score', 0),
            'citation_potential': target_data.get('citation_potential', 0),
            'semantic_density': target_data.get('semantic_density_score', 0),
            'content_quality': target_data.get('clear_answer_quality', 0),
            'rag_optimization': target_data.get('rag_optimization_score', 0)
        }
        
        # Средние показатели конкурентов
        if competitor_data:
            metrics['competitor_averages'] = {
                'geo_score': sum(d.get('overall_geo_score', 0) for d in competitor_data) / len(competitor_data),
                'citation_potential': sum(d.get('citation_potential', 0) for d in competitor_data) / len(competitor_data),
                'semantic_density': sum(d.get('semantic_density_score', 0) for d in competitor_data) / len(competitor_data),
                'content_quality': sum(d.get('clear_answer_quality', 0) for d in competitor_data) / len(competitor_data),
                'rag_optimization': sum(d.get('rag_optimization_score', 0) for d in competitor_data) / len(competitor_data)
            }
            
            # Расчет разрывов
            target_perf = metrics['target_performance']
            competitor_avg = metrics['competitor_averages']
            
            metrics['performance_gaps'] = {
                metric: target_perf[metric] - competitor_avg[metric]
                for metric in target_perf.keys()
            }
            
            # Ключевые инсайты
            for metric, gap in metrics['performance_gaps'].items():
                if gap > 10:
                    metrics['key_insights'].append(f"📈 Преимущество в {metric}: +{gap:.1f} баллов")
                elif gap < -10:
                    metrics['key_insights'].append(f"📉 Отставание в {metric}: {gap:.1f} баллов")
        
        return metrics
    
    def _analyze_market_position(self, rankings: List[Dict], target_url: str) -> Dict[str, Any]:
        """Анализ рыночной позиции с исправлением доступа к позиции"""
        target_rank = next((r for r in rankings if r['is_target']), None)
        if not target_rank:
            return {}
        
        # Используем корректное получение позиции
        position = target_rank.get('position', 0)
        total = len(rankings)
        
        return {
            'current_position': position,
            'total_competitors': total - 1,
            'market_share_estimate': self._estimate_market_share(position, total),
            'competitive_intensity': self._calculate_competitive_intensity(rankings),
            'growth_potential': self._assess_growth_potential(position, total),
            'strategic_priority': self._determine_strategic_priority(position, total)
        }
    
    def _estimate_market_share(self, position: int, total: int) -> str:
        """Оценка доли рынка на основе позиции"""
        if position == 1:
            return "Лидер рынка (25%+)"
        elif position <= 3:
            return "Значительная доля (15-25%)"
        elif position <= total * 0.3:
            return "Средняя доля (5-15%)"
        else:
            return "Незначительная доля (<5%)"
    
    def _calculate_competitive_intensity(self, rankings: List[Dict]) -> str:
        """Расчет интенсивности конкуренции"""
        if len(rankings) < 3:
            return "Низкая"
        
        score_range = rankings[0]['overall_score'] - rankings[-1]['overall_score']
        if score_range < 20:
            return "Высокая"
        elif score_range < 40:
            return "Средняя"
        else:
            return "Низкая"
    
    def _assess_growth_potential(self, position: int, total: int) -> str:
        """Оценка потенциала роста"""
        if position == 1:
            return "Ограниченный - поддержание лидерства"
        elif position <= 3:
            return "Высокий - возможность стать лидером"
        elif position <= total * 0.5:
            return "Средний - постепенное улучшение"
        else:
            return "Критический - необходимо существенное улучшение"
    
    def _determine_strategic_priority(self, position: int, total: int) -> str:
        """Определение стратегического приоритета"""
        if position == 1:
            return "Защита позиций и инновации"
        elif position <= 3:
            return "Атака на лидера"
        elif position <= total * 0.5:
            return "Консолидация и рост"
        else:
            return "Выживание и фундаментальные улучшения"
    
    def _analyze_improvement_potential(self, target_analysis: Dict[str, Any], rankings: List[Dict]) -> Dict[str, Any]:
        """Анализ потенциала улучшений"""
        target_rank = next((r for r in rankings if r['is_target']), None)
        if not target_rank:
            return {}
        
        leader = next((r for r in rankings if not r['is_target']), None)
        
        return {
            'immediate_improvements': self._identify_immediate_improvements(target_analysis),
            'strategic_improvements': self._identify_strategic_improvements(target_rank, leader),
            'quick_wins': self._identify_quick_wins(target_analysis),
            'long_term_initiatives': self._identify_long_term_initiatives(target_rank, leader),
            'estimated_impact': self._estimate_improvement_impact(target_rank, leader)
        }
    
    def _identify_immediate_improvements(self, target_analysis: Dict[str, Any]) -> List[str]:
        """Определение немедленных улучшений"""
        improvements = []
        
        # Анализ на основе данных целевого сайта
        if target_analysis.get('citation_potential', 0) < 70:
            improvements.append("Увеличить количество clear answers и структурированных данных")
        
        if target_analysis.get('semantic_density_score', 0) < 65:
            improvements.append("Улучшить семантическую плотность через углубление тематики")
        
        if target_analysis.get('rag_optimization_score', 0) < 60:
            improvements.append("Оптимизировать контент для RAG-систем")
        
        return improvements[:3]  # Ограничиваем тремя наиболее важными
    
    def _identify_strategic_improvements(self, target_rank: Dict, leader: Dict) -> List[str]:
        """Определение стратегических улучшений"""
        improvements = []
        
        if leader:
            gap = leader['overall_score'] - target_rank['overall_score']
            if gap > 20:
                improvements.append(f"Разработать комплексную стратегию улучшения GEO-показателей (разрыв: {gap:.1f} баллов)")
        
        if target_rank['performance_tier'] in ["Требует улучшений", "Отстающий"]:
            improvements.append("Провести полный аудит и редизайн контентной стратегии")
        
        return improvements
    
    def _identify_quick_wins(self, target_analysis: Dict[str, Any]) -> List[str]:
        """Определение быстрых побед"""
        quick_wins = []
        
        # Проверяем наличие простых для исправления проблем
        llm_analysis = target_analysis.get('llm_analysis', {})
        if llm_analysis:
            recommendations = llm_analysis.get('geo_recommendations', [])
            # Ищем рекомендации, которые можно быстро реализовать
            quick_keywords = ['добавить', 'увеличить', 'исправить', 'оптимизировать']
            for rec in recommendations:
                if any(keyword in rec.lower() for keyword in quick_keywords):
                    if len(rec) < 100:  # Короткие рекомендации обычно проще реализовать
                        quick_wins.append(rec)
        
        return quick_wins[:5]  # Ограничиваем пятью
    
    def _identify_long_term_initiatives(self, target_rank: Dict, leader: Dict) -> List[str]:
        """Определение долгосрочных инициатив"""
        initiatives = []
        
        if target_rank['performance_tier'] != "Лидер":
            initiatives.append("Внедрение AI-оптимизированной контентной стратегии")
            initiatives.append("Разработка системы постоянного мониторинга GEO-метрик")
            initiatives.append("Создание центра компетенций по генеративному поиску")
        
        return initiatives
    
    def _estimate_improvement_impact(self, target_rank: Dict, leader: Dict) -> Dict[str, Any]:
        """Оценка влияния улучшений"""
        if not leader:
            return {}
        
        current_score = target_rank['overall_score']
        leader_score = leader['overall_score']
        gap = leader_score - current_score
        
        return {
            'current_position': f"{current_score:.1f}/100",
            'leader_score': f"{leader_score:.1f}/100",
            'performance_gap': f"{gap:.1f} баллов",
            'estimated_improvement_timeline': self._estimate_timeline(gap),
            'potential_position_improvement': self._estimate_position_improvement(current_score, leader_score),
            'roi_estimate': self._estimate_roi(gap)
        }
    
    def _estimate_timeline(self, gap: float) -> str:
        """Оценка временных рамок для улучшений"""
        if gap < 10:
            return "1-2 месяца"
        elif gap < 25:
            return "3-6 месяцев"
        elif gap < 40:
            return "6-12 месяцев"
        else:
            return "Более 1 года"
    
    def _estimate_position_improvement(self, current_score: float, leader_score: float) -> str:
        """Оценка улучшения позиции"""
        improvement = (leader_score - current_score) / 10  # Упрощенная оценка
        if improvement >= 3:
            return "Значительное улучшение позиций"
        elif improvement >= 1.5:
            return "Умеренное улучшение"
        else:
            return "Незначительное изменение"
    
    def _estimate_roi(self, gap: float) -> str:
        """Оценка возврата инвестиций"""
        if gap < 15:
            return "Высокий ROI - быстрая окупаемость"
        elif gap < 30:
            return "Средний ROI - умеренная окупаемость"
        else:
            return "Низкий ROI - долгосрочные инвестиции"
    
    def _create_detailed_comparison_matrix(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Создание детальной матрицы сравнения"""
        comparison = {
            'metrics_comparison': {},
            'category_breakdown': {},
            'competitive_advantages': {},
            'benchmark_analysis': {}
        }
        
        # Сравнение метрик
        metrics = ['overall_geo_score', 'citation_potential', 'semantic_density_score', 
                  'clear_answer_quality', 'rag_optimization_score']
        
        for metric in metrics:
            comparison['metrics_comparison'][metric] = {}
            for url, analysis in analysis_results.items():
                if metric in analysis:
                    comparison['metrics_comparison'][metric][url] = analysis[metric]
                elif 'llm_analysis' in analysis and metric in analysis['llm_analysis']:
                    comparison['metrics_comparison'][metric][url] = analysis['llm_analysis'][metric]
        
        # Анализ конкурентных преимуществ
        for url, analysis in analysis_results.items():
            advantages = []
            disadvantages = []
            
            for other_url, other_analysis in analysis_results.items():
                if url != other_url:
                    # Сравниваем метрики
                    url_score = analysis.get('overall_geo_score', 0)
                    other_score = other_analysis.get('overall_geo_score', 0)
                    
                    if url_score > other_score + 10:
                        advantages.append(f"Преимущество перед {other_url}: +{url_score - other_score:.1f} баллов")
                    elif url_score < other_score - 10:
                        disadvantages.append(f"Отставание от {other_url}: {other_score - url_score:.1f} баллов")
            
            comparison['competitive_advantages'][url] = {
                'advantages': advantages[:3],  # Ограничиваем тремя
                'disadvantages': disadvantages[:3]
            }
        
        # Бенчмарк-анализ
        if len(analysis_results) > 1:
            scores = [analysis.get('overall_geo_score', 0) for analysis in analysis_results.values()]
            comparison['benchmark_analysis'] = {
                'industry_average': sum(scores) / len(scores),
                'industry_leader': max(scores),
                'performance_benchmark': self._calculate_performance_benchmark(scores),
                'gap_analysis': self._perform_gap_analysis(scores)
            }
        
        return comparison
    
    def _calculate_performance_benchmark(self, scores: List[float]) -> Dict[str, float]:
        """Расчет бенчмарков производительности"""
        return {
            'excellent_threshold': max(scores) * 0.9,  # 90% от лидера
            'good_threshold': sum(scores) / len(scores),  # Среднее по отрасли
            'poor_threshold': min(scores) * 1.1  # На 10% лучше худшего
        }
    
    def _perform_gap_analysis(self, scores: List[float]) -> Dict[str, Any]:
        """Анализ разрывов"""
        sorted_scores = sorted(scores, reverse=True)
        return {
            'leader_gap': sorted_scores[0] - sorted_scores[1] if len(sorted_scores) > 1 else 0,
            'average_gap': sorted_scores[0] - (sum(scores) / len(scores)),
            'competitive_range': sorted_scores[0] - sorted_scores[-1]
        }
    
    def _determine_improvement_priority(self, weaknesses: List[str], target_rank: Dict) -> List[str]:
        """Определение приоритетов улучшений"""
        priorities = []
        
        # Приоритет на основе слабых сторон
        weakness_priority = {
            'цитирования': 'Высокий',
            'RAG': 'Высокий', 
            'семантическая': 'Средний',
            'структур': 'Средний',
            'техническ': 'Низкий'
        }
        
        for weakness in weaknesses:
            for key, priority in weakness_priority.items():
                if key in weakness.lower():
                    priorities.append(f"{priority}: {weakness}")
                    break
        
        # Приоритет на основе позиции
        if target_rank['performance_tier'] in ["Требует улучшений", "Отстающий"]:
            priorities.append("Критический: Фундаментальное улучшение GEO-оптимизации")
        
        return priorities[:5]  # Ограничиваем пятью приоритетами
    
    def _generate_comprehensive_summary(self, comparative_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация комплексной сводки анализа"""
        target_ranking = comparative_analysis.get('target_ranking', {})
        performance_metrics = comparative_analysis.get('performance_metrics', {})
        market_position = comparative_analysis.get('market_position_analysis', {})
        improvement_potential = comparative_analysis.get('improvement_potential', {})
        
        return {
            'overall_assessment': self._generate_overall_assessment(target_ranking),
            'key_findings': self._extract_key_findings(comparative_analysis),
            'strategic_implications': self._derive_strategic_implications(market_position),
            'action_plan': self._create_action_plan(improvement_potential),
            'success_metrics': self._define_success_metrics(performance_metrics),
            'risk_assessment': self._assess_risks(market_position, improvement_potential)
        }
    
    def _generate_overall_assessment(self, target_ranking: Dict[str, Any]) -> str:
        """Генерация общей оценки"""
        position = target_ranking.get('position', 'N/A')
        total = target_ranking.get('total_sites', 0)
        percentile = target_ranking.get('percentile', 0)
        level = target_ranking.get('competitive_level', 'N/A')
        
        if position == 1:
            return f"🎯 Лидирующая позиция на рынке ({position}/{total}, {percentile:.1f}% перцентиль)"
        elif position <= 3:
            return f"📈 Сильная конкурентная позиция ({position}/{total}, {percentile:.1f}% перцентиль)"
        elif position <= total * 0.5:
            return f"📊 Средняя позиция с потенциалом роста ({position}/{total}, {percentile:.1f}% перцентиль)"
        else:
            return f"⚠️ Требует значительных улучшений ({position}/{total}, {percentile:.1f}% перцентиль)"
    
    def _extract_key_findings(self, comparative_analysis: Dict[str, Any]) -> List[str]:
        """Извлечение ключевых находок"""
        findings = []
        
        # Позиционирование
        position = comparative_analysis['target_ranking']['position']
        total = comparative_analysis['target_ranking']['total_sites']
        findings.append(f"Текущая позиция: {position} из {total} сайтов")
        
        # Сильные стороны
        strengths = comparative_analysis['strengths_weaknesses'].get('strengths', [])
        if strengths:
            findings.append(f"Ключевые преимущества: {', '.join(strengths[:2])}")
        
        # Слабые стороны
        weaknesses = comparative_analysis['strengths_weaknesses'].get('weaknesses', [])
        if weaknesses:
            findings.append(f"Основные проблемы: {', '.join(weaknesses[:2])}")
        
        # Разрыв с лидером
        gap = comparative_analysis['strengths_weaknesses'].get('competitive_gap', 0)
        if gap > 0:
            findings.append(f"Разрыв с лидером: {gap:.1f} баллов")
        
        return findings
    
    def _derive_strategic_implications(self, market_position: Dict[str, Any]) -> List[str]:
        """Вывод стратегических импликаций"""
        implications = []
        
        priority = market_position.get('strategic_priority', '')
        growth_potential = market_position.get('growth_potential', '')
        intensity = market_position.get('competitive_intensity', '')
        
        implications.append(f"Стратегический приоритет: {priority}")
        implications.append(f"Потенциал роста: {growth_potential}")
        implications.append(f"Интенсивность конкуренции: {intensity}")
        
        return implications
    
    def _create_action_plan(self, improvement_potential: Dict[str, Any]) -> Dict[str, Any]:
        """Создание плана действий"""
        return {
            'immediate_actions': improvement_potential.get('immediate_improvements', []),
            'quick_wins': improvement_potential.get('quick_wins', []),
            'strategic_initiatives': improvement_potential.get('strategic_improvements', []),
            'long_term_goals': improvement_potential.get('long_term_initiatives', []),
            'implementation_timeline': improvement_potential.get('estimated_impact', {}).get('estimated_improvement_timeline', '')
        }
    
    def _define_success_metrics(self, performance_metrics: Dict[str, Any]) -> List[str]:
        """Определение метрик успеха"""
        metrics = []
        
        gaps = performance_metrics.get('performance_gaps', {})
        for metric, gap in gaps.items():
            if gap > 0:
                metrics.append(f"Увеличить преимущество в {metric}")
            else:
                metrics.append(f"Сократить отставание в {metric}")
        
        return metrics[:3]  # Ограничиваем тремя
    
    def _assess_risks(self, market_position: Dict[str, Any], improvement_potential: Dict[str, Any]) -> List[str]:
        """Оценка рисков"""
        risks = []
        
        position = market_position.get('current_position', 0)
        total = market_position.get('total_competitors', 0) + 1
        
        if position > total * 0.7:
            risks.append("Высокий риск потери видимости в AI-поиске")
        
        if improvement_potential.get('estimated_impact', {}).get('roi_estimate', '').startswith('Низкий'):
            risks.append("Низкая окупаемость инвестиций в улучшения")
        
        intensity = market_position.get('competitive_intensity', '')
        if intensity == 'Высокая':
            risks.append("Высокая конкурентная напряженность требует постоянных улучшений")
        
        return risks
    
    def _generate_executive_summary(self, comparative_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация исполнительного резюме"""
        return {
            'overview': self._create_executive_overview(comparative_analysis),
            'competitive_position': self._summarize_competitive_position(comparative_analysis),
            'key_recommendations': self._prioritize_recommendations(comparative_analysis),
            'expected_outcomes': self._project_expected_outcomes(comparative_analysis),
            'next_steps': self._define_next_steps(comparative_analysis)
        }
    
    def _create_executive_overview(self, comparative_analysis: Dict[str, Any]) -> str:
        """Создание обзора для руководства"""
        target_ranking = comparative_analysis['target_ranking']
        position = target_ranking['position']
        total = target_ranking['total_sites']
        level = target_ranking['competitive_level']
        
        return f"""
        Анализ выявил, что целевой сайт занимает {position}-ю позицию из {total} проанализированных 
        конкурентов, что соответствует уровню '{level}'. Основные возможности для улучшения включают 
        оптимизацию для генеративного поиска и усиление конкурентных преимуществ.
        """
    
    def _summarize_competitive_position(self, comparative_analysis: Dict[str, Any]) -> str:
        """Резюме конкурентной позиции"""
        swot = comparative_analysis['strengths_weaknesses']
        strengths_count = len(swot.get('strengths', []))
        weaknesses_count = len(swot.get('weaknesses', []))
        gap = swot.get('competitive_gap', 0)
        
        return f"""
        Сильные стороны: {strengths_count} обнаружено
        Области улучшения: {weaknesses_count} выявлено
        Разрыв с лидером: {gap:.1f} баллов
        """
    
    def _prioritize_recommendations(self, comparative_analysis: Dict[str, Any]) -> List[str]:
        """Приоритизация рекомендаций"""
        recommendations = comparative_analysis.get('strategic_recommendations', [])
        improvement = comparative_analysis.get('improvement_potential', {})
        quick_wins = improvement.get('quick_wins', [])
        
        # Объединяем и приоритизируем
        all_recs = quick_wins[:2] + recommendations[:3]  # 2 быстрых победы + 3 стратегических
        return all_recs
    
    def _project_expected_outcomes(self, comparative_analysis: Dict[str, Any]) -> List[str]:
        """Проекция ожидаемых результатов"""
        outcomes = []
        target_ranking = comparative_analysis['target_ranking']
        position = target_ranking['position']
        total = target_ranking['total_sites']
        
        if position > 1:
            outcomes.append(f"Возможность подняться на {min(3, position-1)} позицию в рейтинге")
        
        improvement = comparative_analysis.get('improvement_potential', {})
        impact = improvement.get('estimated_impact', {})
        timeline = impact.get('estimated_improvement_timeline', '')
        
        if timeline:
            outcomes.append(f"Заметные улучшения ожидаются через {timeline}")
        
        return outcomes
    
    def _define_next_steps(self, comparative_analysis: Dict[str, Any]) -> List[str]:
        """Определение следующих шагов"""
        return [
            "Разработать детальный план реализации рекомендаций",
            "Назначить ответственных за каждое направление улучшений",
            "Установить KPI для отслеживания прогресса",
            "Запланировать повторный анализ через 3 месяца"
        ]

    def _fetch_content_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Получение базовых данных контента для LLM-анализа"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_data = {
                'basic_info': {
                    'url': url,
                    'title': soup.title.string if soup.title else 'Не найден',
                    'status_code': response.status_code
                },
                'metadata': {
                    'title': {
                        'value': soup.title.string if soup.title else None,
                        'length': len(soup.title.string) if soup.title else 0
                    },
                    'description': {
                        'value': soup.find('meta', attrs={'name': 'description'}).get('content') 
                                 if soup.find('meta', attrs={'name': 'description'}) else None
                    }
                },
                'content_structure': {
                    'readability_sample_text': self._extract_clean_text_for_llm(soup)
                }
            }
            
            return content_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения данных для {url}: {str(e)}")
            return None

    def _extract_clean_text_for_llm(self, soup):
        """Извлечение чистого текста для LLM-анализа"""
        for script in soup(["script", "style"]):
            script.decompose()
        
        content_areas = soup.find_all(['main', 'article', 'section', 'div'], 
                                    class_=re.compile(r'content|main|article', re.I))
        
        if content_areas:
            text_parts = []
            for area in content_areas[:3]:
                text = area.get_text(strip=True)
                if len(text) > 100:
                    text_parts.append(text)
            
            if text_parts:
                return ' '.join(text_parts)[:3000]
        
        return soup.get_text(strip=True)[:3000]

    def _find_competitors_with_deepseek(self, target_url: str, max_competitors: int = 5) -> List[str]:
        """Поиск конкурентов/аналогичных сайтов через DeepSeek"""
        try:
            cache_key = f"competitors_{target_url}"
            if cache_key in self.competitor_cache:
                return self.competitor_cache[cache_key][:max_competitors]
            
            prompt = f"""
            Ты - эксперт по анализу веб-сайтов и поисковой оптимизации. 
            Найди {max_competitors} сайтов-конкурентов или аналогичных по тематике веб-ресурсов для: {target_url}

            Критерии поиска:
            - Схожая тематика и ниша
            - Сопоставимый масштаб и аудитория
            - Релевантные аналоги по содержанию
            - Известные сайты в той же области

            ВАЖНО: Верни ТОЛЬКО JSON массив с URL в формате:
            ["url1", "url2", "url3", ...]

            Не добавляй никакого дополнительного текста, только чистый JSON.
            """
            
            completion = self.client.chat.completions.create(
                model=self.llm_models['deepseek'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
        
            response_text = completion.choices[0].message.content
            
            try:
                competitors = json.loads(response_text)
                if isinstance(competitors, list) and all(isinstance(url, str) for url in competitors):
                    self.competitor_cache[cache_key] = competitors
                    return competitors[:max_competitors]
            except json.JSONDecodeError:
                urls = re.findall(r'https?://[^\s"\']+', response_text)
                self.competitor_cache[cache_key] = urls
                return urls[:max_competitors]
                
            return []
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска конкурентов: {str(e)}")
            return []

    def _determine_market_position(self, target_rank: Dict, rankings: List[Dict]) -> str:
        """Определение рыночной позиции"""
        position = next((i for i, r in enumerate(rankings) if r['is_target']), -1)
        total = len(rankings)
        
        if position == 0:
            return "Лидер рынка"
        elif position == 1:
            return "Близкий преследователь"
        elif position < total * 0.3:
            return "Верхний сегмент"
        elif position < total * 0.7:
            return "Средний сегмент"
        else:
            return "Нижний сегмент"

    def _generate_strategic_recommendations(self, comparative: Dict[str, Any], 
                                          analysis_results: Dict[str, Any]) -> List[str]:
        """Генерация стратегических рекомендаций"""
        recommendations = []
        target_url = comparative['target_url']
        
        if target_url not in analysis_results:
            return recommendations
        
        target_analysis = analysis_results[target_url]
        competitive_analysis = comparative['strengths_weaknesses']
        
        position = comparative['target_ranking']['position']
        total = comparative['target_ranking']['total_sites']
        
        if position == 1:
            recommendations.append("Укрепляйте лидирующие позиции через инновации в GEO-оптимизации")
            recommendations.append("Экспериментируйте с новыми форматами контента для AI")
        elif position <= 3:
            recommendations.append(f"Сфокусируйтесь на преодолении разрыва с лидером ({competitive_analysis.get('competitive_gap', 0):.1f} баллов)")
            recommendations.append("Проанализируйте лучшие практики топ-конкурентов")
        else:
            recommendations.append("Приоритет: улучшение базовых показателей GEO-оптимизации")
            recommendations.append("Изучите и внедрите подходы сайтов из верхнего сегмента")
        
        weaknesses = competitive_analysis.get('weaknesses', [])
        if any("цитирования" in weakness.lower() for weakness in weaknesses):
            recommendations.append("Увеличьте количество clear answers и структурированных данных")
        if any("RAG" in weakness for weakness in weaknesses):
            recommendations.append("Оптимизируйте контент для Retrieval-Augmented Generation систем")
        if any("семантическая" in weakness.lower() for weakness in weaknesses):
            recommendations.append("Улучшите семантическую плотность через углубление тематики")
        
        recommendations.extend([
            "Регулярно мониторьте GEO-показатели конкурентов",
            "Адаптируйте контент-стратегию под особенности разных LLM",
            "Внедряйте A/B тестирование для GEO-элементов"
        ])
        
        return recommendations

    def _get_deep_fallback_analysis(self, target_url: str, error_msg: str) -> Dict[str, Any]:
        """Fallback для глубокого анализа"""
        return {
            'target_url': target_url,
            'competitors_analyzed': 0,
            'ranking': [],
            'competitive_analysis': {},
            'strengths_weaknesses': {},
            'strategic_recommendations': [
                "Не удалось выполнить полный анализ конкурентов",
                "Проверьте доступность целевого URL",
                "Убедитесь в стабильности подключения к LLM API"
            ],
            'error': error_msg,
            'fallback_analysis': True
        }

    def clear_cache(self):
        """Очистка кэшей анализатора"""
        self.competitor_cache.clear()
        self.comparative_analysis_cache.clear()
        self.analysis_cache.clear()
        logger.info("🧹 Кэши анализатора очищены")
    
    def _get_fallback_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback анализ при ошибках получения контента"""
        return {
            'overall_geo_score': 50,
            'citation_potential': 50,
            'semantic_density_score': 50,
            'clear_answer_quality': 50,
            'rag_optimization_score': 50,
            'category_scores': {
                'citation': 50,
                'semantic': 50,
                'structure': 50,
                'technical': 50,
                'rag': 50
            },
            'fallback_analysis': True,
            'error': 'Не удалось получить полный анализ контента'
        }