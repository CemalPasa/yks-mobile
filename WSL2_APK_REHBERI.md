# WSL2 ile APK Oluşturma Rehberi

Bu rehber Windows'ta WSL2 kullanarak YKS Mobil uygulamasını APK'ya dönüştürmenizi sağlar.

## Adım 1: WSL2 Kurulumu

### WSL2'yi Etkinleştirin

1. **PowerShell'i Yönetici olarak açın** ve şu komutu çalıştırın:

```powershell
wsl --install
```

2. Bilgisayarınızı yeniden başlatın.

3. Yeniden başladıktan sonra Ubuntu otomatik olarak kurulacak ve sizden kullanıcı adı/şifre isteyecek.

### Alternatif Kurulum (Manuel)

Eğer `wsl --install` çalışmazsa:

```powershell
# WSL'i etkinleştir
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Virtual Machine Platform'u etkinleştir
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Yeniden başlat, sonra WSL2'yi varsayılan yap
wsl --set-default-version 2

# Ubuntu kur
wsl --install -d Ubuntu-22.04
```

## Adım 2: Proje Dosyalarını WSL'e Kopyalama

### Yöntem 1: Windows Explorer'dan (Kolay)

1. Windows Explorer'ı açın
2. Adres çubuğuna yazın: `\\wsl$\Ubuntu\home\KULLANICI_ADINIZ`
3. `yks-mobile` klasörünü buraya kopyalayın

### Yöntem 2: Komut Satırından

WSL terminalini açın ve:

```bash
# Windows'taki yolu kopyala
cp -r /mnt/c/Users/Demot/OneDrive/Masaüstü/yks/yks-mobile ~/yks-mobile
cd ~/yks-mobile
```

## Adım 3: Gerekli Paketleri Yükleyin

WSL Ubuntu terminalinde:

```bash
# Sistem paketlerini güncelle
sudo apt update
sudo apt upgrade -y

# Python ve geliştirme araçlarını yükle
sudo apt install -y python3 python3-pip git zip unzip

# Java (Android için gerekli)
sudo apt install -y openjdk-17-jdk

# Diğer gerekli kütüphaneler
sudo apt install -y build-essential libssl-dev libffi-dev \
    libncurses5-dev libncursesw5-dev \
    libtinfo5 zlib1g-dev cmake autoconf libtool pkg-config

# Python paketlerini yükle
pip3 install --upgrade pip
pip3 install buildozer cython
```

## Adım 4: Buildozer İlk Kurulum

```bash
cd ~/yks-mobile

# İlk kez buildozer çalıştırıldığında Android SDK/NDK indirilir (yaklaşık 2-3 GB)
buildozer android debug
```

**Not:** İlk çalıştırma 30-60 dakika sürebilir çünkü:
- Android SDK indirilir
- Android NDK indirilir
- Python-for-Android derlenir

## Adım 5: APK Oluşturma

```bash
cd ~/yks-mobile

# Debug APK oluştur (geliştirme için)
buildozer android debug

# Release APK oluştur (yayınlamak için)
buildozer android release
```

APK dosyası şurada oluşturulur:
```
~/yks-mobile/bin/ykstakip-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

## Adım 6: APK'yı Windows'a Kopyalama

### WSL'den Windows'a:

```bash
# APK'yı masaüstüne kopyala
cp bin/*.apk /mnt/c/Users/Demot/Desktop/
```

veya Windows Explorer'dan `\\wsl$\Ubuntu\home\KULLANICI_ADINIZ\yks-mobile\bin\` yoluna gidin.

## Hata Çözümleri

### "Permission denied" hatası:
```bash
sudo chmod +x ~/.buildozer/android/platform/android-sdk/tools/bin/*
```

### Java versiyonu hatası:
```bash
sudo update-alternatives --config java
# Java 17'yi seçin
```

### Disk alanı yetersiz:
```bash
# Buildozer cache'i temizle
buildozer android clean
rm -rf .buildozer
```

### "Command not found: buildozer":
```bash
# PATH'e ekle
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

## Telefona Kurulum

1. APK'yı telefona USB ile kopyalayın veya e-postayla gönderin
2. Telefonda **Ayarlar → Güvenlik → Bilinmeyen Kaynaklar**'ı açın
3. APK dosyasına tıklayıp kurun

## Yararlı Komutlar

```bash
# Buildozer versiyonu
buildozer --version

# Temizlik yap ve yeniden derle
buildozer android clean
buildozer android debug

# Logları görüntüle
buildozer android logcat

# Telefona yükle ve çalıştır (USB debugging açık olmalı)
buildozer android deploy run
```

## Performans İpuçları

- **SSD kullanın:** Derleme çok daha hızlı olur
- **RAM:** En az 8 GB önerilir
- **İlk derleme:** Sabırlı olun, sonrakiler çok daha hızlı

## buildozer.spec Önemli Ayarlar

```ini
# Sürüm güncelleme
version = 1.1

# Daha fazla mimari (daha büyük APK)
android.archs = arm64-v8a,armeabi-v7a,x86_64

# Sadece 64-bit (daha küçük APK, yeni cihazlar)
android.archs = arm64-v8a

# Uygulama ikonu (eklemek için)
icon.filename = %(source.dir)s/icon.png

# Splash ekranı
presplash.filename = %(source.dir)s/splash.png
```

## Sorun mu yaşıyorsunuz?

1. `buildozer.spec` dosyasını kontrol edin
2. `buildozer android clean` ile temizleyin
3. `.buildozer` klasörünü silin ve yeniden deneyin
4. WSL'i yeniden başlatın: `wsl --shutdown` (PowerShell'de)

---

**Önemli:** İlk APK derlemesi uzun sürer ama sonraki derlemeler 2-5 dakika içinde tamamlanır!
