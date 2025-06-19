import psutil
import json
import sqlite3
import os
from configuration.language import Texts
from PyQt6.QtWidgets import QMessageBox
from datetime import  datetime

def isLightroomRunning():
    """Check if Adobe Lightroom Classic is running."""
    for process in psutil.process_iter(attrs=['name']):
        if "Lightroom.exe" in process.info['name'] or "Lightroom" in process.info['name']:
            return True
    return False

def isCatalogLocked(lrcat_path):
    """Check if the Lightroom catalog is locked (indicating Lightroom is open)."""
    lockfile = lrcat_path + "-wal"  # Write-ahead log (WAL) exists if the DB is in use
    return os.path.exists(lockfile)

def processLightroomQueue(lrcat_path, json_path,silent=False):
    """Updates idx_filename and lc_idx_filename in AgLibraryFile based on a JSON mapping.
       Ensures full path (root + folder + filename) matches before renaming.
    """
    if not os.path.exists(json_path):
        return

    while True:
        if isLightroomRunning() or isCatalogLocked(lrcat_path):
            if silent:
                break
            msg_box = QMessageBox()
            msg_box.setWindowTitle(Texts.get('lr_filename_update_error_title'))
            msg_box.setText(Texts.get('lr_filename_update_error_msg'))
            msg_box.setIcon(QMessageBox.Icon.Warning)
            retry_button = msg_box.addButton(Texts.get("lr_filename_update_retry"), QMessageBox.ButtonRole.AcceptRole)
            cancel_button = msg_box.addButton(Texts.get("lr_filename_update_later"), QMessageBox.ButtonRole.RejectRole)

            msg_box.exec()  # This makes the code wait for user input

            if msg_box.clickedButton() == retry_button:
                continue
            elif msg_box.clickedButton() == cancel_button:
                break

        # Load JSON file with old and new filenames
        with open(json_path, "r", encoding="utf-8") as file:
            try:
                queue_entries = json.load(file)
                if not isinstance(queue_entries, list):  # Ensure it's a list
                    queue_entries = []
            except json.JSONDecodeError:
                queue_entries = []  # Reset if JSON is corrupted

        # Connect to Lightroom Classic catalog database
        if queue_entries != []:
            conn = sqlite3.connect(lrcat_path)
            cursor = conn.cursor()

            processed_paths = set()
            for entry in queue_entries:
                old_path = entry.get("old_name")  # Full old file path
                new_path = entry.get("new_name")  # Full new file path

                # Check if old_path exists in previously processed new_paths
                # if old_path in processed_paths:
                #     conn.commit()
                #     conn.close()
                #     conn = sqlite3.connect(lrcat_path)
                #     cursor = conn.cursor()
                #     processed_paths.clear()

                # Extract components
                old_dir, old_filename = os.path.split(old_path)
                new_filename = os.path.basename(new_path)
                new_basename, _ = os.path.splitext(new_filename)  # Filename without extension

                # Step 1: Find the root folder ID and folder ID matching the old path
                cursor.execute("""
                    SELECT rf.id_local, f.id_local
                    FROM AgLibraryRootFolder rf
                    JOIN AgLibraryFolder f ON f.rootFolder = rf.id_local
                    WHERE rf.absolutePath || f.pathFromRoot = ?
                """, (old_dir.replace("\\", "/") + "/",))

                folder_row = cursor.fetchone()
                if not folder_row:
        #           print(f"Skipped (folder not found): {old_path}")
                    continue

                root_folder_id, folder_id = folder_row

                # Step 2: Find the file in AgLibraryFile with correct root/folder and old filename
                cursor.execute("""
                    SELECT id_local FROM AgLibraryFile
                    WHERE folder = ? AND idx_filename = ?
                """, (folder_id, old_filename))

                file_row = cursor.fetchone()
                if file_row:
                    file_id = file_row[0]

                    # Step 3: Rename deleted files as deleted_<filename> in lr catalouge to avoid collisions
                    cursor.execute("""
                        SELECT id_local FROM AgLibraryFile
                        WHERE folder = ? AND idx_filename = ?
                    """, (folder_id, new_filename))
                    file_row_deleted = cursor.fetchone()
                    if file_row_deleted:
                        file_id_deleted = file_row_deleted[0]

                    # Set filename as deleted_filename in lr-catalouge, if file has been deleted on disk
                        now = datetime.now()
                        date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

                        cursor.execute("""
                            UPDATE AgLibraryFile
                            SET idx_filename = ?, lc_idx_filename = ?, baseName = ?
                            WHERE id_local = ?
                        """, ('deleted '+date_time_str+' '+new_filename, 'deleted '+date_time_str+' '+new_filename.lower(), 'deleted '+date_time_str+' '+new_basename, file_id_deleted))

                    # Step 3: Update the filename in AgLibraryFile
                    cursor.execute("""
                        UPDATE AgLibraryFile
                        SET idx_filename = ?, lc_idx_filename = ?, baseName = ?
                        WHERE id_local = ?
                    """, (new_filename, new_filename.lower(), new_basename, file_id))

                # processed_paths.add(new_path)

            # Commit changes and close connection
            conn.commit()
            conn.close()

    # Empty rename-queue
        with open(json_path, "w", encoding="utf-8") as file:
            file.write("[]")  # Empty list
        break
def appendLightroomQueue(json_path,append_entries=[]):
    """Appends a new rename entry to the JSON file."""

    # Check if file exists; create an empty list if not
    if not os.path.exists(json_path):
        queue_entries = []
    else:
        with open(json_path, "r", encoding="utf-8") as file:
            try:
                queue_entries = json.load(file)
                if not isinstance(queue_entries, list):  # Ensure it's a list
                    queue_entries = []
            except json.JSONDecodeError:
                queue_entries = []  # Reset if JSON is corrupted

    # Append new entry
    for entry in append_entries:
        queue_entries.append(entry)

    # Write back to JSON file
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(queue_entries, file, indent=4)






