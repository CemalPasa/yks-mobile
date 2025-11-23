"""
Deneme Ekranı
TYT ve AYT deneme sonuçları
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


class DenemeScreen(MDScreen):
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
        tyt_content = self.create_exam_list('TYT')
        tyt_scroll.add_widget(tyt_content)
        tyt_tab.add_widget(tyt_scroll)
        tabs.add_widget(tyt_tab)
        
        # AYT Tab
        ayt_tab = Tab(title='AYT')
        ayt_scroll = ScrollView()
        ayt_content = self.create_exam_list('AYT')
        ayt_scroll.add_widget(ayt_content)
        ayt_tab.add_widget(ayt_scroll)
        tabs.add_widget(ayt_tab)
        
        layout.add_widget(tabs)
        self.add_widget(layout)
    
    def create_exam_list(self, deneme_turu):
        """Deneme listesi oluştur"""
        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            padding=10
        )
        content.bind(minimum_height=content.setter('height'))
        
        exams = self.db.get_denemeler_by_type(deneme_turu)
        
        if exams:
            for exam in exams:
                card = self.create_exam_card(exam)
                content.add_widget(card)
        else:
            no_exam = MDLabel(
                text=f'{deneme_turu} denemesi yok',
                size_hint_y=None,
                height=50
            )
            content.add_widget(no_exam)
        
        return content
    
    def create_exam_card(self, exam):
        """Deneme kartı oluştur"""
        net = exam['toplam_net'] if exam['toplam_net'] else 0
        
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            radius=[10]
        )
        
        name_label = MDLabel(
            text=exam['deneme_adi'],
            font_size='16sp',
            bold=True
        )
        
        date_label = MDLabel(
            text=f"📅 {exam['tarih']}",
            font_size='14sp'
        )
        
        net_label = MDLabel(
            text=f"📊 Toplam Net: {net:.2f}",
            font_size='14sp',
            bold=True
        )
        
        card.add_widget(name_label)
        card.add_widget(date_label)
        card.add_widget(net_label)
        
        return card
