from extensions import db
from datetime import datetime


class ContainerORM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    container_id = db.Column(db.String(255))
    enable = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    port = db.Column(db.Integer, unique=True)
    status = db.Column(db.Boolean, default=None)
    results = db.Column(db.String(255))
    client = None
    channel = None

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
