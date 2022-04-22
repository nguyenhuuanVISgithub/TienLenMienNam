from colorama import Fore, Style

def printBlueColor(message):
    print(Fore.LIGHTBLUE_EX + message, end='')
    print(Style.RESET_ALL)

def printRedColor(message):
    print(Fore.LIGHTRED_EX + message, end='')
    print(Style.RESET_ALL)

def printCyanColor(message):
    print(Fore.LIGHTCYAN_EX + message, end='')
    print(Style.RESET_ALL)
  
def printGreenColor(message):
    print(Fore.LIGHTGREEN_EX + message, end='')
    print(Style.RESET_ALL)

def printMagentaColor(message):
    print(Fore.LIGHTMAGENTA_EX + message, end='')
    print(Style.RESET_ALL)

def printYellowColor(message):
    print(Fore.LIGHTYELLOW_EX + message, end='')
    print(Style.RESET_ALL)