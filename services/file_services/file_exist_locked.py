import os

def fileLocked(filepath):
    if fileExist(filepath):
        try:
            # Try opening the file in read/write mode with exclusive access
            with open(filepath, 'r+b') as f:
                # Try to lock the first byte using msvcrt
                import msvcrt
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                # If successful, unlock immediately
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
            return False  # Not locked
        except (OSError, PermissionError):
            return True  # Locked
    else:
        return False

def fileExist(filepath):
    if isinstance(filepath,str):
        if filepath != '':
            if os.path.isfile(filepath):
                return True
            else:
                return False
        else:
            return False
    else:
        return False


