# ------------------------------------------------------
# RESTful API
# ------------------------------------------------------
from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from app import app, db, base_url
from app.models import *


api_bp = Blueprint('api', __name__, url_prefix=base_url + '/api')
api = Api(api_bp)

# Define a query parser to process JSON input
parser = reqparse.RequestParser()
parser.add_argument('server_name', type=str, help='Имя сервера')
parser.add_argument('ip_address', type=str, help='IP-адрес сервера')
parser.add_argument('os_id', type=int, help='ID операционной системы')
parser.add_argument('server_purpose_id', type=int, help='ID цели сервера')
parser.add_argument('dev_environment_id', type=int, help='ID среды разработки')
parser.add_argument('project_id', type=int, help='ID проекта')
parser.add_argument('apps', type=str, help='Приложения на сервере')
parser.add_argument('note', type=str, help='Примечание о сервере')
parser.add_argument('ports', type=str, help='Порты, используемые сервером')


# API Resources
class ServerResource(Resource):
    def get(self, server_id):
        server = Servers.query.get_or_404(server_id)
        return {
            'id': server.id,
            'server_name': server.server_name,
            'ip_address': server.ip_address,
            'os_id': server.os_id,
            'server_purpose_id': server.server_purpose_id,
            'dev_environment_id': server.dev_environment_id,
            'project_id': server.project_id,
            'apps': server.apps,
            'note': server.note,
            'ports': server.ports
        }

    def delete(self, server_id):
        server_to_delete = Servers.query.get_or_404(server_id)
        db.session.delete(server_to_delete)
        db.session.commit()
        return {'message': 'Server deleted successfully'}

    def put(self, server_id):
        args = parser.parse_args()
        server = Servers.query.get_or_404(server_id)

        # Обновление атрибутов сервера
        for key, value in args.items():
            if value is not None:
                setattr(server, key, value)

        db.session.commit()
        return {'message': 'Server updated successfully'}


class ServerListResource(Resource):
    def get(self):
        servers = Servers.query.all()
        result = []
        for server in servers:
            result.append({
                'id': server.id,
                'server_name': server.server_name,
                'ip_address': server.ip_address,
                'os_id': server.os_id,
                'server_purpose_id': server.server_purpose_id,
                'dev_environment_id': server.dev_environment_id,
                'project_id': server.project_id,
                'apps': server.apps,
                'note': server.note,
                'ports': server.ports
            })
        return {'servers': result}

    def post(self):
        args = parser.parse_args()
        new_server = Servers(
            server_name=args['server_name'],
            ip_address=args['ip_address'],
            os_id=args['os_id'],
            server_purpose_id=args['server_purpose_id'],
            dev_environment_id=args['dev_environment_id'],
            project_id=args['project_id'],
            apps=args['apps'],
            note=args['note'],
            ports=args['ports']
        )
        db.session.add(new_server)
        db.session.commit()
        return {'message': 'Server added successfully'}


# Registering resources in Blueprint
api.add_resource(ServerResource, '/server/<int:server_id>')
api.add_resource(ServerListResource, '/servers')

# Register Blueprint in the main application
app.register_blueprint(api_bp)
