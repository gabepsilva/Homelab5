
# WG SERVER
# ------------

sudo su

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


#[Peer]
#PublicKey = AddTheClientPublicKeyStringHere=
#AllowedIPs = 10.0.0.2/32

#[Peer]
#PublicKey = AddTheClientPublicKeyStringHere=
#AllowedIPs = 10.0.0.3/32
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

apt update
sudo su
apt install wireguard


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
PublicKey = nGd33qcJfvxjsTDexoSXGzeuo9lFiyrg0b7WE1zQXDM=
AllowedIPs = 10.0.0.0/24  
Endpoint = vpn-server.psilva.org:51820
PersistentKeepalive = 25
EOF


# Stop/Down the interface
sudo wg-quick down wg0
# Start/Up the interface
sudo wg-quick up wg0
# Check status
sudo wg show


# connect on reboot - but there a better way don there
# Create systemd service
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
# To verify status
sudo systemctl status wg-quick@wg0


#LOGS 
sudo journalctl -u wg-quick@wg0.service


# Follow logs in real-time
sudo journalctl -u wg-quick@wg0.service -f

# See just the latest logs
sudo journalctl -u wg-quick@wg0.service -n 50

# View logs since last boot
sudo journalctl -u wg-quick@wg0.service -b





# EXAMPLE config

## WG SERVER ON PREM
```config
cat /etc/wireguard/wg0.conf 
[Interface]
PrivateKey = CD0wK3E5gY4s24KLU7gZtcxxFIOsOXcbQjfWasDJ+kA=
Address = 10.0.0.1/24
ListenPort = 51820

PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE; iptables -A INPUT -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE; iptables -D INPUT -i wg0 -j ACCEPT



[Peer]
PublicKey = ...=
AllowedIPs = 10.0.0.2/32

[Peer]
PublicKey = ...=
AllowedIPs = 10.0.0.3/32, 172.31.0.0/16
root@vpn-server:/home/ubuntu# 
```


## WG CLIENT ON PREM


```config
cat /etc/wireguard/wg0.conf 
[Interface]
PrivateKey = ...=
Address = 10.0.0.2/24
ListenPort = 42150
PostUp = iptables -A INPUT -i wg0 -j ACCEPT; iptables -A OUTPUT -o wg0 -j ACCEPT
PostDown = iptables -D INPUT -i wg0 -j ACCEPT; iptables -D OUTPUT -o wg0 -j ACCEPT


[Peer]
PublicKey = ...=
AllowedIPs = 10.0.0.0/24 #, 172.31.0.0/16 # allow this server to communicate with the aws vpc whiout routing through the vpn server
Endpoint = vpn-server.i.psilva.org:51820
PersistentKeepalive = 25
```



## WG CLIENT EC2

```config
cat /etc/wireguard/wg0.conf 
[Interface]
PrivateKey = ...=
Address = 10.0.0.3/24
ListenPort = 42150
PostUp = iptables -A INPUT -i wg0 -j ACCEPT; iptables -A OUTPUT -o wg0 -j ACCEPT
PostDown = iptables -D INPUT -i wg0 -j ACCEPT; iptables -D OUTPUT -o wg0 -j ACCEPT


[Peer]
PublicKey = ...=
AllowedIPs = 10.0.0.0/24, 10.10.0.0/24, 172.31.0.0/16 
Endpoint = 24.226.117.119:51820
PersistentKeepalive = 25



# may need this to enable comm from other servers to on prem
#echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
#sysctl -p

```
