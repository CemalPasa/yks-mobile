"""
Dashboard Ekranı
Ana sayfa - TYT/AYT istatistikleri ve bugünün görevleri
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView


class DashboardScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Scroll view
        scroll = ScrollView()
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, padding=10)
        content.bind(minimum_height=content.setter('height'))
        
        # Başlık
        title = MDLabel(
            text='YKS Takip Sistemi',
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=50
        )
        content.add_widget(title)
        
        # TYT İstatistikleri
        tyt_stats = self.db.get_tyt_stats()
        tyt_card = self.create_stat_card(
            'TYT İstatistikleri',
            f"{tyt_stats['tamamlanan']}/{tyt_stats['toplam']} Konu",
            '#3498db'
        )
        content.add_widget(tyt_card)
        
        # AYT İstatistikleri
        ayt_stats = self.db.get_ayt_stats()
        ayt_card = self.create_stat_card(
            'AYT İstatistikleri',
            f"{ayt_stats['tamamlanan']}/{ayt_stats['toplam']} Konu",
            '#27ae60'
        )
        content.add_widget(ayt_card)
        
        # Bugünün Görevleri
        tasks_label = MDLabel(
            text='Bugünün Görevleri',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        content.add_widget(tasks_label)
        
        tasks = self.db.get_today_tasks()
        if tasks:
            for task in tasks:
                task_card = self.create_task_card(task)
                content.add_widget(task_card)
        else:
            no_task = MDLabel(
                text='Bugün için görev yok',
                size_hint_y=None,
                height=30
            )
            content.add_widget(no_task)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_stat_card(self, title, value, color):
        """İstatistik kartı oluştur"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            md_bg_color=color,
            radius=[10]
        )
        
        title_label = MDLabel(
            text=title,
            font_size='16sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        value_label = MDLabel(
            text=value,
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        card.add_widget(title_label)
        card.add_widget(value_label)
        
        return card
    
    def create_task_card(self, task):
        """Görev kartı oluştur"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=80,
            padding=10,
            radius=[5]
        )
        
        time_label = MDLabel(
            text=f"⏰ {task['saat']}",
            font_size='14sp',
            bold=True
        )
        
        course_label = MDLabel(
            text=f"📚 {task['ders_adi']}",
            font_size='14sp'
        )
        
        if task['konu_adi']:
            topic_label = MDLabel(
                text=f"📖 {task['konu_adi']}",
                font_size='12sp'
            )
            card.add_widget(topic_label)
        
        status = '✅' if task['tamamlandi'] else '⭕'
        status_label = MDLabel(
            text=status,
            font_size='18sp'
        )
        
        card.add_widget(time_label)
        card.add_widget(course_label)
        card.add_widget(status_label)
        
        return card
