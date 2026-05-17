"""Tests for zero-copy write optimisation using memoryview."""

import socket
import threading

from httpcore2._backends.sync import SyncStream


def test_sync_stream_write_sends_all_bytes():
    """SyncStream.write() must deliver every byte even when send() returns partial writes."""
    payload = b"hello " * 10_000  # 60 KB

    reader_sock, writer_sock = socket.socketpair()
    received: list[bytes] = []

    def reader() -> None:
        chunks = []
        while True:
            chunk = reader_sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
        received.append(b"".join(chunks))
        reader_sock.close()

    t = threading.Thread(target=reader)
    t.start()

    stream = SyncStream(writer_sock)
    stream.write(payload)
    writer_sock.close()

    t.join()
    assert received[0] == payload
