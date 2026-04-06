    #!/bin/bash

    # Update and install packages
    sudo apt-get update -y && sudo apt-get upgrade -y
    sudo apt-get install -y --no-install-recommends \
        ffmpeg git neofetch apt-utils libmediainfo0v5 \
        libgl1-mesa-glx libglib2.0-0 fonts-noto-color-emoji tmux python3-venv python3-pip sqlite3 net-tools lsof

    sudo apt-get clean
    sudo rm -rf /var/lib/apt/lists/*

    # Setup swap
    echo "Setting up swap..."
    sudo fallocate -l 8G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

    # Configure swappiness and cache pressure
    echo "Configuring memory management parameters..."
    echo 'vm.swappiness=90' | sudo tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=200' | sudo tee -a /etc/sysctl.conf
    sudo sysctl vm.swappiness=90
    sudo sysctl vm.vfs_cache_pressure=200
    sudo sysctl -p

    # Show swap and memory status
    echo "Swap status:"
    sudo swapon --show
    echo "Memory usage:"
    free -h
    echo "Current memory parameters:"
    echo "Swappiness: $(cat /proc/sys/vm/swappiness)"
    echo "VFS Cache Pressure: $(cat /proc/sys/vm/vfs_cache_pressure)"

    # ulimit -n
    echo "* soft nofile 4096" >> /etc/security/limits.conf
    echo "* hard nofile 8192" >> /etc/security/limits.conf

    echo "Setup completed successfully!"