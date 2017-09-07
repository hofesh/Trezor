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

# Pretty print of list
def decodeEntries(entries, client):
    for k, v in entries.items():
        entry_id = k

        plain_nonce = getDecryptedNonce(client, entries[entry_id])

        pwdArr = entries[entry_id]['password']['data']
        pwdHex = ''.join([ hex(x)[2:].zfill(2) for x in pwdArr ])
        entries[entry_id]['password'] = decryptEntryValue(plain_nonce, unhexlify(pwdHex))

        safeNoteArr = entries[entry_id]['safe_note']['data']
        safeNoteHex = ''.join([ hex(x)[2:].zfill(2) for x in safeNoteArr ])
        entries[entry_id]['safe_note'] = decryptEntryValue(plain_nonce, unhexlify(safeNoteHex))
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

    jsonraw = decryptStorageRaw(sys.stdin, encKey)
    
    #sys.stdout.write(jsonraw)
    #return

    parsed_json = json.loads(jsonraw)
    entries = parsed_json['entries']
    decodeEntries(entries, client)
    sys.stdout.write(json.dumps(parsed_json, separators=(',', ':')))
    
    return

if __name__ == '__main__':
    main()
