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

    json = sys.stdin.read()
    encryptStorageRaw(sys.stdout, json, encKey)
    
    return

if __name__ == '__main__':
    main()
