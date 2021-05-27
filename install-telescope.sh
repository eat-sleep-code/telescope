# This script will install the telescope software, dng support, and any required prerequisites.
cd ~
echo -e ''
echo -e '\033[32mTelescope [Installation Script] \033[0m'
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e ''
echo -e '\033[93mUpdating package repositories... \033[0m'
sudo apt update

echo ''
echo -e '\033[93mInstalling prerequisites... \033[0m'
sudo apt install -y git python3 python3-pip python3-picamera
sudo pip3 install keyboard --force

echo ''
echo -e '\033[93mInstalling DNG support... \033[0m'
sudo git clone https://github.com/schoolpost/PyDNG.git
sudo chown -R $USER:$USER PyDNG
cd PyDNG
sudo pip3 install src/.
cd ~
sudo rm -Rf PyDNG

echo ''
echo -e '\033[93mInstalling Telescope... \033[0m'
cd ~
sudo rm -Rf ~/telescope
sudo git clone https://github.com/eat-sleep-code/telescope
sudo chown -R $USER:$USER telescope
cd telescope
sudo chmod +x telescope.py

echo ''
echo -e '\033[93mDownloading color profiles... \033[0m'
cd ~
sudo rm -Rf ~/telescope/profiles
mkdir ~/telescope/profiles
sudo chown -R $USER:$USER ~/telescope/profiles
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/PyDNG_profile.dcp -O ~/telescope/profiles/basic.dcp
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/Raspberry%20Pi%20High%20Quality%20Camera%20Lumariver%202860k-5960k%20Neutral%20Look.dcp -O ~/telescope/profiles/neutral.dcp
wget -q https://github.com/davidplowman/Colour_Profiles/raw/master/imx477/Raspberry%20Pi%20High%20Quality%20Camera%20Lumariver%202860k-5960k%20Skin%2BSky%20Look.dcp -O ~/telescope/profiles/skin-and-sky.dcp

cd ~
echo ''
echo -e '\033[93mSetting up alias... \033[0m'
sudo sed -i '/\b\(function telescope\)\b/d' ~/.bash_aliases
sudo sed -i '$ a function telescope { sudo python3 ~/telescope/telescope.py "$@"; }' ~/.bash_aliases
echo -e 'You may use \e[1mtelescope <options>\e[0m to launch the program.'

echo ''
echo -e '\033[32m-------------------------------------------------------------------------- \033[0m'
echo -e '\033[32mInstallation completed. \033[0m'
echo ''
bash
