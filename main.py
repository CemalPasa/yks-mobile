"""
YKS Mobil Takip Uygulaması
Kivy/KivyMD tabanlı mobil uygulama
"""

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.core.window import Window
from database.db_manager import DatabaseManager
from screens.dashboard import DashboardScreen
from screens.konular import KonularScreen
from screens.program import ProgramScreen
from screens.deneme import DenemeScreen
from screens.istatistik import IstatistikScreen
from screens.program_olustur import ProgramOlusturScreen
from screens.gunluk_soru import GunlukSoruScreen
from screens.simulasyon import SimulasyonScreen

# Mobil simülasyonu için pencere boyutu (iPhone X)
Window.size = (375, 812)


class YKSMobileApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Alt navigasyon menüsü
        bottom_nav = MDBottomNavigation()
        
        # Dashboard tab
        dashboard_item = MDBottomNavigationItem(
            name='dashboard',
            text='Ana Sayfa',
            icon='home'
        )
        dashboard_item.add_widget(DashboardScreen(db=self.db))
        bottom_nav.add_widget(dashboard_item)
        
        # Konular tab
        konular_item = MDBottomNavigationItem(
            name='konular',
            text='Konular',
            icon='book-open-page-variant'
        )
        konular_item.add_widget(KonularScreen(db=self.db))
        bottom_nav.add_widget(konular_item)
        
        # Program tab
        program_item = MDBottomNavigationItem(
            name='program',
            text='Program',
            icon='calendar-month'
        )
        program_item.add_widget(ProgramScreen(db=self.db))
        bottom_nav.add_widget(program_item)
        
        # Deneme tab
        deneme_item = MDBottomNavigationItem(
            name='deneme',
            text='Deneme',
            icon='file-document-edit'
        )
        deneme_item.add_widget(DenemeScreen(db=self.db))
        bottom_nav.add_widget(deneme_item)
        
        # İstatistik tab
        istatistik_item = MDBottomNavigationItem(
            name='istatistik',
            text='İstatistik',
            icon='chart-bar'
        )
        istatistik_item.add_widget(IstatistikScreen(db=self.db))
        bottom_nav.add_widget(istatistik_item)
        
        # Program Oluştur tab
        program_olustur_item = MDBottomNavigationItem(
            name='program_olustur',
            text='Prog.Oluştur',
            icon='calendar-plus'
        )
        program_olustur_item.add_widget(ProgramOlusturScreen(db=self.db))
        bottom_nav.add_widget(program_olustur_item)
        
        # Günlük Soru tab
        gunluk_soru_item = MDBottomNavigationItem(
            name='gunluk_soru',
            text='Günlük Soru',
            icon='pencil'
        )
        gunluk_soru_item.add_widget(GunlukSoruScreen(db=self.db))
        bottom_nav.add_widget(gunluk_soru_item)
        
        # Simülasyon tab
        simulasyon_item = MDBottomNavigationItem(
            name='simulasyon',
            text='Simülasyon',
            icon='chart-timeline-variant'
        )
        simulasyon_item.add_widget(SimulasyonScreen(db=self.db))
        bottom_nav.add_widget(simulasyon_item)
        
        return bottom_nav


if __name__ == '__main__':
    YKSMobileApp().run()
