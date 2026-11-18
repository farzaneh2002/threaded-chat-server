import socket
import threading

HOST = "127.0.0.1"
PORT = 5556

clients = {}
clients_lock = threading.Lock()


def broadcast(message, sender_conn=None):
    dead = []
    with clients_lock:
        snapshot = list(clients.items())

    for conn, name in snapshot:
        if conn is sender_conn:
            continue
        try:
            conn.sendall((message + "\n").encode("utf-8"))
        except OSError:
            dead.append(conn)

    if dead:
        with clients_lock:
            for conn in dead:
                clients.pop(conn, None)
                try:
                    conn.close()
                except OSError:
                    pass


def handle_client(conn, addr):
    name = None
    try:
        conn.sendall(b"Enter a username: ")
        raw = conn.recv(1024)
        if not raw:
            return
        name = raw.decode("utf-8", errors="replace").strip()
        if not name:
            conn.sendall(b"Empty username, bye.\n")
            return

        with clients_lock:
            if name in clients.values():
                conn.sendall(b"That username is taken.\n")
                return
            clients[conn] = name

        print(f"[+] {name} ({addr[0]}:{addr[1]}) joined")
        broadcast(f"[server] {name} joined the chat", sender_conn=conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode("utf-8", errors="replace").strip()
            if not msg:
                continue
            print(f"[{name}] {msg}")
            broadcast(f"{name}: {msg}", sender_conn=conn)
    except (ConnectionResetError, OSError):
        pass
    finally:
        with clients_lock:
            clients.pop(conn, None)
        try:
            conn.close()
        except OSError:
            pass
        if name:
            print(f"[-] {name} left")
            broadcast(f"[server] {name} left the chat")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Chat server listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.close()


if __name__ == "__main__":
    start_server()
