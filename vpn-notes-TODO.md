
# WG SERVER
# ------------

sudo apt update
sudo apt install wireguard

cd /etc/wireguard
wg genkey | sudo tee privatekey | wg pubkey | sudo tee publickey

# Get the default interface name (excluding lo)
INTERFACE=$(ip route | grep default | awk '{print $5}')


# Create wg0.conf with proper configuration
sudo tee /etc/wireguard/wg0.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.1/24
ListenPort = 51820

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o $INTERFACE -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o $INTERFACE -j MASQUERADE


[Peer]
PublicKey = AddTheClientPublicKeyStringHere=
AllowedIPs = 10.0.0.2/32
EOF


sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 600 /etc/wireguard/wg0.conf
sudo chmod 644 /etc/wireguard/publickey


sudo echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sudo sysctl -p


sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0




# WG CLIENT
# ------------

sudo apt install wireguard


cd /etc/wireguard
wg genkey | sudo tee privatekey | wg pubkey | sudo tee publickey

sudo chmod 600 /etc/wireguard/privatekey
sudo chmod 644 /etc/wireguard/publickey


# Create client config
cat << EOF > wg0.conf
[Interface]
PrivateKey = $(cat /etc/wireguard/privatekey)
Address = 10.0.0.2/24
ListenPort = 42150
PostUp = iptables -A INPUT -i wg0 -j ACCEPT; iptables -A OUTPUT -o wg0 -j ACCEPT
PostDown = iptables -D INPUT -i wg0 -j ACCEPT; iptables -D OUTPUT -o wg0 -j ACCEPT


[Peer]
PublicKey = AddTheServerPublicKeyStringHere=
AllowedIPs = 10.0.0.0/24  
Endpoint = vpn-onprem2.i.psilva.org:51820
PersistentKeepalive = 25
EOF



# Start/Up the interface
sudo wg-quick up wg0
# Stop/Down the interface
sudo wg-quick down wg0
# Check status
sudo wg show


# connect on reboot - but there a better way don there
# Create systemd service
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
# To verify status
sudo systemctl status wg-quick@wg0


#LOGS 
# View logs for the WireGuard service
sudo journalctl -u wg-reconnect@wg0

# Follow logs in real-time
sudo journalctl -u wg-reconnect@wg0 -f

# See just the latest logs
sudo journalctl -u wg-reconnect@wg0 -n 50

# View logs since last boot
sudo journalctl -u wg-reconnect@wg0 -b




#reconnect on restart and boot
sudo nano /etc/systemd/system/wg-reconnect@.service

[Unit]
Description=Watchdog for WireGuard VPN Interface %I
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/usr/bin/wg-quick up %i
ExecStop=/usr/bin/wg-quick down %i
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target

# activate service
sudo systemctl daemon-reload
sudo systemctl enable wg-reconnect@wg0
sudo systemctl start wg-reconnect@wg0

