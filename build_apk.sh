#!/bin/bash

# YKS Mobil APK Oluşturma Scripti
# WSL2 Ubuntu için otomatik kurulum ve derleme

set -e  # Hata durumunda dur

echo "======================================"
echo "YKS Mobil APK Oluşturucu"
echo "======================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Java kontrolü
check_java() {
    if java -version 2>&1 >/dev/null | grep -q "version" ; then
        print_success "Java kurulu"
        return 0
    else
        return 1
    fi
}

# Buildozer kontrolü
check_buildozer() {
    if command -v buildozer &> /dev/null; then
        print_success "Buildozer kurulu"
        return 0
    else
        return 1
    fi
}

# Ana script
echo "Sistem kontrolleri yapılıyor..."
echo ""

# 1. Java kontrolü
if ! check_java; then
    print_warning "Java kurulu değil, yükleniyor..."
    sudo apt update
    sudo apt install -y openjdk-17-jdk
    print_success "Java kuruldu"
fi

# 2. Gerekli paketler
print_warning "Gerekli sistem paketleri kontrol ediliyor..."
sudo apt install -y \
    python3 python3-pip git zip unzip \
    build-essential libssl-dev libffi-dev \
    libncurses5-dev libncursesw5-dev \
    libtinfo5 zlib1g-dev cmake autoconf libtool pkg-config

print_success "Sistem paketleri hazır"

# 3. Buildozer kontrolü
if ! check_buildozer; then
    print_warning "Buildozer kurulu değil, yükleniyor..."
    pip3 install --upgrade pip
    pip3 install buildozer cython
    
    # PATH'e ekle
    export PATH=$PATH:~/.local/bin
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
    
    print_success "Buildozer kuruldu"
fi

echo ""
echo "======================================"
echo "APK Oluşturuluyor..."
echo "======================================"
echo ""

print_warning "İlk derleme 30-60 dakika sürebilir (Android SDK/NDK indirilecek)"
echo ""

# APK oluştur
buildozer android debug

echo ""
echo "======================================"
print_success "APK başarıyla oluşturuldu!"
echo "======================================"
echo ""

# APK konumunu göster
APK_PATH=$(find bin -name "*.apk" -type f | head -1)

if [ -n "$APK_PATH" ]; then
    APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
    echo "APK Dosyası: $APK_PATH"
    echo "Boyut: $APK_SIZE"
    echo ""
    
    # Windows masaüstüne kopyala
    DESKTOP_PATH="/mnt/c/Users/$USER/Desktop"
    if [ -d "$DESKTOP_PATH" ]; then
        print_warning "APK masaüstüne kopyalanıyor..."
        cp "$APK_PATH" "$DESKTOP_PATH/"
        print_success "APK masaüstüne kopyalandı: $DESKTOP_PATH/"
    fi
    
    # WSL yolu
    echo ""
    echo "WSL'den erişmek için:"
    echo "  $(pwd)/$APK_PATH"
    echo ""
    echo "Windows'tan erişmek için:"
    echo "  \\\\wsl\$\\Ubuntu\\home\\$USER\\$(pwd | sed 's/\/home\///')\\$APK_PATH"
fi

echo ""
print_success "İşlem tamamlandı!"
echo ""
echo "Telefona kurmak için:"
echo "1. APK'yı telefona kopyalayın"
echo "2. Ayarlar → Güvenlik → Bilinmeyen Kaynaklar'ı açın"
echo "3. APK dosyasına tıklayın"
echo ""
