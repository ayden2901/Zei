#!/bin/bash

# Menetapkan batas file descriptor sementara
ulimit -n 100000

echo "Menetapkan ulimit -n menjadi 100000"

# Menambahkan batasan ke /etc/security/limits.conf
LIMITS_CONF="/etc/security/limits.conf"
echo "root soft nofile 100000" | sudo tee -a $LIMITS_CONF
echo "root hard nofile 100000" | sudo tee -a $LIMITS_CONF
echo "Batasan telah ditambahkan ke $LIMITS_CONF"

# Menambahkan batasan ke /etc/systemd/system.conf dan /etc/systemd/user.conf
SYSTEMD_CONF="/etc/systemd/system.conf"
USER_CONF="/etc/systemd/user.conf"

echo "DefaultLimitNOFILE=100000" | sudo tee -a $SYSTEMD_CONF
echo "DefaultLimitNPROC=100000" | sudo tee -a $SYSTEMD_CONF

echo "DefaultLimitNOFILE=100000" | sudo tee -a $USER_CONF
echo "DefaultLimitNPROC=100000" | sudo tee -a $USER_CONF

echo "Batasan telah ditambahkan ke konfigurasi systemd."

echo "Restarting systemd to apply changes..."
sudo systemctl daemon-reexec

echo "Konfigurasi selesai. Silakan reboot agar perubahan diterapkan sepenuhnya."