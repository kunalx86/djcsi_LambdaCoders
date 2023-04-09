from app import db
import datetime

class Activity(db.Document):
    parent = db.ObjectIdField(db_field="parent", required=True)
    child = db.ObjectIdField(db_field="childrens", required=True)
    visits = db.ListField(db.ObjectIdField(db_field="visits"))

