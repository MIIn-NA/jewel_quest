import json
import os
from datetime import datetime


class Highscores:
    def __init__(self, filepath='config/highscores.json'):
        self.filepath = filepath
        self.scores = []
        self.load()

    def load(self):
        """Загружает рекорды из файла"""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
                print(f"✅ Загружено {len(self.scores)} рекордов")
            else:
                self.scores = []
                print("📝 Файл рекордов создан")
        except Exception as e:
            print(f"❌ Ошибка загрузки рекордов: {e}")
            self.scores = []

    def save(self):
        """Сохраняет рекорды в файл"""
        try:
            # Сортируем по очкам (убывание)
            self.scores.sort(key=lambda x: x['score'], reverse=True)

            # Оставляем только топ-10
            self.scores = self.scores[:10]

            data = {'scores': self.scores}
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Сохранено {len(self.scores)} рекордов")
        except Exception as e:
            print(f"❌ Ошибка сохранения рекордов: {e}")

    def add_score(self, name, score, level, mode='time'):
        """Добавляет новый рекорд (только для режима времени)"""
        if mode != 'time':
            print("⚠️ Рекорды сохраняются только для режима 'Время'")
            return None

        record = {
            'name': name,
            'score': score,
            'level': level,
            'mode': mode,
            'date': datetime.now().strftime("%d.%m.%Y")
        }
        self.scores.append(record)

        self.save()

        # Возвращаем позицию в таблице
        for i, r in enumerate(self.scores):
            if r['name'] == name and r['score'] == score:
                return i + 1
        return None

    def get_top_scores(self, limit=10):
        """Возвращает топ рекордов (отсортировано по очкам)"""
        # Сортируем по очкам (убывание)
        sorted_scores = sorted(self.scores, key=lambda x: x['score'], reverse=True)
        return sorted_scores[:limit]