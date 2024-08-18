import asyncio

class ChatClient:
    def __init__(self):
        self.reader = None
        self.writer = None

    async def connect(self, host, port):
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def send_message(self, message):
        self.writer.write(message.encode() + b'\n')
        await self.writer.drain()

    async def receive_messages(self):
        while True:
            data = await self.reader.readline()
            if not data:
                break
            print(data.decode(), end='')

    async def main(self):
        await self.connect('127.0.0.1', 8888)
        receive_task = asyncio.create_task(self.receive_messages())
        try:
            while True:
                message = await asyncio.get_event_loop().run_in_executor(None, input)
                await self.send_message(message)
                if message.lower() == 'quit':
                    break
        finally:
            receive_task.cancel()
            self.writer.close()
            await self.writer.wait_closed()

if __name__ == "__main__":
    client = ChatClient()
    asyncio.run(client.main())
    