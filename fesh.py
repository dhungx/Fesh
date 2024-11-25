import os
import socket
import subprocess
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from cryptography.fernet import Fernet

# Tạo console để hiển thị giao diện đẹp
console = Console()

# Lệnh mẫu cho autocomplete
commands = ["ls", "cd", "exit", "help", "scan", "attack", "vpn"]
command_completer = WordCompleter(commands, ignore_case=True)

# Tạo khóa mã hóa lịch sử lệnh
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Ghi lịch sử lệnh (mã hóa)
def log_command(command):
    encrypted_command = cipher_suite.encrypt(command.encode())
    with open("fesh_history.log", "ab") as log_file:
        log_file.write(encrypted_command + b"\n")

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

# Hàm hiển thị thông tin hệ thống
def show_system_info():
    table = Table(title="Thông tin hệ thống")
    table.add_column("Thành phần", style="cyan")
    table.add_column("Trạng thái", style="green")
    table.add_row("CPU", f"{os.cpu_count()} cores")
    table.add_row("RAM", f"{os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') // (1024 ** 3)} GB")
    console.print(table)

# Hàm lấy prompt
def get_prompt():
    username = os.getenv("USER", "user")  # Lấy tên người dùng
    hostname = socket.gethostname()  # Lấy tên máy
    current_dir = os.getcwd()  # Lấy thư mục hiện tại
    return f"[bold green][{username}][/bold green]@[bold blue][{hostname}][/bold blue]:[bold yellow][{current_dir}][/bold yellow]$ "

# Shell chính
def fesh():
    console.print("[bold green]Chào mừng đến với Fesh - Fezen Shell![/bold green]")
    session = PromptSession(completer=command_completer)
    while True:
        try:
            # Gọi hàm get_prompt() để hiển thị dòng lệnh
            command = session.prompt(get_prompt())
            
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
                console.print("[bold cyan]Các lệnh khả dụng: ls, cd, exit, help, scan, attack, vpn[/bold cyan]")
            elif command == "scan":
                console.print("[bold yellow]Đang quét hệ thống...[/bold yellow]")
                # Thêm lệnh quét thực tế tại đây
            elif command == "attack":
                console.print("[bold red]CẢNH BÁO: Hành động tấn công cần xác nhận![/bold red]")
                # Thực thi tấn công tùy chỉnh tại đây
            elif command == "vpn":
                console.print("[bold cyan]Đang kết nối VPN...[/bold cyan]")
                # Tích hợp chức năng VPN tại đây
            elif command == "info":
                show_system_info()
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
