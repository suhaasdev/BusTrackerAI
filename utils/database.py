"""MongoDB connection with transparent in-memory fallback.

If MONGO_URI is unreachable (common for college demos without a local
MongoDB server), the app falls back to an in-memory store that mimics
the subset of PyMongo Collection API used by this project. This keeps
`python app.py` working out of the box while remaining 100% compatible
with real MongoDB when it IS available.
"""
import uuid
import copy
from datetime import datetime

_mongo_client = None
_mongo_db = None
_use_memory = False
_memory_store = {}

class MemoryResult:
    def __init__(self, inserted_id=None, matched=0, modified=0, deleted=0):
        self.inserted_id = inserted_id
        self.matched_count = matched
        self.modified_count = modified
        self.deleted_count = deleted


def _match(doc, filt):
    if not filt:
        return True
    for k, v in filt.items():
        if isinstance(v, dict):
            # support $in, $gte, $lte, $ne
            if "$in" in v:
                if doc.get(k) not in v["$in"]:
                    return False
            elif "$ne" in v:
                if doc.get(k) == v["$ne"]:
                    return False
            elif "$gte" in v:
                if doc.get(k) is None or doc.get(k) < v["$gte"]:
                    return False
            elif "$lte" in v:
                if doc.get(k) is None or doc.get(k) > v["$lte"]:
                    return False
            else:
                if doc.get(k) != v:
                    return False
        else:
            if doc.get(k) != v:
                return False
    return True


class MemoryCollection:
    def __init__(self, name):
        self.name = name
        if name not in _memory_store:
            _memory_store[name] = []

    @property
    def _docs(self):
        return _memory_store[self.name]

    def insert_one(self, doc):
        d = copy.deepcopy(doc)
        d.setdefault("_id", uuid.uuid4().hex[:24])
        self._docs.append(d)
        return MemoryResult(inserted_id=d["_id"])

    def find_one(self, filt=None, *a, **kw):
        for d in self._docs:
            if _match(d, filt or {}):
                return copy.deepcopy(d)
        return None

    def find(self, filt=None, *a, **kw):
        out = [copy.deepcopy(d) for d in self._docs if _match(d, filt or {})]
        # support sort kwarg: sort=[("created_at", -1)]
        sort = kw.get("sort")
        if sort:
            for key, direction in reversed(sort):
                out.sort(key=lambda x: x.get(key, ""), reverse=(direction < 0))
        limit = kw.get("limit", 0)
        if limit:
            out = out[:limit]
        return out

    def update_one(self, filt, update, upsert=False):
        for d in self._docs:
            if _match(d, filt or {}):
                if "$set" in update:
                    d.update(copy.deepcopy(update["$set"]))
                if "$inc" in update:
                    for k, v in update["$inc"].items():
                        d[k] = d.get(k, 0) + v
                if "$push" in update:
                    for k, v in update["$push"].items():
                        d.setdefault(k, []).append(v)
                return MemoryResult(matched=1, modified=1)
        if upsert:
            d = dict(filt or {})
            if "$set" in update:
                d.update(copy.deepcopy(update["$set"]))
            d.setdefault("_id", uuid.uuid4().hex[:24])
            self._docs.append(d)
            return MemoryResult(inserted_id=d["_id"], matched=0, modified=0)
        return MemoryResult(matched=0, modified=0)

    def delete_one(self, filt):
        for i, d in enumerate(self._docs):
            if _match(d, filt or {}):
                del self._docs[i]
                return MemoryResult(deleted=1)
        return MemoryResult(deleted=0)

    def count_documents(self, filt=None):
        return sum(1 for d in self._docs if _match(d, filt or {}))

    def create_index(self, *a, **kw):
        return None


class MemoryDB:
    def __getitem__(self, name):
        return MemoryCollection(name)

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return MemoryCollection(name)


def get_db():
    """Return (db, using_memory_bool). Connects lazily."""
    global _mongo_client, _mongo_db, _use_memory
    if _mongo_db is not None:
        return _mongo_db, _use_memory
    try:
        from config import Config
        from pymongo import MongoClient
        client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=1500)
        client.server_info()  # raises if unreachable
        _mongo_client = client
        _mongo_db = client[Config.DB_NAME]
        _use_memory = False
        # indexes (best-effort)
        try:
            _mongo_db.users.create_index("email", unique=True)
            _mongo_db.buses.create_index("bus_number", unique=True)
            _mongo_db.bookings.create_index("booking_id", unique=True)
        except Exception:
            pass
        return _mongo_db, False
    except Exception:
        _mongo_db = MemoryDB()
        _use_memory = True
        return _mongo_db, True


def serialize(doc):
    """Make a Mongo doc JSON-safe."""
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    for k, v in list(d.items()):
        if isinstance(v, datetime):
            d[k] = v.isoformat()
    return d
