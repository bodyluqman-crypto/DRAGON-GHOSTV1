import json
import time
import logging
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import jwt
import base64
import requests
import urllib3
from config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DRAGON-API")

class CryptoUtils:
    @staticmethod
    def encrypt_hex(hex_data):
        cipher = AES.new(Config.AES_KEY, AES.MODE_CBC, Config.AES_IV)
        return cipher.encrypt(pad(bytes.fromhex(hex_data), AES.block_size)).hex()
    
    @staticmethod
    def decrypt_hex(hex_data):
        cipher = AES.new(Config.AES_KEY, AES.MODE_CBC, Config.AES_IV)
        return unpad(cipher.decrypt(bytes.fromhex(hex_data)), AES.block_size).hex()
    
    @staticmethod
    def encrypt_packet(hex_data, key, iv):
        return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(bytes.fromhex(hex_data), 16)).hex()

class ProtobufUtils:
    @staticmethod
    def encode_varint(num):
        if num < 0: raise ValueError("Number must be non-negative")
        out = []
        while True:
            b = num & 0x7F
            num >>= 7
            if num: b |= 0x80
            out.append(b)
            if not num: break
        return bytes(out)
    
    @staticmethod
    def create_field(num, val):
        if isinstance(val, int):
            return ProtobufUtils.encode_varint((num << 3) | 0) + ProtobufUtils.encode_varint(val)
        if isinstance(val, (str, bytes)):
            v = val.encode() if isinstance(val, str) else val
            return ProtobufUtils.encode_varint((num << 3) | 2) + ProtobufUtils.encode_varint(len(v)) + v
        if isinstance(val, dict):
            nested = ProtobufUtils.create_packet(val)
            return ProtobufUtils.encode_varint((num << 3) | 2) + ProtobufUtils.encode_varint(len(nested)) + nested
        return b""
    
    @staticmethod
    def create_packet(fields):
        return b"".join(ProtobufUtils.create_field(k, v) for k, v in fields.items())

class AccountManager:
    @staticmethod
    def load_accounts():
        try:
            return {
                "4315220774": "AF46CD1D09E6D361DB063261C79ED35AF2CF0196CC2A4E588BC25752931B552B"
            }
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            return {
                "4315220774": "AF46CD1D09E6D361DB063261C79ED35AF2CF0196CC2A4E588BC25752931B552B"
            }

class APIValidator:
    @staticmethod
    def check_api_status():
        elapsed = datetime.now() - Config.START_TIME
        if elapsed > Config.API_DURATION:
            logger.error("API has expired after 30 days")
            return False
        return True
    
    @staticmethod
    def validate_team_code(team_code):
        if not team_code or not team_code.isdigit():
            return False
        return len(team_code) >= 6