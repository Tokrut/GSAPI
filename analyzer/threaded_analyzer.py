"""
Многопоточный анализатор для параллельного выполнения анализа
"""

import threading
import concurrent.futures
import time
from typing import Dict, List, Any, Callable, Optional
from queue import Queue
import logging
from datetime import datetime

from .enhanced_analyzer import EnhancedWebsiteAnalyzer
from .llm_analyzer import LLMAnalyzer
from .deep_llm_analyzer import DeepLLMAnalyzer
from .base_analyzer import WebsiteAnalyzer
from config import ANALYSIS_CONFIG

logger = logging.getLogger(__name__)


class ThreadedWebsiteAnalyzer:
    """Многопоточный анализатор сайтов"""
    
    def __init__(self, max_workers: int = 5, enable_llm_analysis: bool = True, 
                 enable_deep_analysis: bool = False):
        self.max_workers = max_workers
        self.enable_llm_analysis = enable_llm_analysis
        self.enable_deep_analysis = enable_deep_analysis
        
        # Очередь для отслеживания прогресса
        self.progress_queue = Queue()
        
    def analyze_multiple_urls(self, urls: List[str], callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Параллельный анализ нескольких URL"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(urls), self.max_workers)) as executor:
            # Создаем задачи для каждого URL
            future_to_url = {
                executor.submit(self._analyze_single_url, url): url 
                for url in urls
            }
            
            # Обрабатываем результаты по мере их готовности
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=ANALYSIS_CONFIG['timeout'] * 2)
                    results[url] = result
                    
                    # Вызываем callback для обновления прогресса
                    if callback:
                        callback({
                            'url': url,
                            'status': 'completed',
                            'result': result,
                            'completed_count': len(results),
                            'total_count': len(urls)
                        })
                        
                except Exception as e:
                    logger.error(f"Ошибка анализа {url}: {e}")
                    results[url] = {'error': str(e)}
                    
                    if callback:
                        callback({
                            'url': url,
                            'status': 'error',
                            'error': str(e),
                            'completed_count': len(results),
                            'total_count': len(urls)
                        })
        
        return results
    
    def parallel_llm_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Параллельный LLM-анализ с использованием нескольких моделей"""
        if not self.enable_llm_analysis:
            return {}
            
        llm_analyzer = LLMAnalyzer()
        
        # Используем встроенную параллельную обработку из LLM-анализатора
        return llm_analyzer.analyze_content_for_geo(content_data)
    
    def deep_analyze_with_competitors_threaded(self, target_url: str, 
                                              max_competitors: int = 3) -> Dict[str, Any]:
        """Многопоточный глубокий анализ с конкурентами"""
        if not self.enable_deep_analysis:
            return {
                'error': 'Deep анализ отключен',
                'target_url': target_url,
                'competitors_analyzed': 0
            }
        
        try:
            # Прямой вызов глубокого анализа с конкурентами
            deep_analyzer = DeepLLMAnalyzer()
            
            # Выполняем глубокий анализ
            deep_result = deep_analyzer.deep_analyze_with_competitors(target_url, max_competitors)
            
            # Базовый анализ целевого сайта для объединения
            base_analyzer = EnhancedWebsiteAnalyzer(
                enable_llm_analysis=self.enable_llm_analysis,
                enable_deep_analysis=False  # Отключаем рекурсивный глубокий анализ
            )
            base_result = base_analyzer.analyze_url(target_url)
            
            # Объединяем результаты
            if base_result and 'error' not in base_result:
                result = base_result
                result['deep_analysis'] = deep_result
            else:
                # Если базовый анализ не удался, используем результат глубокого анализа
                result = deep_result
                result['basic_analysis'] = {'error': 'Base analysis failed'} if not base_result else base_result
            
            result['timestamp'] = time.time()
            result['target_url'] = target_url
            result['analysis_method'] = 'threaded_deep_analysis'
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка глубокого анализа: {e}")
            return {
                'error': str(e),
                'target_url': target_url,
                'competitors_analyzed': 0
            }
    
    def _analyze_single_url(self, url: str) -> Dict[str, Any]:
        """Анализ одного URL (используется в пуле потоков)"""
        try:
            # Создаем экземпляр анализатора для каждого потока для thread-safety
            thread_analyzer = EnhancedWebsiteAnalyzer(
                enable_llm_analysis=self.enable_llm_analysis,
                enable_deep_analysis=False  # Отключаем глубокий анализ в отдельных потоках
            )
            return thread_analyzer.analyze_url(url)
        except Exception as e:
            logger.error(f"Ошибка анализа {url}: {e}")
            return {'error': str(e)}
            
    def analyze_with_progress(self, url: str, use_selenium: bool = False,
                            enable_deep_analysis: bool = False,
                            progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Анализ с отслеживанием прогресса"""

        def update_progress(step: str, percentage: int, message: str = ""):
            if progress_callback:
                progress_callback({
                    'step': step,
                    'percentage': percentage,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
        
        try:
            update_progress('initializing', 0, "Инициализация анализатора...")
            
            if enable_deep_analysis:
                # Глубокий анализ с конкурентами
                update_progress('deep_analysis', 30, "Поиск и анализ конкурентов...")
                result = self.deep_analyze_with_competitors_threaded(url, max_competitors=3)
            else:
                # Базовый анализ
                analyzer = EnhancedWebsiteAnalyzer(
                    use_selenium=use_selenium,
                    enable_llm_analysis=self.enable_llm_analysis,
                    enable_deep_analysis=False
                )
                
                update_progress('basic_analysis', 20, "Выполнение базового анализа...")
                result = analyzer.analyze_url(url)
                update_progress('basic_complete', 50, "Базовый анализ завершен")
                
                # Параллельный LLM-анализ если включен
                if self.enable_llm_analysis and result and 'error' not in result:
                    update_progress('llm_analysis', 70, "Запуск AI-анализа...")
                    llm_result = self.parallel_llm_analysis(result)
                    result['llm_analysis'] = llm_result
                    update_progress('llm_complete', 90, "AI-анализ завершен")
            
            update_progress('finalizing', 95, "Формирование отчета...")
            
            # Добавляем метаданные
            if result and 'error' not in result:
                result['analysis_method'] = 'threaded'
                result['thread_count'] = self.max_workers
                result['analysis_time'] = datetime.now().isoformat()
            
            update_progress('completed', 100, "Анализ завершен!")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка в analyze_with_progress: {e}")
            update_progress('error', 100, f"Ошибка анализа: {str(e)}")
            return {'error': str(e)}


class BatchAnalysisManager:
    """Менеджер пакетного анализа"""
    
    def __init__(self, max_concurrent_analyses: int = 3):
        self.max_concurrent_analyses = max_concurrent_analyses
        self.active_analyses = {}
        
    def start_batch_analysis(self, urls: List[str], 
                           analysis_config: Dict[str, Any] = None) -> str:
        """Запуск пакетного анализа"""
        batch_id = f"batch_{int(time.time())}"
        
        # Конфигурация по умолчанию
        if analysis_config is None:
            analysis_config = {
                'enable_llm_analysis': True,
                'enable_deep_analysis': False,
                'use_selenium': False
            }
        
        # Запускаем анализ в отдельном потоке
        def run_batch_analysis():
            analyzer = ThreadedWebsiteAnalyzer(
                max_workers=self.max_concurrent_analyses,
                enable_llm_analysis=analysis_config['enable_llm_analysis'],
                enable_deep_analysis=analysis_config['enable_deep_analysis']
            )
            
            def batch_callback(progress_data):
                # Обновляем прогресс в основном состоянии
                if batch_id in self.active_analyses:
                    self.active_analyses[batch_id]['progress'] = progress_data
            
            results = analyzer.analyze_multiple_urls(urls, batch_callback)
            
            # Сохраняем результаты
            self.active_analyses[batch_id] = {
                'status': 'completed',
                'results': results,
                'completed_at': datetime.now().isoformat(),
                'total_urls': len(urls),
                'successful_analyses': len([r for r in results.values() if 'error' not in r])
            }
        
        # Запускаем в отдельном потоке
        thread = threading.Thread(target=run_batch_analysis)
        thread.daemon = True
        thread.start()
        
        # Сохраняем информацию о запущенном анализе
        self.active_analyses[batch_id] = {
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'total_urls': len(urls),
            'urls': urls,
            'config': analysis_config,
            'progress': None
        }
        
        return batch_id
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Получить статус пакетного анализа"""
        return self.active_analyses.get(batch_id, {'error': 'Batch not found'})
    
    def get_batch_results(self, batch_id: str) -> Dict[str, Any]:
        """Получить результаты пакетного анализа"""
        batch = self.active_analyses.get(batch_id)
        if batch and batch['status'] == 'completed':
            return batch['results']
        return {'error': 'Analysis not completed or not found'}
    
    def cancel_batch_analysis(self, batch_id: str) -> bool:
        """Отменить пакетный анализ"""
        if batch_id in self.active_analyses:
            self.active_analyses[batch_id]['status'] = 'cancelled'
            return True
        return False