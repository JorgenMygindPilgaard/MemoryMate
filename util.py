# Replace a substring with other substring starting from rear end
def rreplace(source_string,old_string,new_string,replace_count = 1):
    reverse_source_string = source_string[::-1]
    reverse_old_string = old_string[::-1]
    reverse_new_string = new_string[::-1]
    reverse_target_string = reverse_source_string.replace(reverse_old_string,reverse_new_string,replace_count)
    return reverse_target_string[::-1]


























