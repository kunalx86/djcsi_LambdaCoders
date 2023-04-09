from app import db
import uuid

class Childrens(db.Document):
    _id = db.StringField(default=str(uuid.uuid4()),)
    firstName=db.StringField(required=True)
    lastName=db.StringField(required=True)
    blockedWebsites=db.ListField(db.StringField())
    hours=  db.IntField(required=True)
    minutes= db.IntField(required=True)
    parent=db.ObjectIdField(db_field="parents")
    token= db.StringField(required=True)
    gender= db.StringField(required=False)
    updatedAt= db.StringField(required=False)
    createdAt= db.StringField(required=False)
    __v= db.StringField(required=False)
    age= db.IntField(required=True)
    meta = {
    'strict': False,
}


