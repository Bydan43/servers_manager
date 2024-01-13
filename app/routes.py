from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from sqlalchemy.exc import IntegrityError
from flask import Blueprint
from flask_restful import Api, Resource, reqparse
from app import app
from app.models import *
import os


base_url = os.environ.get('BASE_URL', '')
app.config['APPLICATION_ROOT'] = base_url


@app.route(base_url + '/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.root_path + '/static', filename)


# ------------------------------------------------------
# Server list
# ------------------------------------------------------
@app.route(base_url + '/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 8

    if request.method == 'POST':
        if 'project_name' in request.form:
            new_project = Projects(name=request.form['project_name'])
            db.session.add(new_project)
            db.session.commit()
        elif 'operating_system_name' in request.form:
            new_operating_system = DevEnvironments(name=request.form['operating_system_name'])
            db.session.add(new_operating_system)
            db.session.commit()
        elif 'server_purpose_name' in request.form:
            new_server_purpose = ServerPurpose(name=request.form['server_purpose_name'])
            db.session.add(new_server_purpose)
            db.session.commit()
        else:
            try:
                new_server = Servers(
                    server_name=request.form['server_name'],
                    ip_address=request.form['ip_address'],
                    os_id=request.form['os_id'],
                    server_purpose_id=request.form['server_purpose_id'],
                    dev_environment_id=request.form['dev_environment_id'],
                    project_id=request.form['project_id'],
                    apps=request.form.get('apps', None),
                    note=request.form.get('note', None),
                    ports=request.form.get('ports', None)
                )

                db.session.add(new_server)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                flash('Сервер с таким именем уже существует!', 'error')

            return redirect(url_for('index'))
    else:
        operating_systems = OperatingSystem.query.all()
        server_purposes = ServerPurpose.query.all()
        dev_environments = DevEnvironments.query.all()
        projects = Projects.query.all()

        # Search
        search_query = request.args.get('search', '')
        if search_query:
            servers = db.session.query(Servers, DevEnvironments, OperatingSystem, ServerPurpose, Projects) \
                .join(DevEnvironments, Servers.dev_environment_id == DevEnvironments.id) \
                .join(OperatingSystem, Servers.os_id == OperatingSystem.id) \
                .join(ServerPurpose, Servers.server_purpose_id == ServerPurpose.id) \
                .join(Projects, Servers.project_id == Projects.id) \
                .filter(
                db.or_(
                    Servers.server_name.ilike(f"%{search_query}%"),
                    DevEnvironments.name.ilike(f"%{search_query}%"),
                    OperatingSystem.name.ilike(f"%{search_query}%"),
                    ServerPurpose.name.ilike(f"%{search_query}%"),
                    Projects.name.ilike(f"%{search_query}%"),
                    Projects.number.ilike(f"%{search_query}%"),
                    Servers.apps.ilike(f"%{search_query}%"),
                )
            ) \
                .paginate(page=page, per_page=per_page, error_out=False)
        else:
            servers = db.session.query(Servers, DevEnvironments, OperatingSystem, ServerPurpose, Projects) \
                .join(DevEnvironments, Servers.dev_environment_id == DevEnvironments.id) \
                .join(OperatingSystem, Servers.os_id == OperatingSystem.id) \
                .join(ServerPurpose, Servers.server_purpose_id == ServerPurpose.id) \
                .join(Projects, Servers.project_id == Projects.id) \
                .paginate(page=page, per_page=per_page, error_out=False)

        total_servers = Servers.query.count()

        return render_template('index.html',
                               operating_systems=operating_systems,
                               server_purposes=server_purposes,
                               dev_environments=dev_environments,
                               projects=projects,
                               servers=servers,
                               search_query=search_query,
                               total_servers=total_servers)


@app.route(base_url + '/delete/<int:server_id>', methods=['POST'])
def delete_server(server_id):
    server_to_delete = Servers.query.get_or_404(server_id)
    db.session.delete(server_to_delete)
    db.session.commit()
    return redirect(url_for('index'))


@app.route(base_url + '/add_project', methods=['POST'])
def add_project():
    new_project = Projects(name=request.form['project_name'])
    db.session.add(new_project)
    db.session.commit()
    return redirect(url_for('index'))


@app.route(base_url + '/add_operating_system', methods=['POST'])
def add_operating_system():
    new_operating_system = OperatingSystem(name=request.form['operating_system_name'])
    db.session.add(new_operating_system)
    db.session.commit()
    return redirect(url_for('index'))


@app.route(base_url + '/add_server_purpose', methods=['POST'])
def add_server_purpose():
    new_server_purpose = ServerPurpose(name=request.form['server_purpose_name'])
    db.session.add(new_server_purpose)
    db.session.commit()
    return redirect(url_for('index'))


# 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def teardown_request(exception=None):
    if exception:
        db.session.rollback()


# ------------------------------------------------------
# RESTful API
# ------------------------------------------------------
api_bp = Blueprint('api', __name__, url_prefix=base_url + '/api')
api = Api(api_bp)

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
        return {'message': 'Сервер успешно удален'}

    def put(self, server_id):
        args = parser.parse_args()
        server = Servers.query.get_or_404(server_id)

        for key, value in args.items():
            if value is not None:
                setattr(server, key, value)

        db.session.commit()
        return {'message': 'Сервер успешно обновлен'}


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
        return {'message': 'Сервер успешно добавлен'}


api.add_resource(ServerResource, '/server/<int:server_id>')
api.add_resource(ServerListResource, '/servers')

app.register_blueprint(api_bp)
