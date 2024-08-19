import asyncio

class ChatClient:
    def __init__(self):
        self.reader = None
        self.writer = None

    async def connect(self, host, port):
        try:
            self.reader, self.writer = await asyncio.open_connection(host, port)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            raise

    async def send_message(self, message):
        try:
            self.writer.write(message.encode() + b'\n')
            await self.writer.drain()
        except Exception as e:
            print(f"Failed to send message: {e}")

    async def receive_messages(self):
        while True:
            try:
                data = await self.reader.readline()
                if not data:
                    break
                print(data.decode(), end='')
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    async def main(self):
        await self.connect('127.0.0.1', 8888)

        # Prompt for username
        while True:
            username = input("Welcome! Please enter your username: ")
            await self.send_message(username)
            response = await self.reader.readline()
            if b"Username already taken" in response:
                print("Username already taken, please choose a different one.")
            else:
                print(response.decode(), end='')
                break

        receive_task = asyncio.create_task(self.receive_messages())
        try:
            while True:
                # Add "you: " before user input
                message = await asyncio.get_event_loop().run_in_executor(None, lambda: input(">"))
                if message.strip().lower() == 'exit':
                    break
                # Print "you: " before sending the message
                print(f"you: {message}")
                await self.send_message(message)
        except KeyboardInterrupt:
            print("\nDisconnected.")
        finally:
            receive_task.cancel()
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception as e:
                print(f"Error closing connection: {e}")

if __name__ == "__main__":
    client = ChatClient()
    asyncio.run(client.main())