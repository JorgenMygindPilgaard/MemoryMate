import hashlib
import json

def hashCode(data):

    data_type = type(data)

    if data_type == str:
        digest = hashlib.sha256(data.encode("utf-8")).hexdigest()   #String
    elif data in (int,float):
        digest = hashlib.sha256(str(data).encode("utf-8")).hexdigest() # Numbers
    elif data is None:
        digest = None
    else:
        data_string = json.dumps(data, sort_keys=True)  # ensures consistent order
        digest = hashlib.sha256(data_string.encode("utf-8")).hexdigest()   # Complex types

    return digest

