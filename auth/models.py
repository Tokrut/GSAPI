"""
Модели данных для системы аутентификации
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Subscription:
    """Модель подписки пользователя"""
    subscription_type: str  # "free", "pro", "pro_plus"
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    
    def is_valid(self) -> bool:
        """Проверка валидности подписки"""
        if not self.is_active:
            return False
        if self.end_date and datetime.now() > self.end_date:
            return False
        return True

@dataclass
class User:
    """Модель пользователя"""
    username: str
    email: str
    password_hash: str
    created_at: datetime
    analysis_history: List[Dict[str, Any]] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    subscription: Optional[Subscription] = None
    
    # Ограничения по подпискам
    FREE_LIMIT = 5  # Максимум 5 анализов для Free
    
    def __post_init__(self):
        """Инициализация после создания объекта"""
        if self.analysis_history is None:
            self.analysis_history = []
    
        # Если подписка не установлена, создаем бесплатную
        if self.subscription is None:
            self.subscription = Subscription(
                subscription_type="free",
                start_date=self.created_at,
                is_active=True
            )
    
    def to_dict(self):
        """Преобразование в словарь для хранения"""
        return {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at.isoformat(),
            'analysis_history': self.analysis_history,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'subscription': {
                'subscription_type': self.subscription.subscription_type,
                'start_date': self.subscription.start_date.isoformat(),
                'end_date': self.subscription.end_date.isoformat() if self.subscription.end_date else None,
                'is_active': self.subscription.is_active
            } if self.subscription else None
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание из словаря"""
        subscription_data = data.get('subscription')
        subscription = None
        
        if subscription_data:
            subscription = Subscription(
                subscription_type=subscription_data['subscription_type'],
                start_date=datetime.fromisoformat(subscription_data['start_date']),
                end_date=datetime.fromisoformat(subscription_data['end_date']) if subscription_data.get('end_date') else None,
                is_active=subscription_data.get('is_active', True)
            )
        
        return cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            created_at=datetime.fromisoformat(data['created_at']),
            analysis_history=data.get('analysis_history', []),
            last_login=datetime.fromisoformat(data['last_login']) if data['last_login'] else None,
            is_active=data.get('is_active', True),
            subscription=subscription
        )
    
    def add_analysis(self, analysis_data: Dict[str, Any]):
        """Добавление анализа в историю"""
        # Ограничиваем историю последними 50 анализами
        if len(self.analysis_history) >= 50:
            self.analysis_history = self.analysis_history[-49:]
        
        self.analysis_history.append(analysis_data)
    
    def clear_analysis_history(self):
        """Очистка истории анализов"""
        self.analysis_history = []
    
    def can_perform_analysis(self) -> bool:
        """Проверка возможности выполнения анализа"""
        if not self.subscription or not self.subscription.is_valid():
            return False
        
        if self.subscription.subscription_type == "free":
            # Для Free подписки - не более FREE_LIMIT анализов
            return len(self.analysis_history) < self.FREE_LIMIT
        
        # Для Pro и Pro+ - неограниченно
        return True
    
    def can_use_deep_analysis(self) -> bool:
        """Проверка возможности использования глубокого анализа с конкурентами"""
        if not self.subscription or not self.subscription.is_valid():
            return False
        
        # Только для Pro+ подписки
        return self.subscription.subscription_type == "pro_plus"
    
    def get_remaining_analyses(self) -> int:
        """Получение количества оставшихся анализов"""
        if not self.subscription or not self.subscription.is_valid():
            return 0
        
        if self.subscription.subscription_type == "free":
            return max(0, self.FREE_LIMIT - len(self.analysis_history))
        
        # Для Pro и Pro+ - неограниченно
        return float('inf')
    
    def upgrade_subscription(self, new_type: str, duration_days: int = 30):
        """Обновление подписки"""
        self.subscription = Subscription(
            subscription_type=new_type,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            is_active=True
        )
    
    def get_subscription_info(self) -> Dict[str, Any]:
        """Получение информации о подписке"""
        if not self.subscription:
            return {
                'type': 'free',
                'status': 'active',
                'remaining_analyses': self.FREE_LIMIT - len(self.analysis_history),
                'can_use_deep_analysis': False,
                'description': 'Бесплатный тариф - 5 анализов всего'
            }
        
        is_valid = self.subscription.is_valid()
        remaining = self.get_remaining_analyses()
        
        descriptions = {
            'free': 'Бесплатный тариф - 5 анализов всего',
            'pro': 'Профессиональный тариф - неограниченное число анализов, но без доступа к анализу с конкурентами',
            'pro_plus': 'Профессиональный+ тариф - весь функционал приложения'
        }
        
        return {
            'type': self.subscription.subscription_type,
            'status': 'active' if is_valid else 'expired',
            'remaining_analyses': remaining,
            'can_use_deep_analysis': self.can_use_deep_analysis(),
            'description': descriptions.get(self.subscription.subscription_type, 'Неизвестный тариф'),
            'end_date': self.subscription.end_date
        }