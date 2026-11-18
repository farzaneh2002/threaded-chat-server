import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 5556


def receive_loop(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\n[server closed the connection]")
                break
            print(f"\r{data.decode('utf-8', errors='replace').strip()}\n> ", end="")
        except OSError:
            break


def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Could not connect. Is the server running?")
        sys.exit(1)

    prompt = sock.recv(1024).decode("utf-8").strip()
    print(prompt, end=" ")
    name = input()
    sock.sendall(name.encode("utf-8"))

    print(f"Connected as {name}. Type 'quit' to leave.")

    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input("> ")
            if msg.lower() in ("quit", "exit"):
                break
            if msg.strip():
                sock.sendall(msg.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sock.close()
        print("Disconnected.")


if __name__ == "__main__":
    start_client()
