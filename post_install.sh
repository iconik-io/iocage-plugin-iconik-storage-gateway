#!/bin/sh

# Enable iconik storage gateway
sysrc -f /etc/rc.conf iconik_storage_gateway_enable="YES"

# Enable iconik ui
echo "iconik_ui_enable=\"YES\"" >> /etc/rc.conf

#restart services
/usr/local/etc/rc.d/iconik_ui restart
/usr/local/etc/rc.d/iconik_storage_gateway restart
