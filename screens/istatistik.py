"""
İstatistik Ekranı
Genel istatistikler ve grafikler
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView


class IstatistikScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Başlık
        title = MDLabel(
            text='İstatistikler',
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
        
        # Genel İstatistikler
        general_label = MDLabel(
            text='Genel İstatistikler',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        content.add_widget(general_label)
        
        # Toplam çalışma saati
        study_hours = self.db.get_total_study_hours()
        study_card = self.create_stat_card('📚 Toplam Çalışma', f'{study_hours} saat', '#3498db')
        content.add_widget(study_card)
        
        # Tamamlanan konu sayısı
        completed_topics = self.db.get_completed_topics_count()
        topics_card = self.create_stat_card('✅ Tamamlanan Konu', f'{completed_topics} konu', '#27ae60')
        content.add_widget(topics_card)
        
        # Deneme sayısı
        exam_count = self.db.get_total_exam_count()
        exam_card = self.create_stat_card('📝 Deneme Sayısı', f'{exam_count} deneme', '#e74c3c')
        content.add_widget(exam_card)
        
        # Konu İstatistikleri
        konu_label = MDLabel(
            text='Konu İlerlemesi',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        content.add_widget(konu_label)
        
        # TYT ve AYT konu istatistikleri
        tyt_stats = self.db.get_tyt_stats()
        ayt_stats = self.db.get_ayt_stats()
        
        stats_text = f"TYT: {tyt_stats['tamamlanan']}/{tyt_stats['toplam']} "
        stats_text += f"(%{int(tyt_stats['tamamlanan']/tyt_stats['toplam']*100) if tyt_stats['toplam'] > 0 else 0})\n"
        stats_text += f"AYT: {ayt_stats['tamamlanan']}/{ayt_stats['toplam']} "
        stats_text += f"(%{int(ayt_stats['tamamlanan']/ayt_stats['toplam']*100) if ayt_stats['toplam'] > 0 else 0})\n"
        stats_text += f"TOPLAM: {tyt_stats['tamamlanan'] + ayt_stats['tamamlanan']}/{tyt_stats['toplam'] + ayt_stats['toplam']}"
        
        konu_chart = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=15,
            radius=[10]
        )
        
        chart_label = MDLabel(
            text=stats_text,
            font_size='14sp'
        )
        konu_chart.add_widget(chart_label)
        content.add_widget(konu_chart)
        
        # Son Denemeler
        recent_label = MDLabel(
            text='Son Denemeler',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=30
        )
        content.add_widget(recent_label)
        
        recent_exams = self.db.get_recent_exams(5)
        if recent_exams:
            for exam in recent_exams:
                exam_card = self.create_exam_card(exam)
                content.add_widget(exam_card)
        else:
            no_exam = MDLabel(
                text='Henüz deneme girilmemiş',
                size_hint_y=None,
                height=30
            )
            content.add_widget(no_exam)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def create_stat_card(self, title, value, color):
        """İstatistik kartı oluştur"""
        card = MDCard(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            padding=15,
            md_bg_color=color,
            radius=[10]
        )
        
        left_box = MDBoxLayout(orientation='vertical', size_hint_x=0.7)
        
        title_label = MDLabel(
            text=title,
            font_size='14sp',
            color=(1, 1, 1, 1)
        )
        
        value_label = MDLabel(
            text=value,
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        
        left_box.add_widget(title_label)
        left_box.add_widget(value_label)
        
        card.add_widget(left_box)
        
        return card
    
    def create_exam_card(self, exam):
        """Deneme kartı oluştur"""
        net = exam['toplam_net'] if exam['toplam_net'] else 0
        
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=90,
            padding=10,
            radius=[5]
        )
        
        name_label = MDLabel(
            text=f"{exam['deneme_adi']} ({exam['deneme_turu']})",
            font_size='14sp',
            bold=True
        )
        
        date_label = MDLabel(
            text=f"📅 {exam['tarih']}",
            font_size='12sp'
        )
        
        net_label = MDLabel(
            text=f"Net: {net:.2f}",
            font_size='14sp'
        )
        
        card.add_widget(name_label)
        card.add_widget(date_label)
        card.add_widget(net_label)
        
        return card
