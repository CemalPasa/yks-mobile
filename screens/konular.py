"""
Konular Ekranı
TYT ve AYT derslerinin konu takibi
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.tabs import MDTabs, MDTabsBase
from kivy.uix.scrollview import ScrollView


class Tab(MDBoxLayout, MDTabsBase):
    """Tab içeriği için temel sınıf"""
    pass


class KonularScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical')
        
        # Tabs
        tabs = MDTabs()
        
        # TYT Tab
        tyt_tab = Tab(title='TYT')
        tyt_scroll = ScrollView()
        tyt_content = self.create_course_list('TYT')
        tyt_scroll.add_widget(tyt_content)
        tyt_tab.add_widget(tyt_scroll)
        tabs.add_widget(tyt_tab)
        
        # AYT Tab
        ayt_tab = Tab(title='AYT')
        ayt_scroll = ScrollView()
        ayt_content = self.create_course_list('AYT')
        ayt_scroll.add_widget(ayt_content)
        ayt_tab.add_widget(ayt_scroll)
        tabs.add_widget(ayt_tab)
        
        layout.add_widget(tabs)
        self.add_widget(layout)
    
    def create_course_list(self, ders_turu):
        """Ders listesi oluştur"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        content.bind(minimum_height=content.setter('height'))
        
        courses = self.db.get_courses_by_type(ders_turu)
        
        for course in courses:
            card = self.create_course_card(course)
            content.add_widget(card)
        
        return content
    
    def create_course_card(self, course):
        """Ders kartı oluştur"""
        toplam = course['toplam_konu']
        tamamlanan = course['tamamlanan_konu']
        yuzde = int((tamamlanan / toplam * 100)) if toplam > 0 else 0
        
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            radius=[10]
        )
        
        name_label = MDLabel(
            text=course['ders_adi'],
            font_size='16sp',
            bold=True
        )
        
        progress_label = MDLabel(
            text=f"İlerleme: {tamamlanan}/{toplam} (%{yuzde})",
            font_size='14sp'
        )
        
        card.add_widget(name_label)
        card.add_widget(progress_label)
        
        return card
