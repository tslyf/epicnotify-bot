from datetime import datetime

import peewee

from .config import settings

db = peewee.SqliteDatabase(settings.db_path)


class Chat(peewee.Model):
    peer_id = peewee.IntegerField(unique=True)
    created_at = peewee.DateTimeField(default=datetime.now)

    class Meta:
        database = db


class Notified(peewee.Model):
    game_id = peewee.CharField()
    start_date = peewee.DateTimeField()

    class Meta:
        database = db
        primary_key = peewee.CompositeKey("game_id", "start_date")


class CachedImage(peewee.Model):
    image_url = peewee.CharField(unique=True)
    attachment = peewee.CharField()

    class Meta:
        database = db


def init_db():
    db.connect()
    db.create_tables([Chat, Notified, CachedImage])
    db.close()
