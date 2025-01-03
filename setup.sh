#!/bin/bash

# dockerのインストール
if docker --version >/dev/null 2>&1; then
  echo "Docker has been installed. Skip install process..."
else
  echo "Docker is not found. Start to install docker!"

  if command -v apt > /dev/null 2>&1; then
    echo "apt"
    sudo apt-get update
    sudo apt-get upgrade -y
    sudo install -m 0755 -d /etc/apt/keyrings -y
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

  elif command -v dnf > /dev/null 2>&1; then
    echo "dnf"
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo -y
    sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

  else
    echo "This system has no install manager (apt or dnf)"
    exit 1
  fi

  echo "Docker has been installed!"
fi

# install python3.11 if not installed
if python3.11 --version >/dev/null 2>&1; then
  echo "Python3.11 has been installed. Skip Python3.11 Install process..."
else
  if command -v apt > /dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install software-properties-common -y
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt-get install python3.11 -y
  elif command -v dnf > /dev/null 2>&1; then
    sudo dnf install gcc openssl-devel bzip2-devel libffi-devel wget make -y
    wget "https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tar.xz"
    tar -xvf Python-3.11.11.tar.xz
    cd Python-3.11.11 && ./configure --enable-optimizations
    sudo make -j $(sudo nproc)
    sudo make altinstall
    cd ..
    sudo rm -rf Python-3.11.11
    rm -rf Python-3.11.11.tar.xz
  fi
fi

if [ ! -d ~/.local/quickrun ]; then
  mkdir -p ~/.local/quickrun
fi
cp -rf ./quickrun/* ~/.local/quickrun

if [ ! -f /usr/local/bin/qrun ]; then
  sudo ln -s ~/.local/quickrun/main.sh /usr/local/bin/qrun
  sudo chown $(whoami):$(whoami) /usr/local/bin/qrun
fi
