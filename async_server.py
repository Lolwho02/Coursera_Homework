import asyncio


class Worker:

    def __init__(self, client, data):
        self.data = data
        self.client = client
        self.output = 'ok\n\n'

    def validation_error(self):
        return 'error\nwrong command\n\n'

    def get(self):
        only_data = self.data[4:]
        splited = only_data.split('\n')
        splited.remove('')
        if len(splited) == 0:
            self.validation_error()
        for d in splited:
            if d not in self.client.storage.keys():
                return 'ok\n\n'
            else:
                for values in self.client.storage[d]:
                    self.output+=d + ' ' + str(values[0]) + ' ' + str(values[1]) + '\n'
        return self.output

    def get_all(self):
        if len(self.client.storage) != 0:
            return str(self.client.storage)
        else:
            return 'ok\n\n'

    def put(self):
        only_data = self.data[4:len(self.data)-2]
        splited = only_data.split(' ')
        if splited[0] not in self.client.storage:
            self.client.storage[splited[0]] = []
        self.client.storage[splited[0]].append((splited[1], splited[2]))
        return 'ok\n\n'


class ClientServerProtocol(asyncio.Protocol):

    storage = {}


    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.data = data
        data_decoded = self.data.decode()
        self.worker = Worker(client = self, data = data_decoded)
        if data_decoded == 'get *\n' in data_decoded:
            print('Получен *')
            resp = self.worker.get_all()
            print(resp)
        elif data_decoded.startswith('get') and '*' not in data_decoded:
            resp = self.worker.get()
            print(resp)
        elif data_decoded.startswith('put') and '*' not in data_decoded:
            resp = self.worker.put()
            print(resp)
        else:
            resp = self.worker.validation_error()
        self.transport.write(resp.encode())

def run_server(host, port):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ClientServerProtocol,
        host, port
    )

    server = loop.run_until_complete(coro)
    print('Сервер запущен')

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    run_server('127.0.0.1', 8888)
