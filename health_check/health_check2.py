import subprocess, itertools
import socket
import concurrent.futures

def generate_ips(prefix: str) -> list[str]:
    """
    x가 포함된 IP prefix를 파싱하여 IP 목록 생성
    예: "1.2.3.x" -> 1.2.3.0 ~ 1.2.3.255
        "1.2.x.x" -> 1.2.0.0 ~ 1.2.255.255
    """
    octets = prefix.split(".")
    
    if len(octets) != 4:
        raise ValueError("IP 형식은 4개의 옥텟이어야 합니다 (예: 1.2.3.x)")
    
    ranges = []
    for octet in octets:
        if octet.lower() == "x":
            ranges.append(range(0, 256))
        else:
            value = int(octet)
            if not 0 <= value <= 255:
                raise ValueError(f"유효하지 않은 옥텟 값: {value}")
            ranges.append([value])
    
    ips = [
        ".".join(map(str, combo))
        for combo in itertools.product(*ranges)
    ]
    
    return ips
def ping_check(ip):
    result = subprocess.run(
        ['ping', '-c', '2', '-W', '1', ip],
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
    prefix = "127.0.0.x" #x를 기준으로 IP탐색
    ips = generate_ips(prefix)
    
    # x 개수에 따른 범위 표시
    x_count = prefix.lower().count("x")
    total = 256 ** x_count
    
    print(f"Scanning {prefix} ({total} IPs)...")
    print("-" * 40)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        for result in executor.map(scan_ip, ips):
            if result:
                print(result)
if __name__ == "__main__":
    main()
