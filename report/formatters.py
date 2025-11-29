"""
Форматирование данных для отчетов GEO Analyzer Pro
"""

import pandas as pd
from datetime import datetime
from config import OPTIMAL_VALUES, COLOR_SCHEME

def format_metadata_for_display(metadata):
    """Форматирование мета-данных для отображения"""
    formatted = {
        'title': {
            'exists': bool(metadata['title']['value']),
            'value': metadata['title']['value'] or 'Отсутствует',
            'length': metadata['title']['length'],
            'optimal': metadata['title']['optimal'],
            'status': 'optimal' if metadata['title']['optimal'] else 'warning' if metadata['title']['value'] else 'error'
        },
        'description': {
            'exists': bool(metadata['description']['value']),
            'value': metadata['description']['value'] or 'Отсутствует',
            'length': metadata['description']['length'],
            'optimal': metadata['description']['optimal'],
            'status': 'optimal' if metadata['description']['optimal'] else 'warning' if metadata['description']['value'] else 'error'
        },
        'technical': {
            'canonical': {
                'exists': metadata['canonical']['exists'],
                'value': metadata['canonical']['value'],
                'status': 'optimal' if metadata['canonical']['exists'] else 'warning'
            },
            'robots': {
                'exists': metadata['robots']['exists'],
                'value': metadata['robots']['value'],
                'status': 'optimal' if metadata['robots']['exists'] else 'warning'
            },
            'viewport': {
                'exists': metadata['viewport']['exists'],
                'value': metadata['viewport']['value'],
                'status': 'optimal' if metadata['viewport']['exists'] else 'error'
            },
            'charset': {
                'exists': metadata['charset']['exists'],
                'value': metadata['charset']['value'],
                'status': 'optimal' if metadata['charset']['exists'] else 'error'
            }
        },
        'open_graph': {
            'exists': metadata['open_graph']['exists'],
            'count': metadata['open_graph']['count'],
            'tags': metadata['open_graph']['tags']
        }
    }
    
    return formatted

def format_content_for_display(content):
    """Форматирование структуры контента для отображения"""
    formatted = {
        'basic_metrics': {
            'word_count': {
                'value': content['word_count'],
                'status': 'optimal' if content['word_count'] > OPTIMAL_VALUES['word_count_good'] 
                         else 'good' if content['word_count'] > OPTIMAL_VALUES['word_count_min'] 
                         else 'warning'
            },
            'text_ratio': {
                'value': f"{content['text_ratio']}%",
                'status': 'optimal' if content['text_ratio'] > 25 
                         else 'good' if content['text_ratio'] > 15 
                         else 'warning'
            },
            'lists': {
                'value': content['lists']['total'],
                'status': 'optimal' if content['lists']['total'] > 3 
                         else 'good' if content['lists']['total'] > 0 
                         else 'warning'
            },
            'tables': {
                'value': content['tables'],
                'status': 'optimal' if content['tables'] > 0 else 'info'
            }
        },
        'images': {
            'total': content['images']['total'],
            'with_alt': content['images']['with_alt'],
            'percentage': content['images']['alt_percentage'],
            'status': 'optimal' if content['images']['alt_percentage'] > OPTIMAL_VALUES['alt_text_percentage_good']
                     else 'good' if content['images']['alt_percentage'] > OPTIMAL_VALUES['alt_text_percentage_min']
                     else 'warning'
        },
        'readability': {}
    }
    
    if 'readability' in content:
        formatted['readability'] = {
            'score': {
                'value': content['readability']['score'],
                'status': 'optimal' if content['readability']['score'] > 80 
                         else 'good' if content['readability']['score'] > 60 
                         else 'warning'
            },
            'avg_sentence_length': content['readability']['avg_sentence_length'],
            'avg_word_length': content['readability']['avg_word_length'],
            'words': content['readability']['words'],
            'sentences': content['readability']['sentences']
        }
    
    if 'keyword_analysis' in content:
        formatted['keywords'] = {
            'top_words': content['keyword_analysis']['top_words'],
            'unique_words': content['keyword_analysis']['unique_words']
        }
    
    return formatted

