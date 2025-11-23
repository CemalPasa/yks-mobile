"""
YKS Mobil - Veritabanı Yöneticisi
SQLite veritabanı işlemleri
"""

import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path='yks_mobile.db'):
        """Veritabanı bağlantısını başlat"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Veritabanı bağlantısı oluştur"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Dersler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dersler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ders_adi TEXT NOT NULL,
                ders_turu TEXT NOT NULL,
                sira INTEGER
            )
        ''')
        
        # Konular tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS konular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ders_id INTEGER,
                konu_adi TEXT NOT NULL,
                tamamlandi INTEGER DEFAULT 0,
                tamamlanma_tarihi TEXT,
                FOREIGN KEY (ders_id) REFERENCES dersler (id)
            )
        ''')
        
        # Haftalık program tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS haftalik_program (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gun TEXT NOT NULL,
                saat TEXT NOT NULL,
                ders_id INTEGER,
                konu_id INTEGER,
                tamamlandi INTEGER DEFAULT 0,
                FOREIGN KEY (ders_id) REFERENCES dersler (id),
                FOREIGN KEY (konu_id) REFERENCES konular (id)
            )
        ''')
        
        # Denemeler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS denemeler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deneme_adi TEXT NOT NULL,
                tarih TEXT NOT NULL,
                deneme_turu TEXT NOT NULL
            )
        ''')
        
        # Deneme detay tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deneme_detay (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deneme_id INTEGER,
                ders_id INTEGER,
                dogru INTEGER DEFAULT 0,
                yanlis INTEGER DEFAULT 0,
                bos INTEGER DEFAULT 0,
                FOREIGN KEY (deneme_id) REFERENCES denemeler (id),
                FOREIGN KEY (ders_id) REFERENCES dersler (id)
            )
        ''')
        
        # Günlük sorular tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gunluk_sorular (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                ders_id INTEGER,
                dogru INTEGER DEFAULT 0,
                yanlis INTEGER DEFAULT 0,
                bos INTEGER DEFAULT 0,
                FOREIGN KEY (ders_id) REFERENCES dersler (id)
            )
        ''')
        
        # Çalışma saatleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calisma_saatleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                sure INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        
        # Varsayılan dersleri ekle
        self._init_default_courses(cursor)
        conn.commit()
        conn.close()
    
    def _init_default_courses(self, cursor):
        """Varsayılan dersleri veritabanına ekle"""
        cursor.execute('SELECT COUNT(*) as count FROM dersler')
        if cursor.fetchone()['count'] == 0:
            courses = [
                # TYT Dersleri (id: 1-10)
                ('Türkçe', 'TYT', 1),
                ('Matematik', 'TYT', 2),
                ('Fizik', 'TYT', 3),
                ('Kimya', 'TYT', 4),
                ('Biyoloji', 'TYT', 5),
                ('Tarih-1', 'TYT', 6),
                ('Coğrafya-1', 'TYT', 7),
                ('Din Kültürü', 'TYT', 8),
                ('Felsefe', 'TYT', 9),
                ('Dil ve Anlatım', 'TYT', 10),
                # AYT Dersleri (id: 11-16)
                ('Edebiyat', 'AYT', 11),
                ('Tarih-1 (AYT)', 'AYT', 12),
                ('Coğrafya-1 (AYT)', 'AYT', 13),
                ('Matematik (AYT)', 'AYT', 14),
                ('Fizik (AYT)', 'AYT', 15),
                ('Kimya (AYT)', 'AYT', 16)
            ]
            
            cursor.executemany(
                'INSERT INTO dersler (ders_adi, ders_turu, sira) VALUES (?, ?, ?)',
                courses
            )
    
    # Dashboard sorguları
    def get_tyt_stats(self):
        """TYT istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN k.tamamlandi = 1 THEN 1 END) as tamamlanan,
                COUNT(*) as toplam
            FROM konular k
            JOIN dersler d ON k.ders_id = d.id
            WHERE d.ders_turu = 'TYT'
        ''')
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else {'tamamlanan': 0, 'toplam': 0}
    
    def get_ayt_stats(self):
        """AYT istatistiklerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN k.tamamlandi = 1 THEN 1 END) as tamamlanan,
                COUNT(*) as toplam
            FROM konular k
            JOIN dersler d ON k.ders_id = d.id
            WHERE d.ders_turu = 'AYT'
        ''')
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else {'tamamlanan': 0, 'toplam': 0}
    
    def get_today_tasks(self):
        """Bugünün görevlerini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
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
        
        cursor.execute('''
            SELECT 
                hp.id,
                hp.saat,
                d.ders_adi,
                k.konu_adi,
                hp.tamamlandi
            FROM haftalik_program hp
            JOIN dersler d ON hp.ders_id = d.id
            LEFT JOIN konular k ON hp.konu_id = k.id
            WHERE hp.gun = ?
            ORDER BY hp.saat
        ''', (today_tr,))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # Konular ekranı sorguları
    def get_courses_by_type(self, ders_turu):
        """Ders türüne göre dersleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.id,
                d.ders_adi,
                COUNT(k.id) as toplam_konu,
                COUNT(CASE WHEN k.tamamlandi = 1 THEN 1 END) as tamamlanan_konu
            FROM dersler d
            LEFT JOIN konular k ON d.id = k.ders_id
            WHERE d.ders_turu = ?
            GROUP BY d.id
            ORDER BY d.sira
        ''', (ders_turu,))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # Program ekranı sorguları
    def get_weekly_program(self):
        """Haftalık programı getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                hp.id,
                hp.gun,
                hp.saat,
                d.ders_adi,
                k.konu_adi,
                hp.tamamlandi
            FROM haftalik_program hp
            JOIN dersler d ON hp.ders_id = d.id
            LEFT JOIN konular k ON hp.konu_id = k.id
            ORDER BY 
                CASE hp.gun
                    WHEN 'Pazartesi' THEN 1
                    WHEN 'Salı' THEN 2
                    WHEN 'Çarşamba' THEN 3
                    WHEN 'Perşembe' THEN 4
                    WHEN 'Cuma' THEN 5
                    WHEN 'Cumartesi' THEN 6
                    WHEN 'Pazar' THEN 7
                END,
                hp.saat
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # Deneme ekranı sorguları
    def get_denemeler_by_type(self, deneme_turu):
        """Deneme türüne göre denemeleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.id,
                d.deneme_adi,
                d.tarih,
                SUM(dd.dogru - (dd.yanlis * 0.25)) as toplam_net
            FROM denemeler d
            LEFT JOIN deneme_detay dd ON d.id = dd.deneme_id
            WHERE d.deneme_turu = ?
            GROUP BY d.id
            ORDER BY d.tarih DESC
        ''', (deneme_turu,))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    
    # İstatistik ekranı sorguları
    def get_total_study_hours(self):
        """Toplam çalışma saatini getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(sure) as toplam FROM calisma_saatleri')
        result = cursor.fetchone()
        conn.close()
        return result['toplam'] if result and result['toplam'] else 0
    
    def get_completed_topics_count(self):
        """Tamamlanan konu sayısını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM konular WHERE tamamlandi = 1')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    def get_total_exam_count(self):
        """Toplam deneme sayısını getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM denemeler')
        result = cursor.fetchone()
        conn.close()
        return result['count'] if result else 0
    
    def get_recent_exams(self, limit=5):
        """Son denemeleri getir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                d.deneme_adi,
                d.tarih,
                d.deneme_turu,
                SUM(dd.dogru - (dd.yanlis * 0.25)) as toplam_net
            FROM denemeler d
            LEFT JOIN deneme_detay dd ON d.id = dd.deneme_id
            GROUP BY d.id
            ORDER BY d.tarih DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
