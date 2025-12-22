import hashlib
import json
import unicodedata

def hashCode(data):

    data_type = type(data)

    if data_type == str:
        digest = hashlib.sha256(data.encode("utf-8")).hexdigest()   #String
    elif data_type in (int,float):
        digest = hashlib.sha256(str(data).encode("utf-8")).hexdigest() # Numbers
    elif data is None:
        digest = None
    else:
        data_string = json.dumps(data, sort_keys=True)                  #  ensures consistent order
        data_string = unicodedata.normalize("NFC",data_string)    # ensure normal encoding of similar characters
        data_string = data_string.encode("utf-8")                       # Transform into raw byte array
        digest = hashlib.sha256(data_string).hexdigest()                # Get hash-code
    return digest

