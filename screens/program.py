"""
Program Ekranı
Haftalık çalışma programı
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView
from datetime import datetime


class ProgramScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Başlık
        title = MDLabel(
            text='Haftalık Program',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title)
        
        # Scroll view
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            padding=5
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Programı günlere göre grupla
        program = self.db.get_weekly_program()
        days = {}
        for item in program:
            gun = item['gun']
            if gun not in days:
                days[gun] = []
            days[gun].append(item)
        
        # Günleri sırayla göster
        gun_sirasi = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        today = datetime.now().strftime('%A')
        gun_mapping = {
            'Monday': 'Pazartesi',
            'Tuesday': 'Salı',
            'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe',
            'Friday': 'Cuma',
            'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        today_tr = gun_mapping.get(today, 'Pazartesi')
        
        for gun in gun_sirasi:
            if gun in days:
                # Gün başlığı
                is_today = gun == today_tr
                day_card = self.create_day_card(gun, days[gun], is_today)
                content.add_widget(day_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_day_card(self, gun, tasks, is_today):
        """Gün kartı oluştur"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=len(tasks) * 60 + 50,
            padding=10,
            radius=[10],
            md_bg_color='#3498db' if is_today else '#ecf0f1'
        )
        
        # Gün başlığı
        day_label = MDLabel(
            text=f"{'🔵 ' if is_today else ''}{gun}",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1) if is_today else (0, 0, 0, 1)
        )
        card.add_widget(day_label)
        
        # Görevler
        for task in tasks:
            task_box = MDBoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=50,
                spacing=10
            )
            
            time_label = MDLabel(
                text=task['saat'],
                size_hint_x=0.3,
                color=(1, 1, 1, 1) if is_today else (0, 0, 0, 1)
            )
            
            course_label = MDLabel(
                text=task['ders_adi'],
                size_hint_x=0.5,
                color=(1, 1, 1, 1) if is_today else (0, 0, 0, 1)
            )
            
            status_label = MDLabel(
                text='✅' if task['tamamlandi'] else '⭕',
                size_hint_x=0.2,
                font_size='18sp'
            )
            
            task_box.add_widget(time_label)
            task_box.add_widget(course_label)
            task_box.add_widget(status_label)
            
            card.add_widget(task_box)
        
        return card
