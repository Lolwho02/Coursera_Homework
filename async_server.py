import asyncio
import re

class Worker:
    """Класс Работник, при получении новых данных создается объект данного класса"""

    def __init__(self, client, data):
        self.data = data  # полученные данные
        self.client = client  # клиент который передал данные
        self.output = 'ok\n'  # строка положительного ответа

    def validation_error(self):
        """Метод возвращающий информацию о неправильном запросе"""

        return 'error\nwrong command\n\n'  # сообщение при неверном запросе


    def get(self):
        """Метод обрабатывающий запрос get"""

        if len(re.findall('\s', self.data)) > 2 or len(re.findall('\s', self.data)) == 1:  # проверка числа пробелов
            return self.validation_error()  # если в запросе один или более двух пробелов сообщение неверного запроса

        only_data = self.data[4:]  # отделяет только данные запроса без метода запроса(get)
        splited = only_data.split('\n')  # разделяет данные по пробелам

        splited.remove('')  # необходимо для верификации невалидных запросов, split('\n') вернёт ['']
        if len(splited) == 0 :  # если запрос не валиден возвращает сообщение о неправильном запросе
            return 'error\nwrong command\n\n'

        for d in splited:
            if d not in self.client.storage.keys():
                return 'ok\n\n'  # ответ на запрос по не существующему ключу
            else:
                for values in self.client.storage[d]:
                    self.output+=d + ' ' + str(values[0]) + ' ' + str(values[1]) + '\n'
        return self.output + '\n'  # возвращает данные по ключу в хранилище

    def get_all(self):
        """Метод обрабатывающий запрос на получение всех данных get *"""

        if len(self.client.storage) != 0:  # вернёт все данные из хранилища если оно не пустое
            for key in self.client.storage.keys():
                for values in self.client.storage[key]:
                    self.output += key + ' ' + str(values[0]) + ' ' + str(values[1]) + '\n'
            return self.output + '\n'
        else:
            return 'ok\n\n'  # выполняется в случае пустого хранилища, сообщение о том что запрос был валиден

    def put(self):
        """Метод обрабатывающий запрос на сохранение данных на сервере"""

        only_data = self.data[4:len(self.data)-1]  # получаем данные запроса
        splited = only_data.split(' ')  # данные запроса кладём в список: [имя, значение, время]

        # блок валидации
        if len(splited) > 3:
            return self.validation_error()
        try:  # проверка данных на правильность типа(значение - число, время - целое число)
            splited[1] = float(splited[1])
            splited[2] = int(splited[2])
        except ValueError:
            return self.validation_error()  # если данные не правильные отпрака сообщения о неправильном запросе

        # блок работы с данными
        if splited[0] not in self.client.storage:  # добавляем новое имя метрики в хранилище
            self.client.storage[splited[0]] = []

        if (splited[1], splited[2]) not in self.client.storage[splited[0]]:  # добавляет только уникальные данные метрики
            self.client.storage[splited[0]].append((splited[1], splited[2]))

            for i in range(len(self.client.storage[splited[0]])):  # проверка на уникальность времени метрики
                if splited[2] in self.client.storage[splited[0]][i]:  # событие при отправки двух метрик в одно время
                    self.client.storage[splited[0]][i] = (splited[1], splited[2])  # перезапись значения метрики

            for i in range(len(self.client.storage[splited[0]])-1):  # удаление повторных метрик, появившихся из-за перезаписи
                for j in range(i+1, len(self.client.storage[splited[0]])):
                    if self.client.storage[splited[0]][i] == self.client.storage[splited[0]][j]:
                        self.client.storage[splited[0]].remove(self.client.storage[splited[0]][j])

        return 'ok\n\n'  # сообщение о правильном запросе клиента


class ClientServerProtocol(asyncio.Protocol):
    """asyncio TCP ECHO SERVER, см. документацию asyncio"""

    storage = {}  # Хранилище метрик


    def connection_made(self, transport):
        """см. документацию asyncio"""

        self.transport = transport

    def data_received(self, data):
        """см документацию asyncio"""

        self.data = data
        data_decoded = self.data.decode()  # декодирует полученные данные

        self.worker = Worker(client = self, data = data_decoded)  # для каждого запроса, создаёт "Класс работника
        # см. class Worker

        # обработка запросов и выполнение их
        if data_decoded == 'get *\n' in data_decoded:
            resp = self.worker.get_all()
        elif data_decoded.startswith('get') and '*' not in data_decoded:
            resp = self.worker.get()
        elif data_decoded.startswith('put') and '*' not in data_decoded:
            resp = self.worker.put()
        else:  # при невалидном запросе
            resp = self.worker.validation_error()

        self.transport.write(resp.encode())  # отправка ответа клиенту

def run_server(host, port):
    """см. документацию asyncio"""
    
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
