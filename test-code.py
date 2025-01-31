import snscrape.modules.twitter as sntwitter
import re
import requests
from solana.rpc.api import Client
import time

# CONFIG (DÜZENLE!)
TELEGRAM_TOKEN = "7598084487:AAGauhXl1KOAgHCu2fG3xveK1vGA7XkM5NU"  # @BotFather'dan al
CHAT_ID = "CHAT_ID"           # https://api.telegram.org/bot<TOKEN>/getUpdates
TARGET_USERS = ["kudret024"]   # Kullanıcı adları (@ işareti olmadan)
SOLANA_RPC = "https://api.mainnet-beta.solana.com"

# Initialize
solana_client = Client(SOLANA_RPC)
last_checked_tweets = {}  # Son kontrol edilen tweet ID'leri saklar

def send_alert(address):
    message = f"🚨 **Yeni Kontrat Bulundu!** \n`{address}`"
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
    )

def check_new_tweets():
    for username in TARGET_USERS:
        query = f"from:{username}"
        latest_tweet = next(sntwitter.TwitterSearchScraper(query).get_items())
        
        if not latest_tweet:
            continue
            
        tweet_id = latest_tweet.id
        if last_checked_tweets.get(username) != tweet_id:
            last_checked_tweets[username] = tweet_id
            addresses = re.findall(r'[1-9A-HJ-NP-Za-km-z]{32,44}', latest_tweet.rawContent)
            
            for addr in addresses:
                try:
                    if solana_client.get_account_info(addr)['result']:
                        send_alert(addr)
                except:
                    pass

# Sonsuz döngü (5 dakikada bir kontrol)
while True:
    check_new_tweets()
    time.sleep(300)  # 5 dakika bekle
