"""Garante que só uma instância do app roda por vez.

Usa um socket local (loopback) como lock — funciona em Windows e Linux
sem precisar de bibliotecas extras. Se já houver uma instância rodando,
`adquirir()` retorna False e o processo novo deve encerrar imediatamente.
"""

import socket
import sys

# Porta local usada como lock. Deve ser única por app — mude se conflitar
# com outro programa na sua máquina. Intervalo seguro: 49152–65535.
_PORTA = 57321
_socket_lock = None


def adquirir() -> bool:
    """Tenta adquirir o lock de instância única.

    Retorna True se este processo é o único rodando (lock adquirido).
    Retorna False se já existe outro processo com o lock (app já aberto).
    """
    global _socket_lock
    try:
        _socket_lock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR desabilitado de propósito: queremos falhar se a
        # porta já estiver em uso por outra instância.
        _socket_lock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        _socket_lock.bind(("127.0.0.1", _PORTA))
        _socket_lock.listen(1)
        return True
    except OSError:
        # Porta já ocupada = outra instância rodando.
        _liberar_socket()
        return False


def liberar():
    """Libera o lock ao encerrar o app (chamado automaticamente pelo atexit)."""
    _liberar_socket()


def _liberar_socket():
    global _socket_lock
    if _socket_lock:
        try:
            _socket_lock.close()
        except OSError:
            pass
        _socket_lock = None