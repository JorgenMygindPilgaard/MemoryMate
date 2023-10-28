# Replace a substring with other substring starting from rear end
def rreplace(source_string,old_string,new_string,replace_count = 1):
    reverse_source_string = source_string[::-1]
    reverse_old_string = old_string[::-1]
    reverse_new_string = new_string[::-1]
    reverse_target_string = reverse_source_string.replace(reverse_old_string,reverse_new_string,replace_count)
    return reverse_target_string[::-1]

def insertDictionary(dic, key, value, index=-1):
    """
    Insert a key-value pair at a specified index in a dictionary.

    Args:
        dic (dict): The dictionary to insert into.
        key: The key to insert.
        value: The value associated with the key.
        index (int, optional): The position (index) at which to insert the key-value pair. Defaults to 0.

    Returns:
        dict: The modified dictionary.
    """
    if index < 0 or index >= len(dic):
        dic[key] = value  # If the index is greater than or equal to the length, append it.
    else:
        items = list(dic.items())
        items.insert(index, (key, value))
        dic.clear()
        dic.update(items)


























