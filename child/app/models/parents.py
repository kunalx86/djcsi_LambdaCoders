from app import db
import uuid

class Parents(db.Document):
    _id = db.StringField(default=str(uuid.uuid4()),)
    firstName=db.StringField(required=True)
    lastName= db.StringField(required=True)
    email= db.StringField(required=True)
    password= db.StringField(required=True)
    childrens= db.ListField(db.ObjectIdField(db_field="childrens"))
    updatedAt= db.StringField(required=False)
    createdAt= db.StringField(required=False)
    
    meta = {
    'strict': False,
}


