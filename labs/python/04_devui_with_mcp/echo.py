from colorama import Fore, Style, init

init(autoreset=True)


class Echo:
    # === Public methods ===
    @staticmethod
    def system(text: str, nl: bool = True):
        Echo._write("⚙ :", text, Fore.LIGHTBLACK_EX, nl)

    @staticmethod
    def debug(text: str, nl: bool = True):
        Echo._write("🐛:", text, Fore.LIGHTWHITE_EX, nl)

    @staticmethod
    def info(text: str, nl: bool = True):
        Echo._write("ℹ :", text, Fore.CYAN, nl)

    @staticmethod
    def user(text: str, nl: bool = True):
        Echo._write("🧑:", text, Fore.YELLOW, nl)

    @staticmethod
    def agent(text: str, nl: bool = True):
        Echo._write("🤖:", text, Fore.GREEN, nl)

    @staticmethod
    def warn(text: str, nl: bool = True):
        Echo._write("⚠ :", text, Fore.MAGENTA, nl)

    @staticmethod
    def step(text: str, nl: bool = True):
        Echo._write("✔ :", text, Fore.LIGHTYELLOW_EX, nl)

    @staticmethod
    def error(text: str, nl: bool = True):
        Echo._write("⛔:", text, Fore.RED, nl)

    @staticmethod
    def done(text: str, nl: bool = True):
        Echo._write("✅:", text, Fore.CYAN, nl)

    # === Helpers ===
    @staticmethod
    def _write(symbol: str, msg: str, color: str, nl: bool):
        end = "\n" if nl else ""
        print(color + symbol + " " + msg + Style.RESET_ALL, end=end)
