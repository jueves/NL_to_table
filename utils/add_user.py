# Adds user field to old MongoDB documents.
from db_utils import MongoManagerPerUser

# Setup Mongo Connection
db = MongoManagerPerUser()

db._db.users.find({"user_id": {"$exists": True}})