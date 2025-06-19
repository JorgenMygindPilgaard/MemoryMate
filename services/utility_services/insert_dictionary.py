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