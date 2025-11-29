"""
Сервис аутентификации и управления пользователями
"""

import hashlib
import secrets
import json
import os
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from .models import User

class AuthService:
    """Сервис для управления аутентификацией и пользователями"""
    
    def __init__(self, users_file: str = 'users.json'):
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self) -> dict:
        """Загрузка пользователей из файла"""
        if not os.path.exists(self.users_file):
            return {}
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {username: User.from_dict(user_data) for username, user_data in data.items()}
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}
    
    def _save_users(self):
        """Сохранение пользователей в файл"""
        try:
            # Создаем backup перед сохранением
            if os.path.exists(self.users_file):
                backup_file = f"{self.users_file}.backup"
                with open(self.users_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                users_dict = {username: user.to_dict() for username, user in self.users.items()}
                json.dump(users_dict, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения пользователей: {e}")
            return False
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Хеширование пароля с солью"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Количество итераций
        ).hex()
        
        return password_hash, salt
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Регистрация нового пользователя"""
        # Проверка существования пользователя
        if username in self.users:
            return False, "Пользователь с таким именем уже существует"
        
        # Валидация данных
        if len(username) < 3:
            return False, "Имя пользователя должно содержать минимум 3 символа"
        
        if len(password) < 6:
            return False, "Пароль должен содержать минимум 6 символов"
        
        if '@' not in email:
            return False, "Некорректный email адрес"
        
        # Хеширование пароля
        password_hash, salt = self._hash_password(password)
        full_hash = f"{salt}${password_hash}"
        
        # Создание пользователя с бесплатной подпиской
        user = User(
            username=username,
            email=email,
            password_hash=full_hash,
            created_at=datetime.now(),
            analysis_history=[]
        )
        
        # Сохранение
        self.users[username] = user
        if self._save_users():
            return True, "Пользователь успешно зарегистрирован"
        else:
            return False, "Ошибка при сохранении пользователя"
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """Аутентификация пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден", None
        
        user = self.users[username]
        
        if not user.is_active:
            return False, "Учетная запись заблокирована", None
        
        # Проверка пароля
        salt, stored_hash = user.password_hash.split('$')
        input_hash, _ = self._hash_password(password, salt)
        
        if secrets.compare_digest(input_hash, stored_hash):
            # Обновление времени последнего входа
            user.last_login = datetime.now()
            self._save_users()
            return True, "Успешная аутентификация", user
        else:
            return False, "Неверный пароль", None
    
    def user_exists(self, username: str) -> bool:
        """Проверка существования пользователя"""
        return username in self.users
    
    def get_user(self, username: str) -> Optional[User]:
        """Получение пользователя по имени"""
        return self.users.get(username)
    
    def update_user_email(self, username: str, new_email: str) -> bool:
        """Обновление email пользователя"""
        if username not in self.users:
            return False
        
        if '@' not in new_email:
            return False
        
        self.users[username].email = new_email
        return self._save_users()
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Смена пароля пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        if len(new_password) < 6:
            return False, "Новый пароль должен содержать минимум 6 символов"
        
        # Проверка старого пароля
        auth_success, message, user = self.authenticate_user(username, old_password)
        if not auth_success:
            return False, "Неверный текущий пароль"
        
        # Установка нового пароля
        password_hash, salt = self._hash_password(new_password)
        user.password_hash = f"{salt}${password_hash}"
        
        if self._save_users():
            return True, "Пароль успешно изменен"
        else:
            return False, "Ошибка при сохранении пароля"
    
    def save_user_analysis(self, username: str, analysis_data: Dict[str, Any]) -> bool:
        """Сохранение анализа пользователя"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user.add_analysis(analysis_data)
        return self._save_users()
    
    def clear_user_analysis_history(self, username: str) -> bool:
        """Очистка истории анализов пользователя"""
        if username not in self.users:
            return False
        
        user = self.users[username]
        user.clear_analysis_history()
        return self._save_users()
    
    def get_user_analysis_history(self, username: str) -> list:
        """Получение истории анализов пользователя"""
        if username not in self.users:
            return []
        
        return self.users[username].analysis_history
    
    def can_user_perform_analysis(self, username: str) -> Tuple[bool, str]:
        """Проверка возможности выполнения анализа пользователем"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        user = self.users[username]
        
        if not user.can_perform_analysis():
            if user.subscription and user.subscription.subscription_type == "free":
                return False, f"Лимит анализов исчерпан. Осталось: {user.get_remaining_analyses()}"
            else:
                return False, "Подписка не активна или истекла"
        
        return True, "Можно выполнять анализ"
    
    def can_user_use_deep_analysis(self, username: str) -> Tuple[bool, str]:
        """Проверка возможности использования глубокого анализа"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        user = self.users[username]
        
        if not user.can_use_deep_analysis():
            return False, "Глубокий анализ с конкурентами доступен только для подписки Pro+"
        
        return True, "Можно использовать глубокий анализ"
    
    def upgrade_user_subscription(self, username: str, subscription_type: str, duration_days: int = 30) -> Tuple[bool, str]:
        """Обновление подписки пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден"
        
        valid_types = ["free", "pro", "pro_plus"]
        if subscription_type not in valid_types:
            return False, f"Неверный тип подписки. Допустимые значения: {', '.join(valid_types)}"
        
        user = self.users[username]
        user.upgrade_subscription(subscription_type, duration_days)
        
        if self._save_users():
            return True, f"Подписка успешно обновлена до {subscription_type}"
        else:
            return False, "Ошибка при сохранении подписки"
    
    def get_user_subscription_info(self, username: str) -> Dict[str, Any]:
        """Получение информации о подписке пользователя"""
        if username not in self.users:
            return {
                'type': 'none',
                'status': 'not_found',
                'remaining_analyses': 0,
                'can_use_deep_analysis': False,
                'description': 'Пользователь не найден'
            }
        
        return self.users[username].get_subscription_info()