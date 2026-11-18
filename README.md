# Threaded Chat Room

A multi-client TCP chat room with Python. The server broadcasts every
message to all other connected clients. One thread per connection, no
dependencies, no frameworks.

## Run it

Terminal 1:
    python server.py

Terminal 2+ (at least two to see the broadcast):
    python client.py

Pick a username when prompted. Anything you type gets sent to everyone
else in the room. Type `quit` to leave.

## What's interesting in the code

- **Shared client registry** — `clients` maps `socket -> username`, guarded
  by a single `threading.Lock`. Every read or write of the dict goes
  through it.

- **Broadcast outside the lock** — `broadcast()` snapshots the client list
  under the lock, then does all `sendall` calls with the lock released.
  Holding a lock while blocking on I/O would serialize every message
  through the server.

- **Dead-client cleanup** — if one client's socket dies mid-broadcast, the
  failure is caught per-client and the dead connection is removed after
  the loop. A single broken client can't stop the broadcast for everyone
  else.

- **Username collision is rejected, not suffixed** — if you ask to be
  `alice` and someone else is already `alice`, you're told to pick again.

## Known limitations

- No authentication — the username is whatever you type.
- No per-client send lock — two simultaneous broadcasts to the same client
  could theoretically interleave bytes. Rare in practice on localhost.
- Messages are one line each. No history for late joiners.

## Possible next steps

- Per-client send lock
- Message history so new joiners see recent chat
- `/nick` command to rename mid-session
- JSON-lines protocol instead of plain text
