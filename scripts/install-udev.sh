#!/bin/bash
echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="5131", ATTRS{idProduct}=="2007", MODE="0666"' \
    | sudo tee /etc/udev/rules.d/99-gamerx-cooler.rules
sudo udevadm control --reload-rules
sudo udevadm trigger
echo "✅ udev rule installed !"