def format_technical_for_display(technical):
    """Форматирование технических данных для отображения"""
    formatted = {
        'links': {
            'basic': {
                'total': technical['links']['total'],
                'internal': technical['links']['internal'],
                'external': technical['links']['external'],
                'with_anchor': technical['links']['with_anchor']
            },
            'enhanced': {
                'total': technical['enhanced_links']['total'],
                'internal': technical['enhanced_links']['internal'],
                'external': technical['enhanced_links']['external'],
                'nofollow': technical['enhanced_links']['nofollow'],
                'with_anchor': technical['enhanced_links']['with_anchor'],
                'empty_anchor': technical['enhanced_links']['empty_anchor']
            }
        },
        'readability': {
            'avg_sentence_length': technical['readability']['avg_sentence_length'],
            'word_count': technical['readability']['word_count'],
            'sentence_count': technical['readability']['sentence_count']
        },
        'technical_tags': {
            'canonical': {
                'exists': technical['important_tags']['canonical'],
                'status': 'optimal' if technical['important_tags']['canonical'] else 'warning'
            },
            'robots_txt': {
                'exists': technical['important_tags']['robots_txt'],
                'status': 'optimal' if technical['important_tags']['robots_txt'] else 'warning'
            },
            'sitemap': {
                'exists': technical['important_tags']['sitemap'],
                'status': 'optimal' if technical['important_tags']['sitemap'] else 'info'
            },
            'favicon': {
                'exists': technical['important_tags']['favicon'],
                'status': 'optimal' if technical['important_tags']['favicon'] else 'info'
            }
        }
    }
    
    # Добавляем статусы для ссылок
    formatted['links']['basic']['internal_status'] = (
        'optimal' if technical['links']['internal'] > 10 
        else 'good' if technical['links']['internal'] > 5 
        else 'warning'
    )
    
    formatted['links']['basic']['external_status'] = (
        'optimal' if technical['links']['external'] > 0 
        else 'info'
    )
    
    return formatted

def format_performance_for_display(performance):
    """Форматирование данных производительности для отображения"""
    formatted = {
        'score': {
            'value': performance['score'],
            'status': 'optimal' if performance['score'] > 80 
                     else 'good' if performance['score'] > 60 
                     else 'warning' if performance['score'] > 40 
                     else 'error'
        },
        'response_time': {
            'value': performance['response_time'],
            'formatted': f"{performance['response_time']:.2f}с",
            'status': 'optimal' if performance['response_time'] <= OPTIMAL_VALUES['response_time_good']
                     else 'good' if performance['response_time'] <= 2.0
                     else 'warning' if performance['response_time'] <= OPTIMAL_VALUES['response_time_max']
                     else 'error'
        },
        'sizes': {
            'page_size': {
                'value': performance['page_size'],
                'formatted': f"{performance['page_size'] // 1024} KB",
                'status': 'optimal' if performance['page_size'] <= OPTIMAL_VALUES['page_size_good']
                         else 'good' if performance['page_size'] <= OPTIMAL_VALUES['page_size_max']
                         else 'warning'
            },
            'html_size': {
                'value': performance['html_size'],
                'formatted': f"{performance['html_size'] // 1024} KB",
                'status': 'info'
            }
        },
        'resources': {
            'images': {
                'value': performance['image_count'],
                'status': 'optimal' if performance['image_count'] <= 15 
                         else 'good' if performance['image_count'] <= 25 
                         else 'warning'
            },
            'scripts': {
                'value': performance['script_count'],
                'status': 'optimal' if performance['script_count'] <= 5 
                         else 'good' if performance['script_count'] <= 10 
                         else 'warning'
            },
            'stylesheets': {
                'value': performance['stylesheet_count'],
                'status': 'optimal' if performance['stylesheet_count'] <= 3 
                         else 'good' if performance['stylesheet_count'] <= 5 
                         else 'warning'
            }
        }
    }
    
    return formatted

def format_score_for_display(score):
    """Форматирование общей оценки для отображения"""
    if score >= 80:
        status = 'optimal'
        label = 'Отлично'
        color = COLOR_SCHEME['excellent']
    elif score >= 60:
        status = 'good'
        label = 'Хорошо'
        color = COLOR_SCHEME['good']
    elif score >= 40:
        status = 'warning'
        label = 'Требует улучшений'
        color = COLOR_SCHEME['average']
    else:
        status = 'error'
        label = 'Критически низкий'
        color = COLOR_SCHEME['critical']
    
    return {
        'value': score,
        'status': status,
        'label': label,
        'color': color
    }

def format_issues_for_display(issues, warnings):
    """Форматирование проблем и предупреждений для отображения"""
    formatted = {
        'critical_issues': {
            'count': len(issues),
            'items': issues,
            'status': 'error' if issues else 'success'
        },
        'warnings': {
            'count': len(warnings),
            'items': warnings,
            'status': 'warning' if warnings else 'success'
        }
    }
    
    return formatted

def create_analysis_summary(result):
    """Создание сводки анализа для быстрого просмотра"""
    summary = {
        'basic_info': {
            'url': result['basic_info']['url'],
            'analysis_date': result['basic_info']['analysis_date'],
            'status_code': result['basic_info']['status_code'],
            'response_time': result['basic_info']['response_time']
        },
        'score': format_score_for_display(result['score']),
        'performance_score': format_score_for_display(result['performance']['score']),
        'key_metrics': {
            'title_exists': bool(result['metadata']['title']['value']),
            'description_exists': bool(result['metadata']['description']['value']),
            'h1_count': result['semantic_markup']['heading_hierarchy']['h1_count'],
            'word_count': result['content_structure']['word_count'],
            'images_with_alt': result['content_structure']['images']['alt_percentage'],
            'internal_links': result['technical_seo']['links']['internal']
        },
        'issues': format_issues_for_display(result['critical_issues'], result['warnings'])
    }
    
    return summary
