"""
Sınav Simülasyonu Ekranı
Konu ve deneme performansına göre tahmin
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView


class SimulasyonScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Başlık
        title = MDLabel(
            text='🎯 Sınav Simülasyonu',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title)
        
        # Yenile butonu
        refresh_btn = MDRaisedButton(
            text='🔄 Simülasyonu Yenile',
            size_hint_y=None,
            height=50,
            md_bg_color=(0.2, 0.6, 0.86, 1),
            on_release=self.calculate_simulation
        )
        layout.add_widget(refresh_btn)
        
        # Scroll view
        scroll = ScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint_y=None,
            padding=5
        )
        content.bind(minimum_height=content.setter('height'))
        
        # TYT Tahmini Kartı
        self.tyt_card = self.create_prediction_card('TYT', '#3498db')
        content.add_widget(self.tyt_card)
        
        # AYT Tahmini Kartı
        self.ayt_card = self.create_prediction_card('AYT (EA)', '#27ae60')
        content.add_widget(self.ayt_card)
        
        # Detaylı Analiz Başlığı
        analysis_title = MDLabel(
            text='📊 Ders Bazlı Analiz',
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        content.add_widget(analysis_title)
        
        # Ders detayları
        self.ders_container = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        self.ders_container.bind(minimum_height=self.ders_container.setter('height'))
        content.add_widget(self.ders_container)
        
        # Bilgi notu
        info_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            radius=[10],
            md_bg_color=(0.2, 0.2, 0.2, 0.5)
        )
        
        info_text = MDLabel(
            text='ℹ️ Tahmin Nasıl Yapılır?\n\n'
                 '• Konu tamamlanma oranı: %40\n'
                 '• Deneme performansı: %60\n\n'
                 'Daha fazla konu ve deneme ile tahmin doğruluğu artar.',
            font_size='12sp'
        )
        info_card.add_widget(info_text)
        content.add_widget(info_card)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # İlk hesaplama
        self.calculate_simulation()
    
    def create_prediction_card(self, exam_name, color):
        """Tahmin kartı oluştur"""
        card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=180,
            padding=15,
            md_bg_color=color,
            radius=[15]
        )
        
        # Sınav adı
        name_label = MDLabel(
            text=exam_name,
            font_size='18sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=30
        )
        card.add_widget(name_label)
        
        # Tahmini net (büyük yazı)
        net_label = MDLabel(
            text='0.0',
            font_size='48sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=60
        )
        card.add_widget(net_label)
        
        # "Tahmini Net" yazısı
        net_text = MDLabel(
            text='Tahmini Net',
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=25
        )
        card.add_widget(net_text)
        
        # Alt bilgi
        info_label = MDLabel(
            text='Hesaplanıyor...',
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1),
            size_hint_y=None,
            height=30
        )
        card.add_widget(info_label)
        
        return {
            'card': card,
            'net_label': net_label,
            'info_label': info_label
        }
    
    def calculate_simulation(self, *args):
        """Simülasyonu hesapla"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # 1. TYT Konu tamamlanma oranı
        cursor.execute('''
            SELECT 
                COUNT(k.id) as toplam,
                SUM(CASE WHEN k.tamamlandi = 1 THEN 1 ELSE 0 END) as tamamlanan
            FROM konular k
            JOIN dersler d ON k.ders_id = d.id
            WHERE d.ders_turu = 'TYT'
        ''')
        tyt_konu = cursor.fetchone()
        tyt_toplam = tyt_konu['toplam'] if tyt_konu['toplam'] else 1
        tyt_tamamlanan = tyt_konu['tamamlanan'] if tyt_konu['tamamlanan'] else 0
        tyt_oran = (tyt_tamamlanan / tyt_toplam * 100) if tyt_toplam > 0 else 0
        
        # 2. AYT Konu tamamlanma oranı
        cursor.execute('''
            SELECT 
                COUNT(k.id) as toplam,
                SUM(CASE WHEN k.tamamlandi = 1 THEN 1 ELSE 0 END) as tamamlanan
            FROM konular k
            JOIN dersler d ON k.ders_id = d.id
            WHERE d.ders_turu = 'AYT'
        ''')
        ayt_konu = cursor.fetchone()
        ayt_toplam = ayt_konu['toplam'] if ayt_konu['toplam'] else 1
        ayt_tamamlanan = ayt_konu['tamamlanan'] if ayt_konu['tamamlanan'] else 0
        ayt_oran = (ayt_tamamlanan / ayt_toplam * 100) if ayt_toplam > 0 else 0
        
        # 3. TYT Deneme ortalaması
        cursor.execute('''
            SELECT AVG(toplam_net) as ortalama
            FROM (
                SELECT d.id, SUM(dd.dogru - (dd.yanlis * 0.25)) as toplam_net
                FROM denemeler d
                JOIN deneme_detay dd ON d.id = dd.deneme_id
                WHERE d.deneme_turu = 'TYT'
                GROUP BY d.id
            )
        ''')
        tyt_deneme = cursor.fetchone()
        tyt_deneme_avg = tyt_deneme['ortalama'] if tyt_deneme and tyt_deneme['ortalama'] else 0
        
        # 4. AYT Deneme ortalaması
        cursor.execute('''
            SELECT AVG(toplam_net) as ortalama
            FROM (
                SELECT d.id, SUM(dd.dogru - (dd.yanlis * 0.25)) as toplam_net
                FROM denemeler d
                JOIN deneme_detay dd ON d.id = dd.deneme_id
                WHERE d.deneme_turu = 'AYT'
                GROUP BY d.id
            )
        ''')
        ayt_deneme = cursor.fetchone()
        ayt_deneme_avg = ayt_deneme['ortalama'] if ayt_deneme and ayt_deneme['ortalama'] else 0
        
        # 5. Tahmin hesaplama
        # TYT: 120 soru max, AYT: 80 soru max
        # Formül: (Deneme Performansı * 0.6) + (Konu Oranı * Deneme Ortalama / Max * 0.4)
        tyt_max = 120
        ayt_max = 80
        
        tyt_net = (tyt_deneme_avg * 0.6) + ((tyt_oran / 100) * tyt_deneme_avg * 0.4)
        ayt_net = (ayt_deneme_avg * 0.6) + ((ayt_oran / 100) * ayt_deneme_avg * 0.4)
        
        # Sıfır kontrolü - en azından konu oranına göre bir şey göster
        if tyt_net == 0 and tyt_oran > 0:
            tyt_net = (tyt_oran / 100) * tyt_max * 0.5
        
        if ayt_net == 0 and ayt_oran > 0:
            ayt_net = (ayt_oran / 100) * ayt_max * 0.5
        
        # 6. Kartları güncelle
        self.tyt_card['net_label'].text = f"{tyt_net:.1f}"
        self.tyt_card['info_label'].text = f"Konu: %{tyt_oran:.0f} | Deneme Ort: {tyt_deneme_avg:.1f}"
        
        self.ayt_card['net_label'].text = f"{ayt_net:.1f}"
        self.ayt_card['info_label'].text = f"Konu: %{ayt_oran:.0f} | Deneme Ort: {ayt_deneme_avg:.1f}"
        
        # 7. Ders detaylarını göster
        self.show_ders_details()
        
        conn.close()
    
    def show_ders_details(self):
        """Ders bazlı detayları göster"""
        self.ders_container.clear_widgets()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.ders_adi,
                d.ders_turu,
                COUNT(k.id) as toplam_konu,
                SUM(CASE WHEN k.tamamlandi = 1 THEN 1 ELSE 0 END) as tamamlanan_konu
            FROM dersler d
            LEFT JOIN konular k ON d.id = k.ders_id
            GROUP BY d.id, d.ders_adi, d.ders_turu
            ORDER BY d.sira
        ''')
        
        dersler = cursor.fetchall()
        
        for ders in dersler:
            toplam = ders['toplam_konu'] if ders['toplam_konu'] else 1
            tamamlanan = ders['tamamlanan_konu'] if ders['tamamlanan_konu'] else 0
            yuzde = int((tamamlanan / toplam * 100)) if toplam > 0 else 0
            
            color = '#3498db' if ders['ders_turu'] == 'TYT' else '#27ae60'
            
            card = MDCard(
                orientation='vertical',
                size_hint_y=None,
                height=80,
                padding=10,
                md_bg_color=color,
                radius=[8]
            )
            
            name_label = MDLabel(
                text=f"{ders['ders_adi']} ({ders['ders_turu']})",
                font_size='14sp',
                bold=True,
                color=(1, 1, 1, 1)
            )
            
            progress_label = MDLabel(
                text=f"İlerleme: {tamamlanan}/{toplam} (%{yuzde})",
                font_size='12sp',
                color=(1, 1, 1, 1)
            )
            
            card.add_widget(name_label)
            card.add_widget(progress_label)
            
            self.ders_container.add_widget(card)
        
        conn.close()
