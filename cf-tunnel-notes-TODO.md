
# Cloudflared SERVER
# ------------

sudo apt update
sudo apt upgrade -y

curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && 

sudo dpkg -i cloudflared.deb && 

sudo cloudflared service install eyJhIjoiOZNjYjQ1YTBiNmFkZ