import asyncio
import datetime

class ChatServer:
    def __init__(self):
        self.rooms = {}
        self.clients = {}  # Track clients by username

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"{self.get_timestamp()} New connection from {addr}")

        # Request username
        writer.write("Welcome! Please enter your username: ".encode())
        await writer.drain()

        username = (await reader.readline()).decode().strip()

        if username in self.clients:
            writer.write("Username already taken. Disconnecting...\n".encode())
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return

        # Register the new client
        self.clients[username] = writer
        print(f"{self.get_timestamp()} {username} has connected.")
        writer.write(f"Hello, {username}! Type 'create <room>' to create a room, 'join <room>' to join a room, 'leave' to leave the current room, or 'exit' to exit.\n".encode())
        await writer.drain()

        current_room = None

        try:
            while True:
                message = (await reader.readline()).decode().strip()
                if not message:
                    break
                if message.lower() == 'exit':
                    break
                elif message.lower().startswith('create '):
                    room_name = message.split(' ', 1)[1]
                    if room_name not in self.rooms:
                        self.rooms[room_name] = set()
                    if current_room:
                        self.rooms[current_room].remove((username, writer))
                    current_room = room_name
                    self.rooms[room_name].add((username, writer))
                    writer.write(f"Room '{room_name}' created and joined.\n".encode())
                elif message.lower().startswith('join '):
                    room_name = message.split(' ', 1)[1]
                    if room_name in self.rooms:
                        if current_room:
                            self.rooms[current_room].remove((username, writer))
                        current_room = room_name
                        self.rooms[room_name].add((username, writer))
                        writer.write(f"Joined room '{room_name}'.\n".encode())
                    else:
                        writer.write(f"Room '{room_name}' does not exist.\n".encode())
                elif message.lower() == 'leave':
                    if current_room:
                        self.rooms[current_room].remove((username, writer))
                        writer.write(f"Left room '{current_room}'.\n".encode())
                        current_room = None
                    else:
                        writer.write("You are not in any room.\n".encode())
                elif current_room:
                    timestamp = self.get_timestamp()
                    for _, w in self.rooms[current_room]:
                        if w != writer:
                            w.write(f"{timestamp} {username}: {message}\n".encode())
                            await w.drain()
                else:
                    writer.write("You are not in any room. Create or join a room first.\n".encode())
                await writer.drain()
        except asyncio.CancelledError:
            pass
        finally:
            if current_room:
                self.rooms[current_room].remove((username, writer))
                if not self.rooms[current_room]:
                    del self.rooms[current_room]
            del self.clients[username]
            writer.close()
            await writer.wait_closed()
            print(f"{self.get_timestamp()} Connection closed for {username}")

    def get_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def main(self):
        server = await asyncio.start_server(self.handle_client, '127.0.0.1', 8888)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    server = ChatServer()
    asyncio.run(server.main())
