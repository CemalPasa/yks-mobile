"""
Günlük Soru Hedefi Ekranı
Soru çözme takibi
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, TwoLineListItem
from kivy.uix.scrollview import ScrollView
from datetime import datetime


class GunlukSoruScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.dialog = None
        self.selected_ders_id = None
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Başlık
        title = MDLabel(
            text='Günlük Soru Hedefi',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title)
        
        # Özet kartlar
        summary_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=10)
        
        # Bugün
        self.today_card = self.create_summary_card('Bugün', '0 / 0', '#3498db')
        summary_box.add_widget(self.today_card)
        
        # Bu Hafta
        self.week_card = self.create_summary_card('Bu Hafta', '0 Soru', '#27ae60')
        summary_box.add_widget(self.week_card)
        
        layout.add_widget(summary_box)
        
        # Hızlı giriş butonu
        quick_btn = MDRaisedButton(
            text='+ Hızlı Soru Giriş',
            size_hint_y=None,
            height=50,
            md_bg_color=(0.9, 0.5, 0.13, 1),
            on_release=self.show_quick_entry
        )
        layout.add_widget(quick_btn)
        
        # Bugünün dersleri
        today_label = MDLabel(
            text="Bugünün Dersleri",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(today_label)
        
        # Liste
        scroll = ScrollView()
        self.ders_list = MDList()
        scroll.add_widget(self.ders_list)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
        self.load_data()
    
    def create_summary_card(self, title, value, color):
        """Özet kartı"""
        card = MDCard(
            orientation='vertical',
            size_hint_x=0.5,
            padding=10,
            md_bg_color=color,
            radius=[10]
        )
        
        title_label = MDLabel(
            text=title,
            font_size='14sp',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=20
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
    
    def load_data(self):
        """Verileri yükle"""
        # Özet verileri
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Bugün
        cursor.execute('''
            SELECT SUM(cozulen) as cozulen, SUM(hedef) as hedef
            FROM gunluk_sorular
            WHERE tarih = ?
        ''', (today,))
        today_data = cursor.fetchone()
        
        if today_data and today_data['cozulen']:
            self.today_card.children[0].text = f"{today_data['cozulen']} / {today_data['hedef']}"
        
        # Dersleri listele
        self.ders_list.clear_widgets()
        
        cursor.execute('''
            SELECT 
                d.id,
                d.ders_adi,
                COALESCE(g.cozulen, 0) as cozulen,
                COALESCE(g.hedef, 0) as hedef,
                COALESCE(g.dogru, 0) as dogru,
                COALESCE(g.yanlis, 0) as yanlis
            FROM dersler d
            LEFT JOIN gunluk_sorular g ON d.id = g.ders_id AND g.tarih = ?
            ORDER BY d.sira
        ''', (today,))
        
        dersler = cursor.fetchall()
        
        for ders in dersler:
            net = ders['dogru'] - (ders['yanlis'] * 0.25)
            item = TwoLineListItem(
                text=ders['ders_adi'],
                secondary_text=f"Çözülen: {ders['cozulen']} | Net: {net:.2f}",
                on_release=lambda x, d=ders: self.show_ders_dialog(d)
            )
            self.ders_list.add_widget(item)
        
        conn.close()
    
    def show_quick_entry(self, *args):
        """Hızlı giriş dialog"""
        if not self.dialog:
            content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=300)
            
            # Ders seçimi
            content.add_widget(MDLabel(text='Ders:', size_hint_y=None, height=30))
            
            self.ders_dropdown = MDTextField(
                hint_text='Ders Adı',
                size_hint_y=None,
                height=50
            )
            content.add_widget(self.ders_dropdown)
            
            # Doğru
            content.add_widget(MDLabel(text='Doğru:', size_hint_y=None, height=30))
            self.dogru_input = MDTextField(
                hint_text='0',
                input_filter='int',
                size_hint_y=None,
                height=50
            )
            content.add_widget(self.dogru_input)
            
            # Yanlış
            content.add_widget(MDLabel(text='Yanlış:', size_hint_y=None, height=30))
            self.yanlis_input = MDTextField(
                hint_text='0',
                input_filter='int',
                size_hint_y=None,
                height=50
            )
            content.add_widget(self.yanlis_input)
            
            self.dialog = MDDialog(
                title='Hızlı Soru Giriş',
                type='custom',
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text='İPTAL',
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text='KAYDET',
                        on_release=self.save_quick_entry
                    )
                ]
            )
        
        self.dialog.open()
    
    def save_quick_entry(self, *args):
        """Hızlı girişi kaydet"""
        # Basitleştirilmiş versiyon - gerçek uygulamada ders seçimi yapılmalı
        self.dialog.dismiss()
        self.load_data()
    
    def show_ders_dialog(self, ders):
        """Ders detay dialog"""
        self.selected_ders_id = ders['id']
        
        content = MDBoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=250)
        
        content.add_widget(MDLabel(text=f"Ders: {ders['ders_adi']}", size_hint_y=None, height=30))
        
        # Doğru
        content.add_widget(MDLabel(text='Doğru:', size_hint_y=None, height=25))
        self.edit_dogru = MDTextField(
            text=str(ders['dogru']),
            input_filter='int',
            size_hint_y=None,
            height=50
        )
        content.add_widget(self.edit_dogru)
        
        # Yanlış
        content.add_widget(MDLabel(text='Yanlış:', size_hint_y=None, height=25))
        self.edit_yanlis = MDTextField(
            text=str(ders['yanlis']),
            input_filter='int',
            size_hint_y=None,
            height=50
        )
        content.add_widget(self.edit_yanlis)
        
        dialog = MDDialog(
            title='Soru Güncelle',
            type='custom',
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text='İPTAL',
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text='KAYDET',
                    on_release=lambda x: self.save_ders_update(dialog)
                )
            ]
        )
        dialog.open()
    
    def save_ders_update(self, dialog):
        """Ders güncellemesini kaydet"""
        today = datetime.now().strftime('%Y-%m-%d')
        dogru = int(self.edit_dogru.text) if self.edit_dogru.text else 0
        yanlis = int(self.edit_yanlis.text) if self.edit_yanlis.text else 0
        cozulen = dogru + yanlis
        net = dogru - (yanlis * 0.25)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Var mı kontrol et
        cursor.execute('''
            SELECT id FROM gunluk_sorular
            WHERE tarih = ? AND ders_id = ?
        ''', (today, self.selected_ders_id))
        
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE gunluk_sorular
                SET dogru = ?, yanlis = ?, cozulen = ?, net = ?
                WHERE id = ?
            ''', (dogru, yanlis, cozulen, net, existing['id']))
        else:
            cursor.execute('''
                INSERT INTO gunluk_sorular
                (tarih, ders_id, dogru, yanlis, cozulen, net, hedef)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (today, self.selected_ders_id, dogru, yanlis, cozulen, net, cozulen))
        
        conn.commit()
        conn.close()
        
        dialog.dismiss()
        self.load_data()
