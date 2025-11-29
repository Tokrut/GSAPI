"""
Базовый класс анализатора сайта
"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import time

class WebsiteAnalyzer:
    """Базовый класс для анализа веб-сайтов"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze_url(self, url):
        """Основной метод анализа URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            analysis_result = {
                'basic_info': self._get_basic_info(soup, url, response),
                'metadata': self._analyze_metadata(soup),
                'semantic_markup': self._analyze_semantic_markup(soup),
                'content_structure': self._analyze_content_structure(soup),
                'technical_seo': self._analyze_technical_seo(soup, url),
                'score': 0
            }
            
            # Расчет общего скора
            analysis_result['score'] = self._calculate_score(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            return None
    
    def _get_basic_info(self, soup, url, response):
        """Базовая информация о странице"""
        return {
            'url': url,
            'title': soup.title.string if soup.title else 'Не найден',
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _analyze_metadata(self, soup):
        """Анализ мета-данных"""
        metadata = {}
        
        # Title
        title = soup.find('title')
        metadata['title'] = {
            'value': title.string if title else None,
            'length': len(title.string) if title else 0,
            'optimal': 50 <= len(title.string) <= 60 if title else False
        }
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        metadata['description'] = {
            'value': meta_desc.get('content') if meta_desc else None,
            'length': len(meta_desc.get('content')) if meta_desc else 0,
            'optimal': 120 <= len(meta_desc.get('content')) <= 160 if meta_desc else False
        }
        
        # Meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        metadata['keywords'] = {
            'value': meta_keywords.get('content') if meta_keywords else None,
            'exists': meta_keywords is not None
        }
        
        # Open Graph
        og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:')})
        metadata['open_graph'] = {
            'tags': [tag.get('property') for tag in og_tags],
            'count': len(og_tags),
            'exists': len(og_tags) > 0
        }
        
        return metadata
    
    def _analyze_semantic_markup(self, soup):
        """Анализ семантической разметки"""
        semantic = {}
        
        # Schema.org (JSON-LD)
        json_ld = soup.find_all('script', type='application/ld+json')
        semantic['schema_org'] = {
            'scripts': len(json_ld),
            'exists': len(json_ld) > 0,
            'content': [script.string for script in json_ld if script.string]
        }
        
        # Microdata
        microdata = soup.find_all(attrs={'itemtype': True})
        semantic['microdata'] = {
            'elements': len(microdata),
            'exists': len(microdata) > 0,
            'types': list(set([elem.get('itemtype') for elem in microdata]))
        }
        
        # Заголовки
        headings = {f'h{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
        semantic['headings'] = headings
        
        # Проверка иерархии заголовков
        h1_count = len(soup.find_all('h1'))
        semantic['heading_hierarchy'] = {
            'h1_count': h1_count,
            'has_single_h1': h1_count == 1,
            'hierarchy_correct': self._check_heading_hierarchy(soup)
        }
        
        return semantic
    
    def _analyze_content_structure(self, soup):
        """Анализ структуры контента"""
        content = {}
        
        # Основной текст
        text_content = soup.get_text()
        words = text_content.split()
        content['word_count'] = len(words)
        
        # Элементы структуры
        content['lists'] = {
            'ul': len(soup.find_all('ul')),
            'ol': len(soup.find_all('ol')),
            'total': len(soup.find_all(['ul', 'ol']))
        }
        
        content['tables'] = len(soup.find_all('table'))
        
        # Изображения
        images = soup.find_all('img')
        images_with_alt = [img for img in images if img.get('alt')]
        content['images'] = {
            'total': len(images),
            'with_alt': len(images_with_alt),
            'alt_percentage': round((len(images_with_alt) / len(images)) * 100, 2) if images else 0
        }
        
        # Соотношение текст/HTML
        html_length = len(str(soup))
        text_length = len(text_content)
        content['text_ratio'] = round((text_length / html_length) * 100, 2) if html_length > 0 else 0
        
        return content
    
    def _analyze_technical_seo(self, soup, base_url):
        """Технический анализ"""
        technical = {}
        
        # Ссылки
        links = soup.find_all('a', href=True)
        internal_links = []
        external_links = []
        
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == urlparse(base_url).netloc:
                internal_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True),
                    'is_anchor': bool(link.get_text(strip=True))
                })
            else:
                external_links.append(full_url)
        
        technical['links'] = {
            'total': len(links),
            'internal': len(internal_links),
            'external': len(external_links),
            'with_anchor': len([link for link in internal_links if link['is_anchor']])
        }
        
        # Читаемость (простая метрика)
        text_content = soup.get_text()
        sentences = re.split(r'[.!?]+', text_content)
        words = text_content.split()
        
        if sentences and words:
            avg_sentence_length = len(words) / len(sentences)
            technical['readability'] = {
                'avg_sentence_length': round(avg_sentence_length, 2),
                'word_count': len(words),
                'sentence_count': len(sentences)
            }
        else:
            technical['readability'] = {
                'avg_sentence_length': 0,
                'word_count': 0,
                'sentence_count': 0
            }
        
        return technical
    
    def _check_heading_hierarchy(self, soup):
        """Проверка корректности иерархии заголовков"""
        headings = []
        for i in range(1, 7):
            elements = soup.find_all(f'h{i}')
            for elem in elements:
                headings.append({'level': i, 'element': elem})
        
        # Простая проверка: наличие H1 и последовательность уровней
        if not any(h['level'] == 1 for h in headings):
            return False
        
        return True
    
    def _calculate_score(self, analysis_result):
        """Расчет общего скора на основе критериев"""
        score = 0
        max_score = 100

        # Мета-данные (25 баллов)
        metadata = analysis_result['metadata']
        if metadata['title']['value']:
            score += 10
            if metadata['title']['optimal']:
                score += 5
        
        if metadata['description']['value']:
            score += 5
            if metadata['description']['optimal']:
                score += 5
        
        # Семантическая разметка (25 баллов)
        semantic = analysis_result['semantic_markup']
        if semantic['schema_org']['exists']:
            score += 10
        if semantic['microdata']['exists']:
            score += 5
        if semantic['heading_hierarchy']['has_single_h1']:
            score += 10
        
        # Структура контента (25 баллов)
        content = analysis_result['content_structure']
        if content['word_count'] > 300:
            score += 10
        if content['images']['alt_percentage'] > 50:
            score += 10
        if content['lists']['total'] > 0:
            score += 5
        
        # Технические аспекты (25 баллов)
        technical = analysis_result['technical_seo']
        if technical['links']['internal'] > 5:
            score += 10
        if technical['links']['with_anchor'] > 0:
            score += 10
        if content['text_ratio'] > 20:
            score += 5
        
        return min(score, max_score)
