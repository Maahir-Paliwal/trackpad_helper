import socket

class HammerSpoonBackend:
    def __init__(self, host: str = "127.0.0.1", port: int = 7777) -> None:
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def scroll(self, dy:int) -> None:
        # Hammerspoon receiver expects: "SCROLL <dy>"
        msg = f"SCROLL {dy}".encode("utf-8")
        self.sock.sendto(msg, self.addr)