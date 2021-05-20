from Crypto.Cipher import AES
from binascii import unhexlify
import sys

key = b"\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01"
iv  = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
mode = AES.MODE_CBC
size = AES.block_size

pad = lambda s: s + (size - len(s) % size) * chr(size - len(s) % size).encode()

def decrypt(ciphertext, key, iv):
    decryptor = AES.new(key, mode, iv)
    return decryptor.decrypt(ciphertext)
    
def encrypt(plaintext, key, iv):
    sample = pad(plaintext)
    encryptor = AES.new(key, mode, iv)
    return encryptor.encrypt(sample)

if __name__=='__main__':
    if len(sys.argv) != 4:
        print("Usage: %s msg1 msg2 passlist" % sys.argv[0])
        sys.exit(1)
    
    msg1 = unhexlify(sys.argv[1])
    msg2 = unhexlify(sys.argv[2])
    
    f = open(sys.argv[3])
    passwords = f.readlines()
    
    for password in passwords:
        password = password.rstrip().upper().encode()
        print("[~] Trying '%s'" % password.decode())
        requestKey = encrypt(password, key, iv)[-16:]
        tempvar = decrypt(msg1, requestKey, iv)
        SessionKey = tempvar[0:16]
        ValToken = tempvar[16:32]
        if msg2 == encrypt(ValToken, SessionKey, iv)[0:16]:
            print("\n[+] Found: '%s'" % password.decode())
            sys.exit()
