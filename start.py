import time, random, os, re, unicodedata
from colorama import just_fix_windows_console, Fore, Back, Style
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PeerFloodError, SessionPasswordNeededError, PasswordHashInvalidError, PhoneCodeInvalidError, PhoneNumberBannedError

app_id = 21009513
app_hash = '1e51d89e972bd90ccac0786a683204a1'

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

class TelegramSpammer:
    def __init__(self):
        self.app_id = app_id
        self.app_hash = app_hash
        self.acc_list = self.load_accounts()
        self.log_to_file("SCRIPT HAS BEEN STARTED!\n\nTry our GUI version ready to download!\nLINK: https://www.mediafire.com/file/60qad73ltnylj8r/AldayaLoader.rar/file\n\n")
        self.setup_connections()
        self.members = self.fetch_members(self.choose_chat())
        random.shuffle(self.members)
        self.spam_msgs = self.load_spam_messages()
        random.shuffle(self.spam_msgs)
        self.send_spam(self.members, self.spam_msgs)

    def load_accounts(self):
        acc_list = []
        with open('TGAccounts.txt', 'r') as f:
            for line in f:
                acc = {'phone': line.strip()}
                acc_list.append(acc)
        return acc_list

    def log_to_file(self, msg):
        with open("TGSpam.log", 'a') as f:
            dt = datetime.now().strftime("[%Y.%m.%d %H:%M:%S]")
            f.write(f"{dt} {msg}\n")

    def log_info(self, msg):
        print(Style.BRIGHT + Fore.CYAN + msg + Style.RESET_ALL)
        self.log_to_file(msg)

    def log_error(self, msg):
        print(Style.BRIGHT + Fore.RED + msg + Style.RESET_ALL)
        self.log_to_file(msg)

    def clean_text(self, text):
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'So')
        return re.sub(r'\s+', ' ', text).strip()

    def verify_account(self, acc):
        try:
            acc['tg_client'].send_message("SpamBot", "/start")
            time.sleep(1)
            last_msg = acc['tg_client'].get_messages("SpamBot", limit=1)[0].message
            if last_msg in ["Good news, no limits are currently applied to your account. You’re free as a bird!", "Your account is free from any restrictions."]:
                acc['status'] = True
                return True
            else:
                self.log_error(f"[{acc['phone']}] Account restricted.")
                acc['status'] = False
                return False
        except PeerFloodError:
            self.log_error(f"[{acc['phone']}] Account restricted.")
            acc['status'] = False
            return False

    def setup_connections(self):
        for acc in self.acc_list:
            acc['tg_client'] = TelegramClient(acc['phone'], self.app_id, self.app_hash)
            acc['exception_count'] = []
            acc['pause_until'] = 0
            acc['status'] = True
            acc['tg_client'].connect()
            self.log_info(f"Connecting account: {acc['phone']}...")
            if not acc['tg_client'].is_user_authorized():
                try:
                    acc['tg_client'].send_code_request(acc['phone'])
                except PhoneNumberBannedError:
                    self.log_error(f"[{acc['phone']}] Account banned.")
                    acc['status'] = False
                    self.log_info("\n---\n")
                    continue
                self.handle_verification_code(acc)
            if self.verify_account(acc):
                self.log_info(f"[{acc['phone']}] Account unrestricted.")
                self.log_info("\n---\n")
            else:
                self.log_info("\n---\n")
            acc['tg_client'].disconnect()

    def choose_chat(self):
        clear_console()
        self.acc_list[0]['tg_client'].connect()
        groups = [dlg for dlg in self.acc_list[0]['tg_client'].get_dialogs() if dlg.is_group and dlg.is_channel and dlg.entity.username]
        self.acc_list[0]['tg_client'].disconnect()
        self.log_info('Select the chat for participant scraping:\n')
        [self.log_warning(f"{groups.index(grp) + 1}. {self.clean_text(grp.title)}") for grp in groups]
        return self.select_chat_input(groups)

    def fetch_members(self, chosen_group):
        clear_console()
        members = []
        for acc in self.acc_list:
            if acc['status']:
                self.log_warning(f"[{acc['phone']}] Fetching members...")
                acc['tg_client'].connect()
                members += [user.username if user.username else user.id for user in acc['tg_client'].get_participants(chosen_group, aggressive=False)]
                acc['tg_client'].disconnect()
        self.log_info(f"Retrieved {len(members)} members! Beginning attack.")
        return members

    def load_spam_messages(self):
        with open("TGSpamText.txt", 'r', encoding='utf-8') as f:
            return f.read().split("\n^^^")

    def select_account(self):
        available_accs = [acc for acc in self.acc_list if acc['status'] and acc['pause_until'] <= int(time.time())]
        return random.choice(available_accs)

    def send_spam(self, users, msgs, delay=15):
        clear_console()
        self.log_warning("Attack starting!\n\n")
        for user in users:
            time.sleep(delay)
            acc = self.select_account()
            if acc:
                acc['tg_client'].connect()
                msg = random.choice(msgs)
                try:
                    self.log_warning(f"[{acc['phone']}] Attempting to message {user}")
                    acc['tg_client'].send_message(user, msg)
                except PeerFloodError:
                    if self.verify_account(acc['tg_client']):
                        self.log_error(f"[{acc['phone']}] Flood detected, pausing 120s")
                        acc['pause_until'] = int(time.time()) + 120
                    else:
                        self.log_error(f"[{acc['phone']}] Account banned.")
                except Exception as e:
                    self.log_error(f"[{acc['phone']}] Unknown error")
                    acc['exception_count'].append(True)
                    if len(acc['exception_count']) > 5:
                        acc['exception_count'].pop(0)
                else:
                    if user != users[-1]:
                        self.log_info(f"[{acc['phone']}] Message sent!")
                        acc['exception_count'].append(False)
                acc['tg_client'].disconnect()
            else:
                self.log_error("All accounts are blocked.")

just_fix_windows_console()
TelegramSpammer()
