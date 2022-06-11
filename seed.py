from app import db
from models import Pokemon

db.drop_all()
db.create_all()

Pokemon.get_national_dex()
db.session.commit()
