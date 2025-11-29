"""
Улучшенный анализатор сайта с расширенными функциями
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
import json
import logging
from collections import Counter
import urllib.robotparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

from .base_analyzer import WebsiteAnalyzer
from .llm_analyzer import LLMAnalyzer
from .deep_llm_analyzer import DeepLLMAnalyzer  # Добавляем импорт глубокого LLM анализатора
from config import ANALYSIS_CONFIG, OPTIMAL_VALUES

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')

class EnhancedWebsiteAnalyzer(WebsiteAnalyzer):
    """Улучшенный анализатор с расширенными функциями и LLM-анализом"""
    
    def __init__(self, use_selenium=False, enable_llm_analysis=True, enable_deep_analysis=False):
        super().__init__()
        self.use_selenium = use_selenium
        self.enable_llm_analysis = enable_llm_analysis
        self.enable_deep_analysis = enable_deep_analysis
        self.driver = None
        
        # Инициализация LLM анализатора
        if self.enable_llm_analysis:
            self.llm_analyzer = LLMAnalyzer()
        else:
            self.llm_analyzer = None
        
        # Инициализация Deep LLM анализатора
        if self.enable_deep_analysis:
            self.deep_llm_analyzer = DeepLLMAnalyzer()
        else:
            self.deep_llm_analyzer = None
        
        # Настраиваем повторные попытки
        retry_strategy = Retry(
            total=ANALYSIS_CONFIG['max_retries'],
            status_forcelist=ANALYSIS_CONFIG['retry_status_codes'],
            allowed_methods=["GET", "POST"],
            backoff_factor=ANALYSIS_CONFIG['backoff_factor']
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Дополнительные заголовки
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        if self.use_selenium:
            self._setup_selenium()
            
    def _setup_selenium(self):
        """Настройка Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=' + ANALYSIS_CONFIG['user_agent'])
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(ANALYSIS_CONFIG['timeout'])
        except Exception as e:
            logger.warning(f"Selenium не доступен: {e}")
            self.use_selenium = False
    
    def analyze_url(self, url):
        """Улучшенный метод анализа с валидацией и LLM"""
        # Валидация URL
        if not self._validate_url(url):
            return None
            
        try:
            start_time = time.time()
            
            if self.use_selenium and self.driver:
                response_data = self._analyze_with_selenium(url)
            else:
                response_data = self._analyze_with_requests(url)
            
            if not response_data:
                return None
                
            response, response_time, soup = response_data
            
            # Базовый анализ
            analysis_result = {
                'basic_info': self._get_enhanced_basic_info(soup, url, response, response_time),
                'metadata': self._analyze_enhanced_metadata(soup),
                'semantic_markup': self._analyze_enhanced_semantic_markup(soup),
                'content_structure': self._analyze_enhanced_content_structure(soup),
                'technical_seo': self._analyze_enhanced_technical_seo(soup, url),
                'performance': self._analyze_enhanced_performance(soup, response, response_time),
                'security': self._analyze_security(response, url),
                'accessibility': self._analyze_accessibility(soup),
                'score': 0,
                'warnings': [],
                'critical_issues': [],
                'recommendations': []
            }
            
            # LLM-анализ для GEO
            if self.enable_llm_analysis and self.llm_analyzer:
                try:
                    logger.info("Запуск LLM-анализа для GEO...")
                    llm_analysis = self.llm_analyzer.analyze_content_for_geo(analysis_result)
                    analysis_result['llm_analysis'] = llm_analysis
                    
                    # Интегрируем LLM-рекомендации в общие рекомендации
                    if 'geo_recommendations' in llm_analysis:
                        analysis_result['recommendations'].extend(llm_analysis['geo_recommendations'])
                        
                except Exception as e:
                    logger.error(f"Ошибка LLM-анализа: {e}")
                    analysis_result['llm_analysis'] = {'error': str(e)}
            
            # Добавляем проверки и предупреждения
            analysis_result = self._add_issues_and_warnings(analysis_result)
            
            # Расчет общего скора с учетом LLM-оценки
            analysis_result['score'] = self._calculate_enhanced_score(analysis_result)
            
            # Генерация рекомендаций
            analysis_result['recommendations'] = self._generate_recommendations(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}")
            return None
        finally:
            if self.driver:
                self.driver.quit()
                
    def deep_analyze_with_competitors(self, target_url: str, max_competitors: int = 3) -> dict:
        """Выполняет глубокий анализ с поиском и сравнением конкурентов"""
        if not self.enable_deep_analysis:
            logger.warning("Deep анализ отключен. Включите флаг enable_deep_analysis")
            return {
                'error': 'Deep анализ отключен',
                'target_url': target_url,
                'competitors_analyzed': 0
            }
        
        try:
            logger.info(f"Запуск глубокого анализа с конкурентами для: {target_url}")
            
            # Проверяем, инициализирован ли deep_llm_analyzer
            if not hasattr(self, 'deep_llm_analyzer') or self.deep_llm_analyzer is None:
                logger.warning("Deep LLM анализатор не инициализирован")
                return {
                    'error': 'Deep LLM анализатор не инициализирован',
                    'target_url': target_url
                }
            
            # Выполняем глубокий анализ с конкурентами
            deep_analysis = self.deep_llm_analyzer.deep_analyze_with_competitors(
                target_url=target_url,
                max_competitors=max_competitors
            )
            
            # Выполняем базовый анализ целевого сайта
            base_result = self.analyze_url(target_url)
            
            # Объединяем результаты
            result = {
                'basic_analysis': base_result,
                'deep_analysis': deep_analysis,
                'timestamp': time.time(),
                'target_url': target_url,
                'competitors_count': max_competitors,
                'analysis_method': 'enhanced_deep_analysis'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка глубокого анализа: {e}")
            return {
                'error': str(e),
                'target_url': target_url,
                'competitors_analyzed': 0
            }           
            
    def _analyze_with_requests(self, url):
        """Анализ с использованием requests"""
        try:
            start_time = time.time()
            response = self.session.get(
                url, 
                timeout=ANALYSIS_CONFIG['timeout'], 
                allow_redirects=ANALYSIS_CONFIG['follow_redirects'],
                verify=ANALYSIS_CONFIG['verify_ssl']
            )
            response_time = time.time() - start_time
            
            response.encoding = self._detect_encoding(response)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            return response, response_time, soup
        except Exception as e:
            logger.error(f"Ошибка requests: {e}")
            return None
    
    def _analyze_with_selenium(self, url):
        """Анализ с использованием Selenium для JavaScript-сайтов"""
        try:
            start_time = time.time()
            self.driver.get(url)
            
            # Ожидаем загрузки страницы
            WebDriverWait(self.driver, ANALYSIS_CONFIG['timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            response_time = time.time() - start_time
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Создаем mock response объект
            class MockResponse:
                def __init__(self, text, url, headers):
                    self.text = text
                    self.url = url
                    self.headers = headers
                    self.status_code = 200
            
            response = MockResponse(page_source, url, {})
            return response, response_time, soup
        except Exception as e:
            logger.error(f"Ошибка Selenium: {e}")
            return None
    
    def _validate_url(self, url):
        """Валидация URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _detect_encoding(self, response):
        """Определение кодировки"""
        if response.encoding:
            return response.encoding
        return 'utf-8'
    
    def _get_enhanced_basic_info(self, soup, url, response, response_time):
        """Расширенная базовая информация"""
        basic_info = self._get_basic_info(soup, url, response)
        basic_info.update({
            'response_time': round(response_time, 2),
            'redirects': len(response.history) if hasattr(response, 'history') else 0,
            'final_url': response.url,
            'content_length': len(response.content),
            'is_https': urlparse(url).scheme == 'https',
            'domain': urlparse(url).netloc,
            'protocol': urlparse(url).scheme
        })
        return basic_info
    
    def _analyze_enhanced_metadata(self, soup):
        """Расширенный анализ мета-данных"""
        metadata = self._analyze_metadata(soup)
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        metadata['canonical'] = {
            'exists': canonical is not None,
            'value': canonical.get('href') if canonical else None,
            'self_referencing': canonical and canonical.get('href') and urlparse(canonical.get('href')).path == ''
        }
        
        # Robots meta
        robots = soup.find('meta', attrs={'name': 'robots'})
        metadata['robots'] = {
            'exists': robots is not None,
            'value': robots.get('content') if robots else None,
            'noindex': robots and 'noindex' in (robots.get('content') or '').lower(),
            'nofollow': robots and 'nofollow' in (robots.get('content') or '').lower()
        }
        
        # Viewport
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        metadata['viewport'] = {
            'exists': viewport is not None,
            'value': viewport.get('content') if viewport else None,
            'mobile_friendly': bool(viewport and 'width=device-width' in (viewport.get('content') or ''))
        }
        
        # Charset
        charset = soup.find('meta', attrs={'charset': True})
        if not charset:
            charset = soup.find('meta', attrs={'http-equiv': re.compile('charset', re.I)})
        metadata['charset'] = {
            'exists': charset is not None,
            'value': charset.get('charset') if charset and charset.get('charset') else charset.get('content') if charset else None
        }
        
        # Open Graph расширенный анализ
        og_tags = {}
        for tag in soup.find_all('meta', attrs={'property': re.compile(r'^og:')}):
            prop = tag.get('property')
            content = tag.get('content')
            if prop and content:
                og_tags[prop] = content
        
        metadata['open_graph']['detailed'] = og_tags
        metadata['open_graph']['essential_count'] = len([tag for tag in og_tags.keys() if tag in ['og:title', 'og:description', 'og:image', 'og:url']])
        
        # Twitter Cards
        twitter_tags = {}
        for tag in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')}):
            name = tag.get('name')
            content = tag.get('content')
            if name and content:
                twitter_tags[name] = content
        
        metadata['twitter_cards'] = {
            'exists': len(twitter_tags) > 0,
            'tags': twitter_tags,
            'count': len(twitter_tags)
        }
        
        return metadata
    
    def _analyze_enhanced_semantic_markup(self, soup):
        """Расширенный анализ семантической разметки"""
        semantic = self._analyze_semantic_markup(soup)
        
        # Расширенный анализ Schema.org
        json_ld_parsed = []
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string:
                    data = json.loads(script.string)
                    json_ld_parsed.append(data)
            except json.JSONDecodeError:
                continue
        
        semantic['schema_org']['parsed'] = json_ld_parsed
        semantic['schema_org']['types'] = list(set([item.get('@type', 'Unknown') for item in json_ld_parsed if isinstance(item, dict)]))
        
        # Расширенный анализ микроразметки
        microdata_items = []
        for item in soup.find_all(attrs={'itemtype': True}):
            microdata_items.append({
                'type': item.get('itemtype'),
                'properties': {
                    prop: item.get(prop) for prop in item.attrs if prop.startswith('itemprop')
                }
            })
        
        semantic['microdata']['detailed'] = microdata_items
        
        # Анализ RDFa
        rdfa_elements = soup.find_all(attrs={'property': True})
        semantic['rdfa'] = {
            'elements': len(rdfa_elements),
            'exists': len(rdfa_elements) > 0
        }
        
        # Анализ структуры заголовков
        headings_structure = []
        for i in range(1, 7):
            heading_elements = soup.find_all(f'h{i}')
            for heading in heading_elements:
                headings_structure.append({
                    'level': i,
                    'text': heading.get_text(strip=True),
                    'length': len(heading.get_text(strip=True))
                })
        
        semantic['headings_structure'] = headings_structure
        
        return semantic
    
    def _extract_clean_text_for_llm(self, soup):
        """Извлечение чистого текста для LLM-анализа"""
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Получаем текст основных контентных областей
        content_areas = soup.find_all(['main', 'article', 'section', 'div'], class_=re.compile(r'content|main|article', re.I))
        
        if content_areas:
            # Берем текст из основных контентных областей
            text_parts = []
            for area in content_areas[:3]:  # Ограничиваем количество областей
                text = area.get_text(strip=True)
                if len(text) > 100:  # Только значимые блоки
                    text_parts.append(text)
            
            if text_parts:
                return ' '.join(text_parts)[:3000]  # Ограничиваем общую длину
        
        # Fallback: весь текст страницы
        return soup.get_text(strip=True)[:3000]


    def _analyze_enhanced_content_structure(self, soup):
        """Расширенный анализ структуры контента с извлечением текста для LLM"""
        content = self._analyze_content_structure(soup)
        
        # Улучшенный анализ читаемости
        text_content = soup.get_text()
        words = re.findall(r'\b\w+\b', text_content)
        sentences = re.split(r'[.!?]+', text_content)
        
        # Сохраняем образец текста для LLM-анализа
        content['readability_sample_text'] = self._extract_clean_text_for_llm(soup)
        
        if sentences and words:
            avg_sentence_length = len(words) / len(sentences)
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            
            # Улучшенная оценка читаемости
            readability_score = self._calculate_readability_score(words, sentences, avg_word_length, avg_sentence_length)
            
            content['readability'] = {
                'score': round(readability_score, 2),
                'level': self._get_readability_level(readability_score),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'avg_word_length': round(avg_word_length, 2),
                'words': len(words),
                'sentences': len(sentences),
                'paragraphs': len(soup.find_all('p'))
            }
        
        # Расширенный анализ ключевых слов
        text_lower = text_content.lower()
        common_words = ['и', 'в', 'на', 'с', 'по', 'для', 'не', 'что', 'это', 'как', 'как', 'но', 'а', 'или', 'у', 'о', 'от', 'до', 'из', 'за']
        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in common_words and len(word_lower) > 2 and word_lower.isalpha():
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        
        # Топ 15 самых частых слов
        top_words = Counter(word_freq).most_common(15)
        content['keyword_analysis'] = {
            'top_words': top_words,
            'unique_words': len(word_freq),
            'keyword_density': round((sum(freq for _, freq in top_words) / len(words)) * 100, 2) if words else 0
        }
        
        # Анализ мультимедиа
        videos = soup.find_all('video')
        iframes = soup.find_all('iframe')
        
        content['multimedia'] = {
            'videos': len(videos),
            'iframes': len(iframes),
            'audio': len(soup.find_all('audio'))
        }
        
        # Анализ интерактивных элементов
        content['interactive'] = {
            'forms': len(soup.find_all('form')),
            'buttons': len(soup.find_all('button')),
            'inputs': len(soup.find_all('input'))
        }
        
        return content

    def _analyze_enhanced_technical_seo(self, soup, base_url):
        """Расширенный технический анализ"""
        technical = self._analyze_technical_seo(soup, base_url)
        
        # Улучшенный анализ ссылок
        links = soup.find_all('a', href=True)
        link_analysis = {
            'total': len(links),
            'internal': 0,
            'external': 0,
            'nofollow': 0,
            'dofollow': 0,
            'with_anchor': 0,
            'empty_anchor': 0,
            'anchor_lengths': [],
            'broken_links': 0
        }
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            anchor_text = link.get_text(strip=True)
            
            # Определение типа ссылки
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                link_analysis['internal'] += 1
            else:
                link_analysis['external'] += 1
            
            # Nofollow/dofollow
            if link.get('rel') and 'nofollow' in link.get('rel'):
                link_analysis['nofollow'] += 1
            else:
                link_analysis['dofollow'] += 1
            
            # Anchor text
            if anchor_text:
                link_analysis['with_anchor'] += 1
                link_analysis['anchor_lengths'].append(len(anchor_text))
            else:
                link_analysis['empty_anchor'] += 1
        
        technical['enhanced_links'] = link_analysis
        
        # Анализ изображений
        images = soup.find_all('img')
        image_analysis = {
            'total': len(images),
            'with_alt': len([img for img in images if img.get('alt')]),
            'with_src': len([img for img in images if img.get('src')]),
            'lazy_loaded': len([img for img in images if 'loading' in img.attrs and img['loading'] == 'lazy']),
            'responsive': len([img for img in images if 'srcset' in img.attrs]),
            'average_size': 0  # Можно добавить анализ размеров
        }
        
        technical['images_analysis'] = image_analysis
        
        # Проверка основных технических теги
        technical['important_tags'] = {
            'canonical': bool(soup.find('link', rel='canonical')),
            'robots_txt': self._check_robots_txt(base_url),
            'sitemap': self._check_sitemap(base_url),
            'favicon': bool(soup.find('link', rel=re.compile('icon', re.I))),
            'manifest': bool(soup.find('link', rel='manifest')),
            'amp_html': bool(soup.find('link', rel='amphtml'))
        }
        
        # Анализ структуры URL
        technical['url_structure'] = {
            'depth': len([p for p in urlparse(base_url).path.split('/') if p]),
            'has_trailing_slash': base_url.endswith('/'),
            'has_uppercase': any(c.isupper() for c in urlparse(base_url).path),
            'has_parameters': bool(urlparse(base_url).query)
        }
        
        return technical
    
    def _analyze_enhanced_performance(self, soup, response, response_time):
        """Расширенный анализ производительности"""
        # Сначала получаем базовые данные производительности
        performance_data = {
            'response_time': response_time,
            'page_size': len(response.content) if hasattr(response, 'content') else 0,
            'html_size': len(str(soup)),
            'image_count': len(soup.find_all('img')),
            'script_count': len(soup.find_all('script')),
            'stylesheet_count': len(soup.find_all('link', rel='stylesheet'))
        }
        
        # Дополнительные метрики производительности
        html_complexity = len(str(soup))
        dom_elements = len(soup.find_all())
        
        performance_data.update({
            'html_complexity': html_complexity,
            'dom_elements': dom_elements,
            'dom_depth': self._calculate_dom_depth(soup),
            'resource_requests': len(soup.find_all(['img', 'script', 'link'])),
            'inline_styles': len(soup.find_all(style=True)),
            'external_scripts': len(soup.find_all('script', src=True)),
            'inline_scripts': len([script for script in soup.find_all('script') if script.string and not script.get('src')])
        })
        
        # Оценка производительности
        performance_score = self._calculate_performance_score(performance_data)
        performance_data['score'] = performance_score
        performance_data['level'] = self._get_performance_level(performance_score)
        
        return performance_data
    
    def _analyze_security(self, response, url):
        """Анализ безопасности"""
        security = {}
        
        # HTTPS и сертификаты
        security['https'] = {
            'enabled': urlparse(url).scheme == 'https',
            'mixed_content': self._check_mixed_content(response.text) if hasattr(response, 'text') else False
        }
        
        # Заголовки безопасности
        headers = response.headers if hasattr(response, 'headers') else {}
        security['headers'] = {
            'hsts': 'strict-transport-security' in headers,
            'x_frame_options': 'x-frame-options' in headers,
            'x_content_type_options': 'x-content-type-options' in headers,
            'x_xss_protection': 'x-xss-protection' in headers,
            'content_security_policy': 'content-security-policy' in headers,
            'referrer_policy': 'referrer-policy' in headers
        }
        
        return security
    
    def _analyze_accessibility(self, soup):
        """Анализ доступности"""
        accessibility = {}
        
        # ARIA атрибуты
        aria_elements = soup.find_all(attrs={'aria-label': True})
        accessibility['aria'] = {
            'labels': len(aria_elements),
            'roles': len(soup.find_all(attrs={'role': True})),
            'describedby': len(soup.find_all(attrs={'aria-describedby': True}))
        }
        
        # Семантические HTML5 теги
        semantic_tags = ['header', 'footer', 'nav', 'main', 'article', 'section', 'aside']
        accessibility['semantic_html'] = {
            tag: len(soup.find_all(tag)) for tag in semantic_tags
        }
        
        # Доступность форм
        forms = soup.find_all('form')
        form_accessibility = {
            'total': len(forms),
            'with_labels': len([form for form in forms if form.find_all('label')]),
            'with_placeholders': len([form for form in forms if form.find_all(attrs={'placeholder': True})])
        }
        accessibility['forms'] = form_accessibility
        
        return accessibility
    
    def _calculate_readability_score(self, words, sentences, avg_word_length, avg_sentence_length):
        """Расчет улучшенной оценки читаемости"""
        # Упрощенная формула на основе Flesch Reading Ease
        if not sentences or not words:
            return 0
        
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / avg_sentence_length))
        return max(0, min(100, score))
    
    def _get_readability_level(self, score):
        """Уровень читаемости"""
        if score >= 90: return "Очень легко"
        elif score >= 80: return "Легко"
        elif score >= 70: return "Достаточно легко"
        elif score >= 60: return "Стандартно"
        elif score >= 50: return "Достаточно сложно"
        elif score >= 30: return "Сложно"
        else: return "Очень сложно"
    
    def _calculate_dom_depth(self, soup):
        """Вычисление глубины DOM"""
        def get_depth(element, current_depth=0):
            if not element.find_all(recursive=False):
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in element.find_all(recursive=False))
        
        return get_depth(soup.html) if soup.html else 0
    
    def _calculate_performance_score(self, performance):
        """Расчет оценки производительности"""
        score = 100
        
        # Штрафы за различные факторы
        if performance['response_time'] > 3: score -= 30
        elif performance['response_time'] > 2: score -= 20
        elif performance['response_time'] > 1: score -= 10
        
        if performance['page_size'] > 3 * 1024 * 1024: score -= 20
        elif performance['page_size'] > 2 * 1024 * 1024: score -= 15
        elif performance['page_size'] > 1 * 1024 * 1024: score -= 10
        
        if performance['dom_elements'] > 1500: score -= 15
        elif performance['dom_elements'] > 1000: score -= 10
        
        if performance['image_count'] > 20: score -= 10
        if performance['script_count'] > 15: score -= 10
        
        return max(0, score)
    
    def _get_performance_level(self, score):
        """Уровень производительности"""
        if score >= 90: return "Отличная"
        elif score >= 80: return "Хорошая"
        elif score >= 60: return "Удовлетворительная"
        elif score >= 40: return "Плохая"
        else: return "Очень плохая"
    
    def _check_mixed_content(self, html):
        """Проверка смешанного контента"""
        mixed_patterns = [
            r'src="http://',
            r'url\(http://',
            r'<link[^>]*href="http://'
        ]
        for pattern in mixed_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                return True
        return False
    
    def _check_robots_txt(self, base_url):
        """Проверка наличия robots.txt"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.head(robots_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_sitemap(self, base_url):
        """Проверка наличия sitemap.xml"""
        try:
            sitemap_url = urljoin(base_url, '/sitemap.xml')
            response = self.session.head(sitemap_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _add_issues_and_warnings(self, analysis_result):
        """Добавление предупреждений и критических проблем"""
        warnings = []
        critical_issues = []
        
        # Критические проблемы
        if not analysis_result['metadata']['title']['value']:
            critical_issues.append("Отсутствует title тег")
            
        if analysis_result['semantic_markup']['heading_hierarchy']['h1_count'] == 0:
            critical_issues.append("Отсутствует H1 заголовок")
            
        if analysis_result['content_structure']['word_count'] < 100:
            critical_issues.append("Слишком мало текстового контента (< 100 слов)")
        
        if not analysis_result['security']['https']['enabled']:
            critical_issues.append("Сайт не использует HTTPS")
        
        # Предупреждения
        if not analysis_result['metadata']['description']['value']:
            warnings.append("Отсутствует meta description")
            
        if not analysis_result['metadata']['canonical']['exists']:
            warnings.append("Отсутствует canonical URL")
            
        if analysis_result['performance']['response_time'] > OPTIMAL_VALUES['response_time_max']:
            warnings.append("Медленная загрузка страницы (> 3 сек)")
            
        if analysis_result['content_structure']['images']['alt_percentage'] < OPTIMAL_VALUES['alt_text_percentage_min']:
            warnings.append("Меньше 50% изображений имеют alt-текст")
        
        if analysis_result['security']['https']['mixed_content']:
            warnings.append("Обнаружен смешанный контент (HTTP ресурсы на HTTPS странице)")
        
        analysis_result['warnings'] = warnings
        analysis_result['critical_issues'] = critical_issues
        
        return analysis_result
    
    def _generate_recommendations(self, analysis_result):
        """Генерация рекомендаций по улучшению с примерами"""
        recommendations = []

        # Рекомендации по мета-данным
        if not analysis_result['metadata']['title']['value']:
            recommendations.append({
                'text': "Добавить title тег с релевантным заголовком страницы",
                'type': 'metadata',
                'example_key': 'missing_title'
            })
        
        if not analysis_result['metadata']['description']['value']:
            recommendations.append({
                'text': "Создать уникальный meta description длиной 120-160 символов",
                'type': 'metadata', 
                'example_key': 'missing_description'
            })

        # Рекомендации по контенту
        if analysis_result['content_structure']['word_count'] < 300:
            recommendations.append({
                'text': "Увеличить объем текстового контента до 300+ слов",
                'type': 'content',
                'example_key': 'low_content'
            })
        
        if analysis_result['content_structure']['images']['alt_percentage'] < 80:
            recommendations.append({
                'text': "Добавить alt-тексты ко всем изображениям",
                'type': 'content',
                'example_key': 'poor_alt_texts'
            })

        return recommendations

    def _calculate_enhanced_score(self, analysis_result):
        """Улучшенный расчет скора с учетом LLM-анализа"""
        from config import SCORING_CONFIG, OPTIMAL_VALUES
        
        score = 0
        max_score = 100
        
        # Мета-данные (20 баллов)
        metadata = analysis_result['metadata']
        if metadata['title']['value']:
            score += 8
            if metadata['title']['optimal']:
                score += SCORING_CONFIG['bonus_optimal']
        
        if metadata['description']['value']:
            score += 4
            if metadata['description']['optimal']:
                score += SCORING_CONFIG['bonus_optimal']
        
        if metadata['canonical']['exists']:
            score += 3
        
        # Семантическая разметка (20 баллов)
        semantic = analysis_result['semantic_markup']
        if semantic['schema_org']['exists']:
            score += 6
        if semantic['microdata']['exists']:
            score += 4
        if semantic['heading_hierarchy']['has_single_h1']:
            score += 10
        
        # Структура контента (20 баллов)
        content = analysis_result['content_structure']
        if content['word_count'] > OPTIMAL_VALUES['word_count_good']:
            score += 8
        elif content['word_count'] > OPTIMAL_VALUES['word_count_min']:
            score += 4
            
        if content['images']['alt_percentage'] > OPTIMAL_VALUES['alt_text_percentage_good']:
            score += 6
        elif content['images']['alt_percentage'] > OPTIMAL_VALUES['alt_text_percentage_min']:
            score += 3
            
        if content['lists']['total'] > 0:
            score += 3
        if content['tables'] > 0:
            score += 3
        
        # Технические аспекты (20 баллов)
        technical = analysis_result['technical_seo']
        if technical['links']['internal'] > 10:
            score += 8
        elif technical['links']['internal'] > 5:
            score += 4
            
        if technical['links']['with_anchor'] > 5:
            score += 6
        elif technical['links']['with_anchor'] > 0:
            score += 3
            
        if content['text_ratio'] > 25:
            score += 6
        
        # Производительность (10 баллов)
        performance = analysis_result['performance']
        score += min(performance['score'] / 10, 10)
        
        # Безопасность (5 баллов)
        security = analysis_result['security']
        if security['https']['enabled']:
            score += 3
        if any(security['headers'].values()):
            score += 2
        
        # Доступность (5 баллов)
        accessibility = analysis_result['accessibility']
        if accessibility['aria']['labels'] > 0:
            score += 2
        if any(accessibility['semantic_html'].values()):
            score += 3
        
        # LLM-анализ GEO (дополнительные 20 баллов)
        if 'llm_analysis' in analysis_result:
            llm_analysis = analysis_result['llm_analysis']
            if 'overall_geo_score' in llm_analysis:
                # Добавляем до 20 баллов за LLM-оценку
                geo_bonus = llm_analysis['overall_geo_score'] * 0.2
                score += geo_bonus
        
        # Штрафы за критические проблемы
        score -= len(analysis_result['critical_issues']) * SCORING_CONFIG['penalty_critical']
        score -= len(analysis_result['warnings']) * SCORING_CONFIG['penalty_warning']
        
        return max(0, min(score, max_score))