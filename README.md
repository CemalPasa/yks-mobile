# YKS Mobil Takip Uygulaması

YKS (Yükseköğretim Kurumları Sınavı) için mobil takip uygulaması. Kivy/KivyMD ile geliştirilmiştir.

## Özellikler

- 📊 TYT/AYT istatistikleri
- 📚 Konu takibi
- 📅 Haftalık çalışma programı
- 📝 Deneme sonuçları
- 📈 Detaylı istatistikler

## Kurulum

### Geliştirme Ortamı

```bash
pip install -r requirements.txt
python main.py
```

### APK Oluşturma

APK dosyası oluşturmak için Linux/Mac ortamında Buildozer kullanmanız gerekmektedir.

#### Linux/Mac'te APK Oluşturma:

1. Buildozer'ı yükleyin:
```bash
pip install buildozer
```

2. Android geliştirme araçlarını yükleyin:
```bash
# Ubuntu/Debian için
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# macOS için (Homebrew ile)
brew install autoconf automake libtool pkg-config
brew install --cask adoptopenjdk
```

3. APK oluşturun:
```bash
buildozer android debug
```

4. APK dosyası `bin/` klasöründe oluşturulacaktır.

#### Windows'ta APK Oluşturma:

Windows'ta direkt APK oluşturulamaz. Şu seçenekler var:

1. **WSL2 (Windows Subsystem for Linux) Kullanımı:**
   - WSL2'yi etkinleştirin
   - Ubuntu kurulumu yapın
   - Yukarıdaki Linux adımlarını izleyin

2. **Docker Kullanımı:**
```bash
# Buildozer Docker image ile
docker run -v "%CD%:/home/user/app" kivy/buildozer android debug
```

3. **Sanal Makine (VirtualBox/VMware) ile Ubuntu:**
   - Ubuntu VM kurun
   - Projeyi VM'e kopyalayın
   - Yukarıdaki Linux adımlarını izleyin

4. **GitHub Actions ile Online Build:**
   - GitHub'a yükleyin
   - Actions workflow ile otomatik build

## Mimari

```
yks-mobile/
├── main.py                 # Ana uygulama
├── database/
│   └── db_manager.py      # Veritabanı yöneticisi
├── screens/
│   ├── dashboard.py       # Ana sayfa
│   ├── konular.py         # Konu takibi
│   ├── program.py         # Haftalık program
│   ├── deneme.py          # Deneme sonuçları
│   └── istatistik.py      # İstatistikler
├── buildozer.spec         # APK yapılandırması
└── requirements.txt       # Python bağımlılıkları
```

## Veritabanı

SQLite veritabanı kullanılmaktadır. İlk çalıştırmada otomatik olarak oluşturulur.

### Tablolar:
- `dersler` - Ders bilgileri (TYT/AYT)
- `konular` - Konu takibi
- `haftalik_program` - Haftalık çalışma programı
- `denemeler` - Deneme sınavları
- `deneme_detay` - Deneme sonuç detayları
- `gunluk_sorular` - Günlük soru çözümleri
- `calisma_saatleri` - Çalışma süreleri

## Geliştirme

Uygulama 5 ana ekrandan oluşmaktadır:

1. **Dashboard** - Genel bakış ve bugünün görevleri
2. **Konular** - TYT/AYT konu takibi
3. **Program** - Haftalık çalışma programı
4. **Deneme** - Deneme sınav sonuçları
5. **İstatistik** - Detaylı analizler

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
