import os
import sys

_ENV_LOADED = False
_ENV_VARS = {}


def _load_env():
    global _ENV_LOADED, _ENV_VARS
    if _ENV_LOADED:
        return
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        print(f"错误: .env 文件不存在: {env_path}", file=sys.stderr)
        sys.exit(1)
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            _ENV_VARS[key.strip()] = value.strip()
    _ENV_LOADED = True


def get(key, default=None):
    _load_env()
    value = _ENV_VARS.get(key)
    if value is None:
        if default is not None:
            return default
        print(f"错误: .env 中缺少配置项 {key}", file=sys.stderr)
        sys.exit(1)
    return value


def get_servers():
    return [
        {
            'name': '日本',
            'host': get('SERVER_JP_HOST'),
            'port': int(get('SERVER_JP_PORT', '22')),
            'username': get('SERVER_JP_USER'),
            'password': get('SERVER_JP_PASSWORD'),
        },
        {
            'name': '日本(旧IP)',
            'host': get('SERVER_JP_OLD_HOST'),
            'port': int(get('SERVER_JP_OLD_PORT', '22')),
            'username': get('SERVER_JP_OLD_USER'),
            'password': get('SERVER_JP_OLD_PASSWORD'),
        },
        {
            'name': '新加坡',
            'host': get('SERVER_SG_HOST'),
            'port': int(get('SERVER_SG_PORT', '22')),
            'username': get('SERVER_SG_USER'),
            'password': get('SERVER_SG_PASSWORD'),
        },
    ]


def get_server_old_jp():
    return {
        'host': get('SERVER_JP_OLD_HOST'),
        'port': int(get('SERVER_JP_OLD_PORT', '22')),
        'username': get('SERVER_JP_OLD_USER'),
        'password': get('SERVER_JP_OLD_PASSWORD'),
    }
