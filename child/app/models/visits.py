from app import db
import datetime

class Visits(db.Document):
    childrens=db.ObjectIdField(db_field="childrens")
    timestamp=db.DateTimeField(default=datetime.datetime.utcnow)
    url=db.StringField(required=True)
    isblocked=db.BooleanField(required=True, default=False)
    suggestBlocked=db.BooleanField(required=False, default=False)

