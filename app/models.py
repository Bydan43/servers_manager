from app import db


class DevEnvironments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class ServerPurpose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(255), nullable=False)


class OperatingSystem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Servers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dev_environment_id = db.Column(db.Integer, db.ForeignKey('dev_environments.id'))
    server_name = db.Column(db.String(255),unique=True, nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)
    os_id = db.Column(db.Integer, db.ForeignKey('operating_system.id'))
    server_purpose_id = db.Column(db.Integer, db.ForeignKey('server_purpose.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    apps = db.Column(db.Text)
    note = db.Column(db.Text)
    ports = db.Column(db.Text)
