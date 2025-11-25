from typing import Any
from datetime import datetime
from repository.gps_location_repo.gps_location_db import prepareDb

class GpsApi:
    instance = None
    def __init__(self):
        self.gps_location_db = prepareDb()

    @staticmethod
    def getInstance():
        if GpsApi.instance is None:
            GpsApi.instance = GpsApi()
        return GpsApi.instance

    # ---------- SERVICE ----------
    def create_service(self, name: str) -> int:
        return self.gps_location_db.insert_rows("service", [{"name": name}])

    def update_service(self, id: int, name: str) -> int:
        return self.gps_location_db.update_rows("service", {"name": name}, "id = ?", (id,))

    def delete_service(self, id: int) -> int:
        # Get all users for this service
        users = self.gps_location_db.search(select="id", from_="user", where="service_id = ?", params=(id,))
        for user in users:
            self.delete_user(user["id"])
        return self.gps_location_db.delete_rows("service", "id = ?", (id,))

    def get_services(self,id: int | None = None, name: str | None = None) -> list[dict[str, Any]]:
        where_clauses = []
        params = []

        if id is not None:
            where_clauses.append("id = ?")
            params.append(id)

        if name is not None:
            where_clauses.append("name = ?")
            params.append(name)

        where_sql = " AND ".join(where_clauses) if where_clauses else ""

        return self.gps_location_db.search(
            from_="service",
            where=where_sql,
            params=params
        )

    # ---------- USER ----------
    def create_user(self, name: str, service_id: int) -> int:
        return self.gps_location_db.insert_rows("user", [{"name": name, "service_id": service_id}])

    def update_user(self, id: int, name: str) -> int:
        return self.gps_location_db.update_rows("user", {"name": name}, "id = ?", (id,))

    def delete_user(self, id: int) -> int:
        # Get all tracks for this user
        tracks = self.gps_location_db.search(select="id", from_="track", where="user_id = ?", params=(id,))
        for t in tracks:
            self.delete_track(t["id"])
        return self.gps_location_db.delete_rows("user", "id = ?", (id,))

    def get_users(self, id: int | None = None,service_id: int | None = None,name: str | None = None) -> list[dict[str, Any]]:
        where_clauses = []
        params = []

        if id is not None:
            where_clauses.append("id = ?")
            params.append(id)
        if service_id is not None:
            where_clauses.append("service_id = ?")
            params.append(service_id)

        if name is not None:
            where_clauses.append("name = ?")
            params.append(name)

        where_sql = " AND ".join(where_clauses) if where_clauses else ""

        return self.gps_location_db.search(
            from_="user",
            where=where_sql,
            params=params
        )

    # ---------- TRACK ----------
    def create_track(self, external_id: str, user_id: int, start_time_utc: str | None = None, end_time_utc: str | None = None, start_time_local: str | None = None, point_count: int | None = None) -> int:
        return self.gps_location_db.insert_rows("track", [{
            "external_id": external_id,
            "user_id": user_id,
            "start_time_utc": start_time_utc,
            "end_time_utc": end_time_utc,
            "start_time_local": start_time_local,
            "point_count": point_count
        }])

    def update_track(self, track_id: int, **updates) -> int:
        return self.gps_location_db.update_rows("track", updates, "id = ?", (track_id,))


    def delete_track(self, track_id: int) -> int:
        # Delete all points for this track
        self.gps_location_db.delete_rows("point", "track_id = ?", (track_id,))
        return self.gps_location_db.delete_rows("track", "id = ?", (track_id,))

    def get_tracks(self, id: int | None = None, external_id: str | None = None, user_id: int | None = None, contains_time_utc: str | None = None) -> list[dict[str, Any]]:
        where_clauses = []
        params = []

        if id is not None:
            where_clauses.append("id = ?")
            params.append(id)

        if external_id is not None:
            where_clauses.append("external_id = ?")
            params.append(external_id)

        if user_id is not None:
            where_clauses.append("user_id = ?")
            params.append(user_id)

        if contains_time_utc is not None:
            where_clauses.append("start_time_utc <= ?")
            params.append(contains_time_utc)
            where_clauses.append("end_time_utc >= ?")
            params.append(contains_time_utc)


        where_sql = " AND ".join(where_clauses) if where_clauses else ""

        return self.gps_location_db.search(
            from_="track",
            where=where_sql,
            params=params
        )

    # ---------- POINT ----------
    def create_points(self, points) -> int:
        """
        Create points.

        Example:
            points = [
                {"track_id": 1, "time": "2025-09-14T12:00:00Z", "longitude": 12.34, "latitude": 56.78},
                {"track_id": 2, "time": "2025-09-14T12:01:00Z", "longitude": 98.76, "latitude": 54.32},
            ]
        """
        return self.gps_location_db.insert_rows("point", points)

    def get_points(self,
                   track_id: int | None = None,
                   earliest_time_utc: str | None = None,
                   latest_time_utc: str | None = None,
                   limit: int | None = None) -> list[dict[str, Any]]:
        where_clauses = []
        params = []

        if track_id is not None:
            where_clauses.append("track_id = ?")
            params.append(track_id)

        order_by=""
        if earliest_time_utc is not None:
            where_clauses.append("time_utc >= ?")
            params.append(earliest_time_utc)
            order_by="time_utc ASC"

        if latest_time_utc is not None:
            where_clauses.append("time_utc <= ?")
            params.append(latest_time_utc)
            order_by = "time_utc DESC"


        where_sql = " AND ".join(where_clauses) if where_clauses else ""

        return self.gps_location_db.search(
            from_="point",
            where=where_sql,
            params=params,
            limit=limit,
            order_by=order_by
        )

    # Get user-id for a username (fo a specific gps-service like garmin connect)
    def get_user_id(self,service_name:str,user_name:str):
        services = self.get_services(name=service_name)
        if services == []:
            return None
        service_id = services[0]["id"]

        users = self.get_users(name=user_name,service_id=service_id)
        if users == []:
            return None
        return users[0]["id"]


#   Get the estimated location for a user of a gps-service at a given time
    def get_location(self,user_id: int,time_utc:str) -> [float,float]:          # A user-id can be assigned to one service only. It can share user_name with other user-ids though.
        if time_utc is None:
            return None
        tracks = self.get_tracks(user_id=user_id,contains_time_utc=time_utc)
        if tracks == []:
            return None
        track_id = tracks[0]["id"]

        # Get point right after time
        points = self.get_points(track_id=track_id,earliest_time_utc=time_utc,limit=1)  # Gets the first point with time on or after time_utc
        if points == []:
            return None
        point_after = points[0]
        if point_after["time_utc"] == time_utc:   # Exact time match. No interpolation needed
            return point_after["latitude"],point_after["longitude"]

        # Get point right before time
        points = self.get_points(track_id=track_id,latest_time_utc=time_utc,limit=1)  # Gets the first point with time on or before time
        if points == []:
            return None
        point_before = points[0]
        if point_before["time_utc"] == time_utc:   # Not exact time match. Interpolation needed
            return point_before["latitude"],point_before["longitude"]

        # Interpolation
        time_after = datetime.fromisoformat(point_after["time_utc"])
        time_before = datetime.fromisoformat(point_before["time_utc"])
        time_photo = datetime.fromisoformat(time_utc)
        time_fraction = (time_photo - time_before)  / (time_after - time_before)
        latitude  = ( point_after["latitude"] - point_before["latitude"] ) * time_fraction + point_before["latitude"]
        longitude = ( point_after["longitude"] - point_before["longitude"] ) * time_fraction + point_before["longitude"]
        return latitude,longitude
