* Deploy in terminal
```sh
git clone https://github.com/Rayanfer32/RRBOT.git
pip3 install -r requirements.txt
cd RRBOT
python3 bot.py
```

* Setup

create `.env` file in the RRBOT directory
add this line 
`RRBOT_TOKEN=YOUR_BOT_TOKEN` 


* Bot Commands
```bash
start - Check if the bot is Alive.
help - Useful commands.
tasks - Check Running tasks
```

* Autostart at boot
```
mkdir /home/pi/.config/autostart
nano /home/pi/.config/autostart/rrbot.desktop
```

```desktop
[Desktop Entry]
Type=Application
Name=RRbot
Exec=lxterminal -e python3 /home/pi/bot.py
```
* BASH aliases
```
alias temp='/opt/vc/bin/vcgencmd measure_temp'
alias pingg='fping -l -t100 www.google.com'
alias tempp='while true;do temp;sleep 3s;done'
alias speedtestt='speedtest-cli --server 7379'
alias cloudtest='npx speed-cloudflare-cli'
alias pingt='__pingt() { s=0; while :; do s=$(($s+1)); result=$(ping $1 -c1 -W1 |/bin/grep from) && echo "$result, seq=$s" && sleep 1 || echo timeout; done }; __pingt $1'
alias speedtestt='speedtest-cli --server 24161'
alias speedgo='/home/pi/./speedtest-go --server 7379'
alias fpingg='fping -l -t100 '
```

* Selenium Firefox setup
```
pip install selenium 
wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux32.tar.gz
tar xvf geckodriver*
cp geckodriver /usr/local/bin
```