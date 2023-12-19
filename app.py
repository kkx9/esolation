import subprocess
import time

import paramiko
from flask import Flask, request, render_template
import config
from extensions import register_extension, db
from orms import ContainerORM

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.cli.command()
def create():
    db.drop_all()
    db.create_all()


@app.get('/container_add')
def student_add():
    return render_template('container_add.html')


test_image = "ubuntu"


def create_container(enable, port):
    return "asdfghjklzxcvbnmqwertyuiop123456"
    # if enable:
    #     command = f"docker run --rm -d --name vkernel -p {port}:22 --privileged --runtime=vkernel-runtime {test_image}"
    # else:
    #     command = f"docker run --rm -d --name cve -p {port}:22 --privileged {test_image}"
    #
    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # stdout, stderr = process.communicate()
    # if process.returncode == 0:
    #     # 获取容器 ID
    #     container_id = stdout.decode().strip()
    #     return container_id
    # else:
    #     return ""


def connect_container(container):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())

    remote_host = '127.0.0.1'
    username = 'testuser'
    password = 'testuser'

    client.connect(hostname=remote_host, username=username, password=password, port=container.port)

    # 使用paramiko.Channel和paramiko.invoke_shell实现交互式shell会话
    container.channel = client.invoke_shell()
    time.sleep(0.1)
    output = ""
    while not container.channel.recv_ready():
        continue
    while container.channel.recv_ready():
        output += container.channel.recv(65535).decode()
    print(output)


@app.post('/api/create')
def api_create_post():
    data = request.get_json()
    # data['create_at'] = datetime.strptime(data['create_at'], '%Y-%m-%d %H:%M:%S')
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
        # connect_container(container)
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


@app.post('/api/root/<int:id>')
def api_root(id):
    container: ContainerORM = db.get_or_404(ContainerORM, id)
    output = ""
    while container.channel.recv_ready():
        container.channel.recv(65535).decode()

    container.channel.send("sudo -u#-1 /bin/bash\n")
    time.sleep(0.1)
    while not container.channel.recv_ready():
        continue
    while container.channel.recv_ready():
        output += container.channel.recv(65535).decode()
    print(output)
    if 'Operation not permitted' in output:
        return {
            'code': -1,
            'msg': '提权失败'
        }
    else:
        return {
            'code': 0,
            'msg': '提权成功'
        }


def exec_command(container, command):
    print(command)
    command = f"/cdk.sh \"{command}\""
    flag = False
    ret = ""
    try:
        while container.channel.recv_ready():
            container.channel.recv(65535).decode()
        container.channel.send(f"{command}\n")
        time.sleep(0.5)
        output = ""
        while not container.channel.recv_ready():
            continue
        while container.channel.recv_ready():
            output += container.channel.recv(65535).decode()
        print(output)
        time.sleep(0.5)
        output = ""
        while not container.channel.recv_ready():
            continue
        while container.channel.recv_ready():
            output += container.channel.recv(65535).decode()
        print(output)
        if "exit status 1" in output:
            ret = output
        else:
            flag = True
            lines = output.strip().splitlines()
            filtered_lines = lines[1:]
            result = "\n".join(filtered_lines)
            ret = result
            print(result)

        container.client.close()
        container.client = None
        container.channel = None
        re = f"docker restart {container.container_id}"
        process = subprocess.Popen(re, shell=True)
        if process.returncode != 0:
            return {
                'code': -1,
                'msg': '容器重启失败'
            }
        time.sleep(0.1)
        connect_container(container)
    except Exception as e:
        return {
            'code': -1,
            'msg': e
        }
    container.results = ret
    container.status = flag
    container.save()
    if flag:
        return {
            'code': 0,
            'msg': '逃逸成功'
        }
    else:
        return {
            'code': -1,
            'msg': '逃逸失败'
        }


@app.post('/api/exec/<int:id>')
def api_exec_post(id):
    data = request.json  # 获取前端发送的 JSON 数据
    command = data.get('command')  # 获取命令值
    # 在这里可以根据需要处理命令，执行相应操作
    container: ContainerORM = db.get_or_404(ContainerORM, id)
    print(f"Received command '{command}' for container {container.container_id}")
    # return exec_command(container, command)
    container.status = False
    container.results = command
    container.save()
    return {
        'code': -1,
        'msg': '执行失败'
    }


@app.delete('/api/del/<int:id>')
def api_container_del(id):
    container: ContainerORM = db.get_or_404(ContainerORM, id)
    command = f"docker rm -f {container.container_id}"
    # process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # if process.returncode != 0:
    #     return {
    #         'code': -1,
    #         'msg': '容器删除失败'
    #     }
    try:
        db.session.delete(container)
        # container.is_del = True
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
                # 'command': None,
                'status': item.status,
                'results': item.results,
            } for item in items
        ]
    }


app.config.from_object(config)
register_extension(app)


if __name__ == '__main__':
    app.run(debug=True)
