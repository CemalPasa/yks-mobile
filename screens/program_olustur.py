"""
Program Oluşturma Ekranı
Otomatik çalışma programı oluşturma
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.picker import MDDatePicker
from kivy.uix.scrollview import ScrollView
from datetime import datetime, timedelta
import json


class ProgramOlusturScreen(MDScreen):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.dialog = None
        self.build_ui()
    
    def build_ui(self):
        """Arayüzü oluştur"""
        layout = MDBoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Başlık
        title = MDLabel(
            text='Program Oluştur',
            font_size='20sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(title)
        
        # Form
        scroll = ScrollView()
        form = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            size_hint_y=None,
            padding=10
        )
        form.bind(minimum_height=form.setter('height'))
        
        # Günlük çalışma saati
        form.add_widget(MDLabel(text='Günlük Çalışma Saati:', font_size='16sp', size_hint_y=None, height=30))
        self.gunluk_saat = MDTextField(
            hint_text='Saat (örn: 8)',
            input_filter='int',
            size_hint_y=None,
            height=50
        )
        form.add_widget(self.gunluk_saat)
        
        # Sınav tarihi
        form.add_widget(MDLabel(text='YKS Sınav Tarihi:', font_size='16sp', size_hint_y=None, height=30))
        self.sinav_tarihi_btn = MDRaisedButton(
            text='Tarih Seç',
            size_hint_y=None,
            height=50,
            on_release=self.show_date_picker
        )
        form.add_widget(self.sinav_tarihi_btn)
        
        # Çalışma günleri
        form.add_widget(MDLabel(text='Çalışma Günleri:', font_size='16sp', size_hint_y=None, height=30))
        
        self.gun_checkboxes = {}
        gunler = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        
        for gun in gunler:
            gun_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            checkbox = MDTextField(
                hint_text=gun,
                text='✓',
                disabled=True,
                size_hint_x=0.8
            )
            self.gun_checkboxes[gun] = checkbox
            gun_box.add_widget(checkbox)
            form.add_widget(gun_box)
        
        # Program oluştur butonu
        create_btn = MDRaisedButton(
            text='Program Oluştur',
            size_hint_y=None,
            height=60,
            md_bg_color=(0.2, 0.6, 0.86, 1),
            on_release=self.create_program
        )
        form.add_widget(create_btn)
        
        # Mevcut programı göster
        form.add_widget(MDLabel(text='', size_hint_y=None, height=20))
        self.program_status = MDLabel(
            text='Henüz program oluşturulmamış',
            font_size='14sp',
            size_hint_y=None,
            height=40
        )
        form.add_widget(self.program_status)
        
        scroll.add_widget(form)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        # Mevcut program var mı kontrol et
        self.check_existing_program()
    
    def show_date_picker(self, *args):
        """Tarih seçici göster"""
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()
    
    def on_date_save(self, instance, value, date_range):
        """Tarih seçildiğinde"""
        self.selected_date = value
        self.sinav_tarihi_btn.text = value.strftime('%d.%m.%Y')
    
    def create_program(self, *args):
        """Program oluştur"""
        if not self.gunluk_saat.text:
            self.show_error('Günlük çalışma saati giriniz!')
            return
        
        if not hasattr(self, 'selected_date'):
            self.show_error('Sınav tarihini seçiniz!')
            return
        
        try:
            gunluk_saat = int(self.gunluk_saat.text)
            
            if gunluk_saat < 1 or gunluk_saat > 16:
                self.show_error('Günlük çalışma saati 1-16 arası olmalı!')
                return
            
            # Çalışma günlerini al
            calisma_gunleri = [gun for gun, cb in self.gun_checkboxes.items() if cb.text == '✓']
            
            # Program oluştur
            self.generate_program(gunluk_saat, calisma_gunleri, self.selected_date)
            
            self.show_success('Program başarıyla oluşturuldu!')
            self.check_existing_program()
            
        except ValueError:
            self.show_error('Geçersiz saat değeri!')
    
    def generate_program(self, gunluk_saat, calisma_gunleri, sinav_tarihi):
        """Otomatik program oluştur"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Önce eski programı sil
        cursor.execute('DELETE FROM haftalik_program')
        
        # Bugünden sınav tarihine kadar günler
        bugun = datetime.now().date()
        toplam_gun = (sinav_tarihi - bugun).days
        
        # Dersleri ve konuları al
        cursor.execute('''
            SELECT d.id, d.ders_adi, COUNT(k.id) as konu_sayisi
            FROM dersler d
            LEFT JOIN konular k ON d.id = k.ders_id
            GROUP BY d.id
            ORDER BY d.sira
        ''')
        dersler = cursor.fetchall()
        
        # Her gün için program oluştur
        current_date = bugun
        gun_mapping = {
            'Monday': 'Pazartesi',
            'Tuesday': 'Salı',
            'Wednesday': 'Çarşamba',
            'Thursday': 'Perşembe',
            'Friday': 'Cuma',
            'Saturday': 'Cumartesi',
            'Sunday': 'Pazar'
        }
        
        ders_index = 0
        
        for i in range(min(toplam_gun, 90)):  # Max 90 gün
            gun_adi = gun_mapping.get(current_date.strftime('%A'), 'Pazartesi')
            
            if gun_adi in calisma_gunleri:
                # Günlük saatleri böl
                saat_per_ders = gunluk_saat // len(dersler) if len(dersler) > 0 else 1
                current_time = 9  # Saat 09:00'da başla
                
                # Her ders için slot oluştur
                for j in range(len(dersler)):
                    if current_time >= 22:  # 22:00'dan sonra çalışma
                        break
                    
                    ders = dersler[ders_index % len(dersler)]
                    
                    baslangic = f"{current_time:02d}:00"
                    bitis = f"{(current_time + saat_per_ders):02d}:00"
                    
                    cursor.execute('''
                        INSERT INTO haftalik_program
                        (tarih, gun, saat_baslangic, saat_bitis, ders_id, konu_adi, tamamlandi)
                        VALUES (?, ?, ?, ?, ?, ?, 0)
                    ''', (
                        current_date.strftime('%Y-%m-%d'),
                        gun_adi,
                        baslangic,
                        bitis,
                        ders[0],
                        f"{ders[1]} Çalışması"
                    ))
                    
                    current_time += saat_per_ders
                    ders_index += 1
            
            current_date += timedelta(days=1)
        
        conn.commit()
        conn.close()
    
    def check_existing_program(self):
        """Mevcut program kontrolü"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM haftalik_program')
        result = cursor.fetchone()
        
        if result and result['count'] > 0:
            self.program_status.text = f"✓ Mevcut program: {result['count']} ders saati"
        else:
            self.program_status.text = 'Henüz program oluşturulmamış'
        
        conn.close()
    
    def show_error(self, message):
        """Hata mesajı göster"""
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="TAMAM",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.text = message
        self.dialog.open()
    
    def show_success(self, message):
        """Başarı mesajı göster"""
        if not self.dialog:
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="TAMAM",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
        else:
            self.dialog.text = message
        self.dialog.open()
