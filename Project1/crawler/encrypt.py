import base64
import json
import random
import string
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# 相关加密常量
MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
PUB_KEY = "010001"
PRESET_KEY = b"0CoJUm6Qyw8W8jud"
IV = b"0102030405060708"

def _aes_encrypt(text: bytes, key: bytes) -> bytes:
    """AES-128-CBC加密"""
    padded_text = pad(text, AES.block_size, style="pkcs7")
    cipher = AES.new(key, AES.MODE_CBC, IV)
    return base64.b64encode(cipher.encrypt(padded_text))

def _rsa_encrypt(text: bytes) -> str:
    """RSA加密"""
    text_int = int(text[::-1].hex(), 16)
    result_int = pow(text_int, int(PUB_KEY, 16), int(MODULUS, 16))
    return format(result_int, 'x').zfill(256)

def encrypt(payload: dict) -> dict:
    """加密payload为参数和密钥"""
    
    payload_bytes = json.dumps(payload).encode('utf-8')
    # 生成16字节的随机密钥
    random_key = "".join(random.choices(string.ascii_letters + string.digits, k=16)).encode('utf-8')
    # AES加密，得到'params'
    params = _aes_encrypt(_aes_encrypt(payload_bytes, PRESET_KEY), random_key)
    # RSA加密，得到'encSecKey'
    enc_sec_key = _rsa_encrypt(random_key)
    
    return {
        'params': params.decode('utf-8'),
        'encSecKey': enc_sec_key
    }