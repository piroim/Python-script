import subprocess
import socket
import concurrent.futures

def ping_check(ip):
    result = subprocess.run(
        ['ping', '-c', '1', '-W', '1', ip],
        capture_output=True
    )
    return result.returncode == 0

def tcp_check(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result == 0

def scan_ip(ip):
    results = []
    
    if ping_check(ip):
        results.append("ping-alive")
    
    for port in [80, 443]:
        if tcp_check(ip, port):
            results.append(f"port {port}")
    
    if results:
        return f"{ip} [{'] ['.join(results)}]"
    return None

def main():
    prefix = "127.0.0" #마지막 자리 수는 제외
    ips = [f"{prefix}.{i}" for i in range(1, 256)]
    
    print(f"Scanning {prefix}.1 ~ {prefix}.255...")
    print("-" * 40)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for result in executor.map(scan_ip, ips):
            if result:
                print(result)

if __name__ == "__main__":
    main()
