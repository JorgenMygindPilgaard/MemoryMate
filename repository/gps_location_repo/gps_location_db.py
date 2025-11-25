# ------------------------------
# DEMO USAGE STARTS HERE
# ------------------------------
from configuration.paths import Paths
from services.db_services.db_service import Database

def prepareDb():
    # Create the database
    db = Database(Paths.get("gps_location_db"))

    # Create table holding gps-services
    db.create_table(
        "service",
        "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT"
    )
    db.create_index(                    # To check if service exist
        "idx_service_name",
        "service",
        "name")

    # Create table holding service-users
    db.create_table(
        "user",
        "id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, service_id INTEGER"
    )
    db.create_index(
        "idx_user_name_service",        # To check if user/service-combination exist
        "user",
        "name,service_id"
    )

    # Create a table for gps-tracks (activities)
    db.create_table(
        "track",
        "id INTEGER PRIMARY KEY AUTOINCREMENT,external_id TEXT, user_id INTEGER, start_time_utc TEXT, end_time_utc TEXT, start_time_local TEXT, point_count INTEGER"
    )
    db.create_index(                    # To find activity holding a given photo-time
        "idx_track_user_start_end",
        "track",
        "user_id,start_time_utc,end_time_utc"
    )
    db.create_index(                    # To check if activity (track) has already been synchronized
        "idx_track_user_name",
        "track",
        "user_id,external_id"
    )
    db.create_index(                    # To find activity holding a given photo-time
        "idx_track_user_external_id",
        "track",
        "user_id,external_id"
    )

    # Create a table for gps points on the track
    db.create_table(
        "point",
        "id INTEGER PRIMARY KEY AUTOINCREMENT, track_id INTEGER, time_utc TEXT, latitude REAL, longitude REAL"
    )
    db.create_index(                    # To find neighbour times to a given photo-time (and interpolate gps-location)
        "idx_point_track_time",
        "point",
        "track_id,time_utc"
    )
    return db




# # 3. Insert rows (with different keys)
# rows_to_insert = [
#     {"name": "Alice", "age": 30},
#     {"name": "Bob", "city": "Berlin"},
#     {"name": "Charlie", "age": 25, "city": "Paris"}
# ]
# count = db.insert_rows("people", rows_to_insert)
# print(f"Inserted {count} rows\n")
#
# # 4. Search all rows
# print("All rows in table:")
# pprint(db.search(from_="people"))
#
# # 5. Search with WHERE and params
# print("\nPeople aged >= 26:")
# pprint(db.search(
#     from_="people",
#     where="age >= ?",
#     params=(26,),
#     order_by="age DESC"
# ))
#
# # 6. Update rows
# print("\nUpdating Bob's age to 40...")
# affected = db.update_rows(
#     "people",
#     updates={"age": 40},
#     where="name = ?",
#     params=("Bob",)
# )
# print(f"Rows updated: {affected}\n")
#
# # Show result
# pprint(db.search(from_="people"))
#
# # 7. Delete rows
# print("\nDeleting people from Paris...")
# deleted = db.delete_rows(
#     "people",
#     where="city = ?",
#     params=("Paris",)
# )
# print(f"Rows deleted: {deleted}\n")
#
# # Show final result
# print("Final table contents:")
# pprint(db.search(from_="people"))