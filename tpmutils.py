#!/usr/bin/env python

from __future__ import print_function

from binascii import hexlify, unhexlify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib
import json
import os
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse
    input = raw_input

from trezorlib.client import TrezorClient
from trezorlib.transport_udp import UdpTransport

# Return path by BIP-32
def getPath(client):
    return client.expand_path("10016'/0")

# Deriving master key
def getMasterKey(client):
    bip32_path = getPath(client)
    ENC_KEY = 'Activate TREZOR Password Manager?'
    ENC_VALUE = unhexlify('2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee2d650551248d792eabf628f451200d7f51cb63e46aadcbb1038aacb05e8c8aee')
    key = hexlify(client.encrypt_keyvalue(
        bip32_path,
        ENC_KEY,
        ENC_VALUE,
        True,
        True
    ))
    return key

# Deriving file name and encryption key
def getFileEncKey(key):
    filekey, enckey = key[:len(key) // 2], key[len(key) //2:]
    FILENAME_MESS = b'5f91add3fa1c3c76e90c90a3bd0999e2bd7833d06a483fe884ee60397aca277a'
    digest = hmac.new(filekey, FILENAME_MESS, hashlib.sha256).hexdigest()
    filename = digest + '.pswd'
    return [filename, filekey, enckey]

# def encryptStorageRaw(f, jsonData, key):
#     cipherkey = unhexlify(key)
    
#     iv = os.urandom(12)
#     #tag = os.urandom(16)
#     f.write(iv)
#     cipher = Cipher(algorithms.AES(cipherkey), modes.GCM(iv), backend=default_backend())
#     encryptor = cipher.encryptor()
#     block = ''
#     offest = 0
#     res = ''
#     while True:
#         block = jsonData[offest:offest+16]
#         if len(block) == 0:
#             break
#         offest = offest + 16
#         block = encryptor.update(block)
#         res = res + block
#     # throws exception when the tag is wrong
#     res = res + encryptor.finalize()

#     f.write(encryptor.tag)
#     f.write(res)

def encryptStorageRaw(f, jsonData, key):
    cipherkey = unhexlify(key)
    res = encryptRaw(jsonData, cipherkey)
    f.write(res)

def encryptRaw(data, cipherkey):
    output = ''
    iv = os.urandom(12)
    output += iv
    cipher = Cipher(algorithms.AES(cipherkey), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    block = ''
    offest = 0
    res = ''
    while True:
        block = data[offest:offest+16]
        if len(block) == 0:
            break
        offest = offest + 16
        block = block.encode('utf-8')
        block = encryptor.update(block)
        res = res + block
    # throws exception when the tag is wrong
    res = res + encryptor.finalize()

    output += encryptor.tag
    output += res
    return output

def encryptStorage(path, passDict, key):
    jsonData = json.dumps(passDict, separators=(',', ':'))
    with open(path, 'wb') as f:
        encryptStorageRaw(f, jsonData, key)

def decryptStorage(path, key):
    data = ''
    with open(path, 'rb') as f:
        data = decryptStorageRaw(f, key)
    return json.loads(data)

def decryptStorageRaw(f, key):
    cipherkey = unhexlify(key)

    iv = f.read(12)
    tag = f.read(16)
    cipher = Cipher(algorithms.AES(cipherkey), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    data = ''
    while True:
        block = f.read(16)
        # data are not authenticated yet
        if block:
            data = data + block
        else:
            break
    # throws exception when the tag is wrong

    data = decryptor.update(data) + decryptor.finalize()
    return data


def encryptEntryValue(nonce, val):
    cipherkey = unhexlify(nonce)
    output = encryptRaw(val, cipherkey)
    return output

def decryptEntryValue(nonce, val):
    cipherkey = unhexlify(nonce)
    iv = val[:12]
    tag = val[12:28]
    cipher = Cipher(algorithms.AES(cipherkey), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    data = ''
    inputData = val[28:]
    while True:
        block = inputData[:16]
        inputData = inputData[16:]
        if block:
            data = data + block
        else:
            break
        # throws exception when the tag is wrong
    data = decryptor.update(data).decode('utf-8') + decryptor.finalize().decode('utf-8')
    return json.loads(data)

# Decrypt give entry nonce
def getDecryptedNonce(client, entry):
    if 'item' in entry:
        item = entry['item']
    else:
        item = entry['title']

    pr = urlparse(item)
    if pr.scheme and pr.netloc:
        item = pr.netloc

    ENC_KEY = 'Unlock %s for user %s?' % (item, entry['username'])
    ENC_VALUE = entry['nonce']
    decrypted_nonce =  hexlify(client.decrypt_keyvalue(
        getPath(client),
        ENC_KEY,
        unhexlify(ENC_VALUE),
        False,
        True
    ))
    return decrypted_nonce

# Pretty print of list
def printEntries(entries, client):
    for k, v in entries.items():
        print('Entry id: #%s' % k)
        print('-------------')
        entry_id = k

        plain_nonce = getDecryptedNonce(client, entries[entry_id])

        pwdArr = entries[entry_id]['password']['data']
        pwdHex = ''.join([ hex(x)[2:].zfill(2) for x in pwdArr ])
        print('password: ', decryptEntryValue(plain_nonce, unhexlify(pwdHex)))

        safeNoteArr = entries[entry_id]['safe_note']['data']
        safeNoteHex = ''.join([ hex(x)[2:].zfill(2) for x in safeNoteArr ])
        print('safe_note:', decryptEntryValue(plain_nonce, unhexlify(safeNoteHex)))
        
        for kk, vv in v.items():
            if kk in ['nonce', 'safe_note', 'password']: continue # skip these fields
            print('*', kk, ': ', vv)
        print()
    return
