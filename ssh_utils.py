import paramiko
import socket
import sys
from contextlib import contextmanager


@contextmanager
def ssh_connect(server_config):
    """SSH连接上下文管理器，确保连接在finally中关闭

    server_config: dict, 包含 host, port, username, password
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            server_config['host'],
            port=server_config.get('port', 22),
            username=server_config['username'],
            password=server_config['password'],
            timeout=15,
            allow_agent=False,
            look_for_keys=False,
        )
        yield client
    except paramiko.SSHException as e:
        print(f"SSH连接失败: {e}", file=sys.stderr)
        raise
    except socket.error as e:
        print(f"网络连接失败: {e}", file=sys.stderr)
        raise
    finally:
        client.close()


def run_command(client, cmd, timeout=30):
    """执行远程命令，返回(stdout_text, stderr_text)"""
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err
