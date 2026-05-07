import socket, time

# 日本当前CDN IP
ips = ['162.159.35.152', '104.19.149.140', '162.159.152.11', '172.64.53.146', '172.64.48.95']

print("=== 从本地测试日本CDN IP延迟 ===")
for ip in ips:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        t0 = time.time()
        r = s.connect_ex((ip, 443))
        t1 = time.time()
        s.close()
        status = "OK" if r==0 else "FAIL"
        print(f"{ip}: {status} ({int((t1-t0)*1000)}ms)")
    except Exception as e:
        print(f"{ip}: ERROR {e}")

# 测试新加坡CDN IP
sg_ips = ['173.245.59.21', '8.35.211.141', '8.39.125.3', '108.162.195.110', '162.159.4.12']
print("\n=== 从本地测试新加坡CDN IP延迟 ===")
for ip in sg_ips:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        t0 = time.time()
        r = s.connect_ex((ip, 443))
        t1 = time.time()
        s.close()
        status = "OK" if r==0 else "FAIL"
        print(f"{ip}: {status} ({int((t1-t0)*1000)}ms)")
    except Exception as e:
        print(f"{ip}: ERROR {e}")
