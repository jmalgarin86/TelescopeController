#!/bin/bash

echo "############################################################"
echo "Code for setting up astropi"
echo "J.M. Algarín"
echo "2025.06.21"
echo "############################################################"

echo "Press ENTER to continue..."
read
echo ""

ASTRO_INDEX_URL="https://upvedues-my.sharepoint.com/:u:/g/personal/joalgui2_upv_edu_es/EfNo7Z7rzZ9OhoUhWiJPmJMBCG7nbZb7DdFH6qczrXVf7A?e=HqF1ox&download=1"
ASTRO_TARXZ="astrometry.tar.xz"

# Update package list and upgrade packages
echo "[1] Upgrading installed packages..."
sudo apt update
sudo apt upgrade -y
echo "✅ Packages upgraded."
echo " "

 # Install development and library packages
echo "[2] Installing required packages..."
sudo apt install -y git cdbs dkms cmake fxload libev-dev libgps-dev libgsl-dev libraw-dev libusb-dev \
 zlib1g-dev libftdi-dev libjpeg-dev libkrb5-dev libnova-dev libtiff-dev libfftw3-dev librtlsdr-dev \
 libcfitsio-dev libgphoto2-dev build-essential libusb-1.0-0-dev libdc1394-dev libboost-regex-dev \
 libcurl4-gnutls-dev libtheora-dev
echo "✅ Packages installed."
echo " "

# Clone indilib
echo "[3] Cloning indilib"
mkdir ~/Projects
cd ~/Projects
git clone --depth 1 https://github.com/indilib/indi.git
echo "✅ Indilib ready."
echo " "

# Install indiserver
echo "[4] Installing indiserver..."
mkdir -p ~/Projects/indi/tmp
cd ~/Projects/indi/tmp
cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Debug ~/Projects/indi
make -j4
sudo make install
echo "✅ Indiserver ready."
echo ""

# Installing 3rd Party Device Drivers
echo "[5] Installing 3rd party device drivers..."
cd ~/Projects
git clone --depth=1 https://github.com/indilib/indi-3rdparty

libraries=(
  libasi
  indi-asi
)

# Rutas base
src_base=~/Projects/indi-3rdparty
build_base=~/Projects

for lib in "${libraries[@]}"; do
  echo "Building and installing $lib..."

  # Create build directory
  mkdir -p "$build_base/$lib/tmp"
  cd "$build_base/$lib/tmp" || exit

  # Run cmake
  cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Debug "$src_base/$lib"

  # Compile and install
  make -j4
  sudo make install
done
echo "✅ 3rd party device drivers installed."
echo " "

# Install TelescopeController
echo " [6] Installing Telescope Controller"
cd ~
git clone https://github.com/jmalgarin86/TelescopeController.git
echo "✅ Telescope controller installed."
echo " "

# Create virtual environment here
echo "[7] Creating virtual environment"
cd ~/TelescopeController
python3 -m venv .venv
source .venv/bin/activate
echo "✅ Virtual environment ready."
echo " "

# Install PyQt5
echo "[8] Installing required python modules..."
# PyQt5
ln -s /usr/lib/python3/dist-packages/PyQt5 /home/$(logname)/TelescopeController/.venv/lib/python3.11/site-packages/PyQt5
ln -s /usr/lib/python3/dist-packages/sip* /home/$(logname)/TelescopeController/.venv/lib/python3.11/site-packages/

# pyindi-client
sudo apt install swig
# pip install pyindi-client git+https://github.com/indilib/pyindi-client.git
pip install 'git+https://github.com/indilib/pyindi-client.git@674706f#egg=pyindi-client'

# Requirements
pip install -r requirements.txt
echo "✅ Python modules installed."
echo ""

echo "[9] Installing astrometry.net..."
sudo apt install astrometry.net
echo "✅ Astrometry.net installed."
echo ""

echo "[10] Downloading astrometry index files..."
if [ ! -f "$ASTRO_TARXZ" ]; then
  wget --content-disposition "$ASTRO_INDEX_URL"
  echo "✅ $ASTRO_TARXZ downloaded."
else
  echo "✅ $ASTRO_TARXZ is already in the system."
fi
echo ""

echo "[11] Installing astrometry index files..."
sudo tar -xvf "$ASTRO_TARXZ" -C /usr/share
echo "✅ Index files installed."
echo ""

echo "[12] Auto startup configuration..."
# Create or overwrite Netplan configuration file
AUTOSTART_DIR="/home/$(logname)/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_DIR/inicio.desktop" <<EOF
[Desktop Entry]
Type=Application
Exec=/home/$(logname)/init.sh
Hidden=false
EOF
echo "✅ Automatic initialization configured."
echo ""

echo "[13] Crating init.sh file..."
# Create or overwrite Netplan configuration file
INIT_DIR="/home/$(logname)"
cat > "$INIT_DIR/init.sh" <<EOF
#!/bin/bash

cd ~/TelescopeController
source .venv/bin/activate
python main.py
EOF
chmod +x $INIT_DIR/init.sh
echo "✅ init.sh file created."
echo ""

echo "[14] Open the gui"
cd $INIT_DIR
./init.sh

echo "✅Ready!"