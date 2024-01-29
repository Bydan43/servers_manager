from flask import render_template, request, redirect, url_for, flash, send_from_directory
from sqlalchemy.exc import IntegrityError
from app import app, db, base_url
from app.models import *



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


# Form for editing server records
@app.route(base_url + '/edit/<int:server_id>', methods=['GET', 'POST'])
def edit_server(server_id):
    server = Servers.query.get_or_404(server_id)

    if request.method == 'POST':
        # Processing the edit form
        server.server_name = request.form['server_name']
        server.ip_address = request.form['ip_address']
        server.os_id = int(request.form['os_id'])
        server.server_purpose_id = int(request.form['server_purpose_id'])
        server.dev_environment_id = int(request.form['dev_environment_id'])
        server.project_id = int(request.form['project_id'])
        server.apps = request.form.get('apps', None)
        server.note = request.form.get('note', None)
        server.ports = request.form.get('ports', None)

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('inc/edit_server.html', server=server, projects=Projects.query.all(),
                           operating_systems=OperatingSystem.query.all(),
                           server_purposes=ServerPurpose.query.all(),
                           dev_environments=DevEnvironments.query.all())

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
