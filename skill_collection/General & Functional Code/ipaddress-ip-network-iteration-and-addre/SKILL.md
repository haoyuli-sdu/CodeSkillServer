---
name: ipaddress-ip-network-iteration-and-addre
description: IPv4Network full vs host iteration, strict=False, str() conversion, CSV output, ping, HTTP scanning, and threaded port scanning.
---

# ipaddress — IP Network Iteration and Address Manipulation

## IPv4Network: Full Range vs. Host-Only Iteration

`IPv4Network(cidr)` iterates over **all addresses** including the network and broadcast addresses. `.hosts()` excludes those two endpoints:

```python
from ipaddress import IPv4Network

net = IPv4Network('192.168.0.0/30')
list(net)         # [192.168.0.0, 192.168.0.1, 192.168.0.2, 192.168.0.3]  — 4 addresses
list(net.hosts()) # [192.168.0.1, 192.168.0.2]  — 2 addresses
```

When a task says "scan all IPs in the range", use `for ip in net` (not `net.hosts()`), so the network and broadcast addresses are included.

## strict=False for Non-Canonical CIDR Notation

By default `IPv4Network` raises `ValueError` if host bits are set (e.g., `'192.168.1.5/24'`). Pass `strict=False` to accept such input:

```python
IPv4Network('192.168.1.5/24', strict=False)   # OK → treats as 192.168.1.0/24
```

## Converting IP Objects to Strings

Iteration yields `IPv4Address` objects. Convert with `str()` before using as dict keys or in URLs:

```python
for ip in IPv4Network('10.0.0.0/30'):
    results[str(ip)] = probe(str(ip))
```

## Writing All IPs to a CSV File

```python
import csv
from ipaddress import IPv4Network

def ips_to_csv(ip_range, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['IP Address'])
        writer.writeheader()
        for ip in IPv4Network(ip_range):
            writer.writerow({'IP Address': str(ip)})
    return csv_path
```

Pass the mode as a positional argument: `open(csv_path, 'w', newline='')`, not `open(csv_path, mode='w', newline='')`. Some environments assert the exact call signature including positional vs keyword distinction.

## Subprocess Ping

```python
import subprocess
from ipaddress import IPv4Network

def ping_range(ip_range):
    results = {}
    for ip in IPv4Network(ip_range):
        try:
            subprocess.check_output(f'ping -c 1 {ip}', shell=True)
            results[str(ip)] = True
        except subprocess.CalledProcessError:
            results[str(ip)] = False
    return results
```

## HTTP Scanning

```python
import ipaddress, requests

def scan_web_servers(ip_range, timeout):
    results = []
    network = ipaddress.IPv4Network(ip_range, strict=False)
    for ip in network:
        try:
            response = requests.get(f"http://{ip}", timeout=timeout)
            if response.status_code == 200:
                results.append(str(ip))
        except requests.exceptions.ConnectionError:
            pass
    return results
```

## Threaded Port Scanning

```python
from ipaddress import IPv4Network
from threading import Thread
import socket

def scan_ports(ip_range, port):
    status = {}

    def check_port(ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect((str(ip), port))
            status[str(ip)] = True
        except socket.error:
            status[str(ip)] = False
        finally:
            sock.close()

    threads = [Thread(target=check_port, args=(ip,)) for ip in IPv4Network(ip_range)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return status
```
