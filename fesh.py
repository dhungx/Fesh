import os
import socket
import subprocess
import psutil
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import track
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from cryptography.fernet import Fernet

# Console giao diện đẹp
console = Console()

# Danh sách lệnh có sẵn
commands = ["ls", "cd", "exit", "help", "scan", "attack", "vpn", "history", "alias", "info", "check", "run", "plugin"]
command_completer = WordCompleter(commands, ignore_case=True)

# Tạo khóa mã hóa lịch sử lệnh
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Lưu alias (lệnh tùy chỉnh)
aliases = {}

# Lưu lịch sử lệnh
history = []

# Danh sách tiến trình đáng ngờ
blacklist_processes = ["malware.exe", "spyware.py"]

# Ghi lịch sử lệnh (mã hóa)
def log_command(command):
    encrypted_command = cipher_suite.encrypt(command.encode())
    with open("fesh_history.log", "ab") as log_file:
        log_file.write(encrypted_command + b"\n")
    history.append(command)

# Thực thi lệnh
def execute_command(command):
    try:
        if "rm -rf /" in command or "shutdown" in command:
            console.print("[bold red]CẢNH BÁO: Lệnh nguy hiểm đã bị chặn![/bold red]")
            return
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        console.print(result.stdout if result.stdout else "[bold yellow]Không có kết quả trả về.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Lỗi: {e}[/bold red]")

# Kiểm tra tiến trình độc hại
def check_processes():
    console.print("[bold yellow]Đang kiểm tra các tiến trình...[/bold yellow]")
    for proc in track(psutil.process_iter(['pid', 'name']), description="Đang quét"):
        try:
            process_name = proc.info['name']
            if process_name in blacklist_processes:
                console.print(f"[bold red]Phát hiện tiến trình nguy hiểm: {process_name} (PID: {proc.info['pid']})[/bold red]")
        except Exception:
            continue

# Hàm hiển thị thông tin hệ thống
def show_system_info():
    table = Table(title="Thông tin hệ thống")
    table.add_column("Thành phần", style="cyan")
    table.add_column("Trạng thái", style="green")
    table.add_row("CPU", f"{os.cpu_count()} cores")
    table.add_row("RAM", f"{os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') // (1024 ** 3)} GB")
    table.add_row("Dung lượng ổ cứng", f"{psutil.disk_usage('/').percent}% đã sử dụng")
    table.add_row("Kết nối mạng", f"{len(psutil.net_connections())} kết nối")
    console.print(table)

# Hàm lấy prompt
def get_prompt():
    username = os.getenv("USER", "user")
    hostname = socket.gethostname()
    current_dir = os.getcwd()
    time_now = datetime.now().strftime("%H:%M:%S")
    disk_free = psutil.disk_usage('/').free // (1024**3)
    return f"[bold green][{username}][/bold green]@[bold blue][{hostname}][/bold blue]:[bold yellow][{current_dir}][/bold yellow] ([bold magenta]{time_now}[/bold magenta] | Free Disk: {disk_free} GB)$ "

# Tạo alias
def add_alias(alias_name, command):
    aliases[alias_name] = command
    console.print(f"[bold cyan]Alias thêm thành công: {alias_name} -> {command}[/bold cyan]")

# Xử lý alias
def handle_alias(command):
    parts = command.split(" ", 1)
    if parts[0] in aliases:
        return f"{aliases[parts[0]]} {parts[1]}" if len(parts) > 1 else aliases[parts[0]]
    return command

# Shell chính
def fesh():
    console.print("[bold green]Chào mừng đến với Fesh - Fezen Shell![/bold green]")
    session = PromptSession(completer=command_completer)
    while True:
        try:
            # Gọi hàm get_prompt() để hiển thị dòng lệnh
            command = session.prompt(get_prompt()).strip()
            
            # Xử lý alias
            command = handle_alias(command)
            
            # Lệnh đặc biệt
            if command in ["exit", "quit"]:
                console.print("[bold red]Tạm biệt![/bold red]")
                break
            elif command.startswith("cd"):
                try:
                    target_dir = command.split(" ", 1)[1] if " " in command else os.getenv("HOME", "/")
                    os.chdir(target_dir)
                except FileNotFoundError:
                    console.print(f"[bold red]Thư mục không tồn tại: {target_dir}[/bold red]")
            elif command == "help":
                console.print("[bold cyan]Các lệnh khả dụng: ls, cd, exit, help, scan, attack, vpn, history, alias, info, check, run, plugin[/bold cyan]")
            elif command == "scan":
                console.print("[bold yellow]Đang quét hệ thống...[/bold yellow]")
                check_processes()
            elif command == "attack":
                console.print("[bold red]CẢNH BÁO: Hành động tấn công cần xác nhận![/bold red]")
                # Thực thi tấn công tùy chỉnh tại đây
            elif command == "vpn":
                console.print("[bold cyan]Đang kết nối VPN...[/bold cyan]")
                # Tích hợp chức năng VPN tại đây
            elif command == "info":
                show_system_info()
            elif command == "history":
                console.print("[bold cyan]Lịch sử lệnh:[/bold cyan]")
                for i, cmd in enumerate(history, 1):
                    console.print(f"{i}: {cmd}")
            elif command.startswith("alias "):
                try:
                    alias_name, alias_command = command.split(" ", 1)[1].split("=")
                    add_alias(alias_name.strip(), alias_command.strip())
                except ValueError:
                    console.print("[bold red]Cú pháp alias không hợp lệ! Dùng: alias [tên]=[lệnh][/bold red]")
            elif command.startswith("run "):
                script = command.split(" ", 1)[1]
                if os.path.exists(script) and script.endswith(".sh"):
                    execute_command(f"bash {script}")
                else:
                    console.print("[bold red]Script không hợp lệ hoặc không tồn tại![/bold red]")
            elif command.startswith("plugin "):
                console.print("[bold yellow]Tải và cài đặt plugin (chức năng đang phát triển)...[/bold yellow]")
                # Tích hợp tải plugin tại đây
            else:
                execute_command(command)
                log_command(command)
        except KeyboardInterrupt:
            console.print("\n[bold red]Sử dụng 'exit' để thoát![/bold red]")
        except EOFError:
            console.print("\n[bold red]Tạm biệt![/bold red]")
            break

if __name__ == "__main__":
    fesh()
