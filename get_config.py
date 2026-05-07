from audit_config import get_servers
from ssh_utils import ssh_connect, run_command

for srv in get_servers():
    print(f"\n{'='*50}")
    print(f"=== {srv['name']} ===")
    print(f"{'='*50}")

    with ssh_connect(srv) as c:
        cmd = 'cat /root/singbox-eps-node/config.json'
        out, err = run_command(c, cmd)

        with open(f'config_{srv["name"]}.json', 'w', encoding='utf-8') as f:
            f.write(out)

        print(f"config.json已保存到本地: config_{srv['name']}.json")
        print(f"文件大小: {len(out)} 字节")

print("\n全部完成")
