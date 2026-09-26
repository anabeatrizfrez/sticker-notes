import socket
import sys

_PORTA = 49152 + (hash("sticker-notes") % 16383)
_socket_lock = None


def adquirir() -> bool:
    global _socket_lock
    try:
        _socket_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket_lock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        _socket_lock.bind(("127.0.0.1", _PORTA))
        _socket_lock.listen(1)
        return True
    except OSError:
        _liberar_socket()
        return False


def liberar():
    _liberar_socket()


def _liberar_socket():
    global _socket_lock
    if _socket_lock:
        try:
            _socket_lock.close()
        except OSError:
            pass
        _socket_lock = None