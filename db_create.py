#! .env/bin/python

from config import SQLALCHEMY_DATABASE_URI
from app import db

def create_all():
    db.create_all()
    # TODO: run alembic migration here.

if __name__ == '__main__':
    create_all()
