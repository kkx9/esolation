import json
import os

import time

import config
import paramiko
import subprocess
from flask import Flask, request, render_template, jsonify
from extensions import register_extension, db
from orms import ContainerORM

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/test_data', methods=['POST'])
def test_data():
    data = {'Application': 'image_process', 'System': 'streambox'}
    return data
    # response = requests.post(url='http://127.0.0.1:5000/static/page/gpu_one.html', data=data)
    # print(response)


# @app.route('/clear_cache', methods=['GET'])
# def clear_cache():
#     esolation = './static/api/esolation/'
#     gpu = './static/api/gpu/'
#
#     esolations = os.listdir(esolation)
#     gpus = os.listdir(gpu)
#     try:
#         for e in esolations:
#             with open(esolation + e, 'r') as file:
#                 data = json.load(file)
#             for key in data:
#                 data[key] = []
#             file.close()
#             with open(esolation + e, 'w') as file:
#                 json.dump(data, file)
#             file.close()
#         for g in gpus:
#             with open(gpu + g, 'r') as file:
#                 data = json.load(file)
#             if 'pool' in g or 'latency' in g:
#                 for item in data['lines']:
#                     for key in item:
#                         item[key] = ""
#             else:
#                 for key in data:
#                     data[key] = []
#             file.close()
#             with open(gpu + g, 'w') as file:
#                 json.dump(data, file)
#             file.close()
#     except Exception as e:
#         print(e)
#         return jsonify({
#             "code": 2,
#             "msg": e
#         })
#     return jsonify({
#         "code": 1,
#         "msg": "清理缓存成功"
#     })


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()


test_image = "cve-image"


def create_container(enable, port):
    if enable:
        command = f"docker run --rm -d -p {port}:22 --privileged --runtime=vkernel-runtime {test_image}"
    else:
        command = f"docker run --rm -d -p {port}:22 --privileged {test_image}"

    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        # 获取容器 ID
        container_id = stdout.decode().strip()
        return container_id
    else:
        return ""


@app.post('/api/create')
def api_create_post():
    data = request.get_json()
    container = ContainerORM()
    container.update(data)
    id = create_container(data['enable'], data['port'])
    if id:
        container.container_id = id
    else:
        return {
            'code': -1,
            'msg': "容器创建失败"
        }
    try:
        container.save()
    except Exception as e:
        return {
            'code': -1,
            'msg': e
        }
    return {
        'code': 0,
        'msg': '容器创建成功'
    }


def exec_dmesg(container):
    try:
        container.client = paramiko.SSHClient()
        container.client.load_system_host_keys()
        container.client.set_missing_host_key_policy(paramiko.WarningPolicy())

        remote_host = '127.0.0.1'
        username = 'testuser'
        password = 'testuser'

        container.client.connect(hostname=remote_host, username=username, password=password, port=container.port)
    except paramiko.AuthenticationException:
        return {
            'code': -1,
            'output': '',
            'msg': '连接容器失败'
        }
    stdin, stdout, stderr = container.client.exec_command('dmesg')
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    container.client.close()
    if output:
        print(f"Output from remote host: {output}")
        return {
            'code': 0,
            'output': output,
            'msg': 'Success'
        }
    elif error:
        print(f"Error from remote host: {error}")
        return {
            'code': -1,
            'output': '',
            'msg': error
        }


@app.post('/api/exec/<int:id>')
def api_exec_post(id):
    container: ContainerORM = db.get_or_404(ContainerORM, id)
    return exec_dmesg(container)


def exec_scripts(s):
    path = "scripts/"
    script = path + s + ".sh"
    process = subprocess.Popen(['sh', script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               universal_newlines=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    if process.poll() == 0:
        return {
            'code': 0,
            'msg': '执行成功'
        }
    else:
        return {
            'code': -1,
            'msg': '执行失败'
        }


@app.post('/api/button/<string:id>')
def api_exec_button(id):
    return exec_scripts(id)


n = 0


@app.post('/api/button/image')
def api_exec_button1():
    time.sleep(5)
    global n
    if n == 4:
        n = 0
    n += 1
    print(n)
    return {
        'n': n
    }


m = 0


@app.post('/api/button/traffic')
def api_exec_button2():
    time.sleep(5)
    global m
    if m == 4:
        m = 0
    m += 1
    print(m)
    return {
        'm': m
    }


@app.delete('/api/del/<int:id>')
def api_container_del(id):
    container: ContainerORM = db.get_or_404(ContainerORM, id)
    command = f"docker rm -f {container.container_id}"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print(stdout)
    print(stderr)
    if process.returncode != 0:
        return {
            'code': -1,
            'msg': '容器删除失败'
        }
    try:
        db.session.delete(container)
        db.session.commit()
    except Exception as e:
        return {
            'code': -1,
            'msg': e
        }
    return {
        'code': 0,
        'msg': '容器删除成功'
    }


@app.route('/api/container')
def student_view():
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    paginate = ContainerORM.query.paginate(page=page, per_page=per_page, error_out=False)
    items: [ContainerORM] = paginate.items
    return {
        'code': 0,
        'msg': '信息查询成功',
        'count': paginate.total,
        'data': [
            {
                'id': item.id,
                'container_id': item.container_id,
                'port': item.port,
                'enable': item.enable,
                'create_at': item.create_at.strftime('%Y-%m-%d %H:%M:%S'),
            } for item in items
        ]
    }


app.config.from_object(config)
register_extension(app)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
