import os
from dotenv import load_dotenv
load_dotenv("secrets.env")

TOKEN = os.environ.get("BOT_TOKEN", os.getenv("BOT_TOKEN"))

ENABLED_USERS = os.environ.get("ENABLED_USERS", '1024316776,628650705')
ENABLED_USERS = set(int(e.strip()) for e in ENABLED_USERS.split(','))

PING_SERVERS = ["www.google.com",
"www.whatsapp.com",
"www.primevideo.com",
"www.pulsesecure.net",
"www.webex.com",
"www.bing.com",
"www.facebook.com",
'8.8.8.8',
'8.8.4.4',
"1.1.1.1",
"meet.google.com",
'www.instagram.com',
"103.89.235.174",
'www.youtube.com',
'www.speedtest.net',
'www.fast.com',
'www.microsoft.com',
"www.cloudflare.com",
'www.gmail.com',
'www.fast.com',
"www.yahoo.com",
"www.amazon.com",
"www.cisco.com",
"www.robosoftin.com",
"www.spotify.com",
"www.flipkart.com",
"103.89.235.174",
"www.hotstar.com",
"www.sophos.com",
"www.botim.me",
"www.zomato.com",
"www.swiggy.com",
"www.zoho.com",
"www.anydesk.com",
"www.cablenote.com",
"www.citrix.com",
]

# Alert if greater than threshold
LATENCY_ALERT = 100
PACKETLOSS_ALERT = 7
# sleep for pinger 
PINGER_SLEEP_AT = 23 #rd hour 23:00
PINGER_RESUME_AT = 7 # resume packetLossNotifier at 07:00

CMD_WHITE_LIST = {}
CMD_BLACK_LIST = {'rm'}
CMD_BLACK_CHARS = {';', '\n'}
ONLY_SHORTCUT_CMD = False

MAX_TASK_OUTPUT = int(os.environ.get("MAX_TASK_OUTPUT", 5000))

PROXY_URL = os.environ.get("ALL_PROXY", '')

SC_MENU_ITEM_ROWS = (
    (
        ('temp','/opt/vc/bin/vcgencmd measure_temp'),
        ('pingg','oa;fping -l -t100 www.google.com'),   
        ('fast-bin','oa;fast-bin'),
        # ('deenet','oa;speedtest-cli --server 16512'),
    ),
    (
        # ('speedgo','oa;/home/pi/./speedtest-go --server 7379'),
        # ('speedtestt','oa;speedtest-cli --server 7379'),
        ('fast-arm','oa;fast-arm'),
        ('cloudtest','oa;npx speed-cloudflare-cli'),
        ('jio-speed','oa;speedtest -s 10195'),
        ('dubai','oa;speedtest -s 22129'),
        ('airtel-speed','oa;speedtest -s 18976'),
        ('singapore','oa;speedtest -s 13623'),
        
        # ('Demo Script', 'demo.py', True),
    ),
    (
      ('speed-deenet','oa;speedtest -s 16512'),
      ('speed-act','oa;speedtest -s 7379'),
      ('fast -u','oa;fast --upload'),
    ),
)

SC_MENU_ITEM_CMDS = {}
for row in SC_MENU_ITEM_ROWS:
    for cmd in row:
        SC_MENU_ITEM_CMDS[cmd[1]] = cmd

REQUEST_KWARGS = {
    'proxy_url': PROXY_URL
}

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SCRIPTS_ROOT_PATH = os.path.join(ROOT_PATH, 'scripts')