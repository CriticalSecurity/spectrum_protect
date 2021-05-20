# IBM Spectrum Protect: Exploiting Legacy Authentication Protocol

### Intro
We want to share details of a little-known attack vector that we have successfully exploited in numerous security audits.

IBM Spectrum Protect is a backup solution that provides data protection for virtual, physical and cloud environments. The solution is based on a client-server architecture. IBM Spectrum Protect client nodes, administrative clients, and servers communicate using a proprietary communication protocol. Since version 8.1.2 released in 2017, the communication protocol got a major upgrade where TLS support was added, and a new authentication protocol was introduced. 

To maintain backward compatibility, the latest version of IBM Spectrum Protect (8.1.12 released in 2021) still supports the old authentication protocol. This protocol is vulnerable to offline, also known as stealth, password cracking. During a single authentication attempt the authentication protocol leaks enough information about a password needed to crack it offline. Upon a successful attack, an attacker would gain access to the backup data.

By default, a newly created administrative user is in a transitional state if not explicitly specified otherwise. This means that the old authentication protocol can be used to authenticate. The state is automatically upgraded and afterwards enforced if a user connects using a client, which supports a newer communication/authentication protocol. Therefore, only freshly created or forgotten administrative users can be exploited.  

### Session Security
Session security is the level of security that is used for communication between IBM Spectrum Protect clients and servers. It is set by using the SESSIONSECURITY parameter. This parameter can be set either to STRICT or TRANSITIONAL. The STRICT value enforces the highest level of security, while the TRANSITIONAL value enables authentication using the old protocol. By default, the value TRANSITIONAL is assigned to a newly created administrative user:

![dsmadmc](https://user-images.githubusercontent.com/79406206/118981653-daa00180-b97a-11eb-8905-c9891e5cb030.png)

### Authentication Protocol
The old authentication protocol can be reverse engineered from the JAR file dsmapi.jar that comes with the IBM Spectrum Protect Operations Center software. JADX and similar Java byte code decompilers can be used to obtain the source code. For example, a hardcoded AES key can be found in the decompiled source code. This key is used to encrypt the password of an admin user during the login procedure.

![dsmapi](https://user-images.githubusercontent.com/79406206/118981793-091ddc80-b97b-11eb-9022-91628f8670ed.png)
 
The authentication protocol is implemented as follows:
1. A client generates session and validation tokens.
2. A client encrypts the password provided by the user using the hardcoded AES key.
3. A client encrypts the session and validation tokens using the encrypted password as a key.
4. A client sends the encrypted session and validation tokens to the server.
5. The server selects the password of the connecting user from the database and encrypts it using the same hardcoded key.
6. The server decrypts the received encrypted session and validation tokens using the encrypted password as a key.
7. The server generates its own validation token.
8. The server encrypts the decrypted validation token and its own token using the decrypted session token as a key.
9. The server sends the encrypted response back to the client.
10. A client decrypts the received validation tokens using the session token.
11. A client sends the decrypted server’s validation token to the server.
12. The server compares its previously generated token to the received validation token and authenticates the user if the tokens match.
13. A client compares its previously generated token to the received validation token and authenticates the server if the tokens match.

### Stealth Password Cracking
The implementation of the old authentication protocol is flawed, because an attacker can repeat the authentication sequence offline. Basically, the attacker tries to decrypt the authentication message (a chosen-ciphertext) described in Step 3 until he gets a session token that was used to encrypt the response message described in Step 8.

To illustrate the attack three proof-of-concept tools were written. The [tsm_admin_enum.py](tsm_admin_enum.py) tool can be used to identify (using a dictionary attack) administrative accounts that are in a transitional state. The [tsm_auth_leak.py](tsm_auth_leak.py) tool retrieves authentication messages (for the specified user) needed for an offline password cracking attack. The [tsm_auth_crack.py](tsm_auth_crack.py) tool takes authentication messages and a password file as input and tries to find a valid password.

The following figure shows these three tools first identifying an admin account then retrieving authentication messages and finally cracking a password:

![terminal](https://user-images.githubusercontent.com/79406206/118981965-3b2f3e80-b97b-11eb-917b-c19917be8ef4.png)
