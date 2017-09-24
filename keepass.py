import csv
import json
import os,binascii
import sys
import fileinput

entries = {}
id = 0
reader = csv.reader(sys.stdin)
next(reader, None)
for row in reader:
    entry = {}
    entry["username"] = row[1] # USERNAME
    entry["nonce"] = binascii.b2a_hex(os.urandom(32))
    entry["tags"] = []
    entry["title"] = row[3] # URL
    entry["safe_note"] = row[4] # COMMENT
    entry["note"] = row[0] # TITLE
    entry["password"] = row[2] # PASSWORD
    entries[id] = entry
    id += 1
        
res = {"entries": entries}
res["version"] = "0.0.1"
res["extVersion"] = "0.5.14"
res["config"] = {"orderType": "date"}
res["tags"] = {}
res["tags"]["0"] = {"icon": "home", "title": "All"}

print(json.dumps(res, separators=(',', ':')))
