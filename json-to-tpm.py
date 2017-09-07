#!/usr/bin/env python

from __future__ import print_function

from binascii import hexlify, unhexlify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hmac
import hashlib
import json
import os
import sys
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse
    input = raw_input

from trezorlib.client import TrezorClient
from trezorlib.transport_udp import UdpTransport

from tpmutils import *

def encodeEntries(entries, client):
    for k, v in entries.items():
        entry_id = k

        plain_nonce = getDecryptedNonce(client, entries[entry_id])

        password = json.dumps(entries[entry_id]['password'])
        passwordEnc = encryptEntryValue(plain_nonce, password)
        bytesArr = [ord(x) for x in passwordEnc]
        entries[entry_id]['password'] = { 'type': 'Buffer', 'data': bytesArr }

        safeNote = json.dumps(entries[entry_id]['safe_note'])
        safeNoteEnc = encryptEntryValue(plain_nonce, safeNote)
        bytesArr = [ord(x) for x in safeNoteEnc]
        entries[entry_id]['safe_note'] = { 'type': 'Buffer', 'data': bytesArr }
    return


def main():
    client = TrezorClient(UdpTransport())

    masterKey = getMasterKey(client)
    # print('master key:', masterKey)

    fileName = getFileEncKey(masterKey)[0]
    # print('file name:', fileName)

    path = os.path.expanduser('~/Dropbox/Apps/TREZOR Password Manager/')
    # print('path to file:', path)

    encKey = getFileEncKey(masterKey)[2]
    # print('enckey:', encKey)

    jsonraw = sys.stdin.read()
    pswd = json.loads(jsonraw)
    encodeEntries(pswd["entries"], client)
    jsonraw = json.dumps(pswd, separators=(',', ':'))
    encryptStorageRaw(sys.stdout, jsonraw, encKey)
    
    return

if __name__ == '__main__':
    main()
