import json
import sqlite3
from pathlib import Path
from typing import Any

from typing import Any

from satelite_temperature_prediction.tile_api.application.repositories import INeighborhoodRepository


class SqliteNeighborhoodRepository(INeighborhoodRepository):
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)

    def get_neighborhoods_geojson(self) -> dict[str, Any]:
        if not self.db_path.exists():
            raise FileNotFoundError(f"SQLite database not found: {self.db_path}")

        query = (
            "SELECT n.feature_id, n.fid, n.gid, n.synoikia, n.dk, n.shape_leng, n.geit_thesm, "
            "n.synoik_en, n.dk_en, n.shape_area, n.id_prop, n.geitonia, n.name_place, "
            "n.name_pl_en, n.geiton_en, n.geometry_type, n.geometry_json, "
            "AVG(t.temperature_2m_mean) AS average_temperature "
            "FROM neighborhood_athens AS n "
            "LEFT JOIN neighborhood_temperatures AS t "
            "ON t.neighborhood_fid = n.fid "
            "GROUP BY n.row_id"
        )

        features = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute(query):
                geometry = json.loads(row["geometry_json"]) if row["geometry_json"] else None
                properties = {
                    "average_temperature": row["average_temperature"],
                    "fid": row["fid"],
                    "gid": row["gid"],
                    "synoikia": row["synoikia"],
                    "dk": row["dk"],
                    "shape_leng": row["shape_leng"],
                    "geit_thesm": row["geit_thesm"],
                    "synoik_en": row["synoik_en"],
                    "dk_en": row["dk_en"],
                    "shape_area": row["shape_area"],
                    "id": row["id_prop"],
                    "geitonia": row["geitonia"],
                    "name_place": row["name_place"],
                    "name_pl_en": row["name_pl_en"],
                    "geiton_en": row["geiton_en"],
                }
                features.append({
                    "type": "Feature",
                    "id": row["feature_id"],
                    "geometry": geometry,
                    "properties": properties,
                })

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    def get_neighborhood_list(self) -> list[dict[str, Any]]:
        query = (
            "SELECT fid, "
            "COALESCE(geiton_en, name_place, geitonia, 'Unknown') AS name "
            "FROM neighborhood_athens "
            "ORDER BY name"
        )

        neighborhoods = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute(query):
                neighborhoods.append({
                    "fid": row["fid"],
                    "name": row["name"],
                })

        return neighborhoods

    def get_neighborhoods_geojson_by_fids(self, fids: list[int]) -> dict[str, Any]:
        if not fids:
            return {"type": "FeatureCollection", "features": []}

        placeholders = ",".join("?" for _ in fids)
        query = (
            "SELECT n.feature_id, n.fid, n.gid, n.synoikia, n.dk, n.shape_leng, n.geit_thesm, "
            "n.synoik_en, n.dk_en, n.shape_area, n.id_prop, n.geitonia, n.name_place, "
            "n.name_pl_en, n.geiton_en, n.geometry_type, n.geometry_json, "
            "AVG(t.temperature_2m_mean) AS average_temperature "
            "FROM neighborhood_athens AS n "
            "LEFT JOIN neighborhood_temperatures AS t "
            "ON t.neighborhood_fid = n.fid "
            f"WHERE n.fid IN ({placeholders}) "
            "GROUP BY n.row_id"
        )

        features = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute(query, fids):
                geometry = json.loads(row["geometry_json"]) if row["geometry_json"] else None
                properties = {
                    "average_temperature": row["average_temperature"],
                    "fid": row["fid"],
                    "gid": row["gid"],
                    "synoikia": row["synoikia"],
                    "dk": row["dk"],
                    "shape_leng": row["shape_leng"],
                    "geit_thesm": row["geit_thesm"],
                    "synoik_en": row["synoik_en"],
                    "dk_en": row["dk_en"],
                    "shape_area": row["shape_area"],
                    "id": row["id_prop"],
                    "geitonia": row["geitonia"],
                    "name_place": row["name_place"],
                    "name_pl_en": row["name_pl_en"],
                    "geiton_en": row["geiton_en"],
                }
                features.append({
                    "type": "Feature",
                    "id": row["feature_id"],
                    "geometry": geometry,
                    "properties": properties,
                })

        return {"type": "FeatureCollection", "features": features}

    def get_neighborhood_temperatures_by_fids(self, fids: list[int]) -> dict[str, Any]:
        if not fids:
            return {}

        placeholders = ",".join("?" for _ in fids)
        query = (
            "SELECT neighborhood_fid, date, temperature_2m_mean "
            "FROM neighborhood_temperatures "
            f"WHERE neighborhood_fid IN ({placeholders}) "
            "ORDER BY date ASC"
        )

        timeseries = {str(fid): [] for fid in fids}
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            for row in conn.execute(query, fids):
                fid_str = str(row["neighborhood_fid"])
                if fid_str not in timeseries:
                    timeseries[fid_str] = []
                timeseries[fid_str].append({
                    "date": row["date"],
                    "temperature": row["temperature_2m_mean"]
                })

        return timeseries
