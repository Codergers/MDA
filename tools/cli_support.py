import json
import locale
import os
import platform
import sys
from pathlib import Path
from typing import Callable


class Ansi:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

LANG_MAP = {
    "Chinese (Simplified)_China": "zh_cn",
    "Chinese (Traditional)_Taiwan": "zh_cn",
    "zh_cn": "zh_cn",
    "zh_tw": "zh_cn",
}


def configure_utf8_stdio() -> None:
    """Keep Python CLI output readable in Windows terminals using UTF-8 files."""
    if platform.system() != "Windows":
        return

    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass


configure_utf8_stdio()


def _enable_windows_virtual_terminal() -> bool:
    if platform.system() != "Windows":
        return False
    try:
        import ctypes
        from ctypes import wintypes

        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

        kernel32 = ctypes.windll.kernel32
        kernel32.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel32.GetStdHandle.restype = wintypes.HANDLE
        kernel32.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel32.GetConsoleMode.restype = wintypes.BOOL
        kernel32.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.SetConsoleMode.restype = wintypes.BOOL

        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        handle_value = ctypes.c_void_p(handle).value

        if handle_value in (None, 0, INVALID_HANDLE_VALUE):
            return False

        mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False

        if mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
            return True

        return bool(kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))
    except Exception:
        return False


def supports_color() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR") is not None:
        return True
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if platform.system() == "Windows":
        return _enable_windows_virtual_terminal()
    return os.environ.get("TERM", "") not in ("", "dumb")


class Console:
    enabled = supports_color()

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        if not cls.enabled:
            return text
        return f"{color}{text}{Ansi.RESET}"

    @classmethod
    def hdr(cls, text: str) -> str:
        return cls.colorize(text, Ansi.MAGENTA)

    @classmethod
    def ok(cls, text: str) -> str:
        return cls.colorize(text, Ansi.GREEN)

    @classmethod
    def warn(cls, text: str) -> str:
        return cls.colorize(text, Ansi.YELLOW)

    @classmethod
    def err(cls, text: str) -> str:
        return cls.colorize(text, Ansi.RED)

    @classmethod
    def step(cls, text: str) -> str:
        """Return a step label string, e.g. for multi-step CLI workflows."""
        return cls.colorize(text, Ansi.MAGENTA)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.colorize(text, Ansi.CYAN)


def init_localization(
    locals_dir: Path,
    lang_map: dict[str, str] = LANG_MAP,
    default_lang: str = "en_us",
) -> tuple[Callable[..., str], str | None]:
    loc = locale.getlocale()
    lang = (loc[0] or "") if loc else ""

    if lang in lang_map:
        lang = lang_map[lang]
    elif lang.lower() in lang_map:
        lang = lang_map[lang.lower()]
    else:
        lang = default_lang

    lang_res: dict[str, str] = {}
    locale_file = locals_dir / f"{lang}.json"
    load_error_path: str | None = None

    try:
        with open(locale_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            lang_res = {str(k): str(v) for k, v in data.items()}
    except FileNotFoundError:
        load_error_path = str(locale_file)
        print(Console.err(f"[localization] locale file not found: {locale_file}"))
    except json.JSONDecodeError as e:
        load_error_path = str(locale_file)
        print(Console.err(f"[localization] failed to decode locale json: {locale_file}: {e}"))
    except OSError as e:
        load_error_path = str(locale_file)
        print(Console.err(f"[localization] failed to read locale file: {locale_file}: {e}"))
    except Exception as e:
        load_error_path = str(locale_file)
        print(Console.err(f"[localization] unexpected error while loading locale file: {locale_file}: {e}"))

    def t(key: str, **kwargs) -> str:
        template = lang_res.get(key, key)
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    return t, load_error_path
