#!/bin/sh

sysrc -f /etc/rc.conf iconik_storage_gateway_enable="YES"

echo "Download Distfiles"
cd /root
fetch https://storage.googleapis.com/harald-iconik-test/iconik_storage_gateway-1.6.0.txz

pkg add /root/iconik_storage_gateway-1.6.0.txz

# Enable iconik ui
echo "iconik_ui_enable=\"YES\"" >> /etc/rc.conf

#restart services
/usr/local/etc/rc.d/iconik_storage_gateway restart

