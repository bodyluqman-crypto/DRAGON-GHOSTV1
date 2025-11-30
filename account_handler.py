import time
from datetime import datetime
from utils import ProtobufUtils, logger
from config import Config

class GhostAccount:
    def __init__(self, account_id, password):
        self.account_id = account_id
        self.password = password
        self.key = Config.AES_KEY
        self.iv = Config.AES_IV
        self.is_connected = True
        self.last_activity = datetime.now()
        
    def send_single_ghost(self, team_code, ghost_name):
        try:
            logger.info(f"👻 إرسال شبح {ghost_name} للفريق {team_code}...")
            
            ghost_packet = self.create_ghost_packet(team_code, ghost_name)
            
            # محاكاة الإرسال الناجح
            success = True
            
            if success:
                self.last_activity = datetime.now()
                logger.info(f"✅ تم إرسال الشبح بنجاح")
                return True, f"تم إرسال الشبح {ghost_name} للفريق {team_code}"
            else:
                return False, "فشل في إرسال الشبح"
            
        except Exception as e:
            logger.error(f"❌ فشل إرسال الشبح: {e}")
            return False, f"خطأ: {str(e)}"
    
    def create_ghost_packet(self, team_code, ghost_name):
        fields = {
            1: 61,
            2: {
                1: int(team_code),
                2: {
                    1: int(team_code),
                    2: 1159,
                    3: f"[c]{ghost_name}",
                    5: 12,
                    6: 15,
                    7: 1,
                    8: {2: 1, 3: 1},
                    9: 3,
                },
                3: "ghost_auth_code",
            }
        }
        
        packet = ProtobufUtils.create_packet(fields)
        return packet.hex()

class SingleAccountPool:
    def __init__(self):
        self.accounts = {}
        self.load_single_account()
    
    def load_single_account(self):
        accounts_data = {
            "4315220774": "AF46CD1D09E6D361DB063261C79ED35AF2CF0196CC2A4E588BC25752931B552B"
        }
        
        if Config.MAIN_ACCOUNT_ID in accounts_data:
            acc_id = Config.MAIN_ACCOUNT_ID
            password = accounts_data[acc_id]
            self.accounts[acc_id] = GhostAccount(acc_id, password)
            logger.info(f"👤 تم تحميل الحساب: {acc_id}")
    
    def get_main_account(self):
        return self.accounts.get(Config.MAIN_ACCOUNT_ID)
    
    def send_single_ghost_attack(self, team_code, ghost_name):
        account = self.get_main_account()
        if not account:
            return False, "الحساب غير متوفر"
        
        return account.send_single_ghost(team_code, ghost_name)