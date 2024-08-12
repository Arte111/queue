import copy
import queue

from multiprocessing import queues
class Queue:
    name: str
    isAvailable: bool

    def __init__(self, name):
        self.q = queue.Queue()
        self.isAvailable = True
        self.name = name

    def put(self, user_id: int) -> None:
        if self.isAvailable:
            self.q.put(user_id)

    def get(self) -> int:
        return self.q.get()

    def remove(self, user_id: int) -> None:
        # костыльно. создаём новую очередь, удаляя user_id,
        # тк Queue не реализует удаление элемента по индексу или значению
        temp = queue.Queue()
        while not self.q.empty():
            remove_id = self.q.get()
            if remove_id != user_id:
                temp.put(remove_id)
        self.q = temp


class User:
    user_id: int
    user_admin_queues: list[int]  # IDs where user admin
    user_queues: list[int]  # IDs where user normies

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user_admin_queues = []
        self.user_queues = []

    def __str__(self):
        return f"{self.user_id}"


class DataBase:
    users: list[User]

    def __init__(self):
        self.queues = dict()
        self.users = []

    def is_user_exist(self, user_id) -> bool:
        return any(user.user_id == user_id for user in self.users)

    def create_user(self, user_id):
        self.users.append(User(user_id))

    def create_queue(self, user_id, name) -> int:
        q_id = self.__first_empty_q_id()
        self.queues[q_id] = Queue(name)
        user = next((element for element in self.users if element.user_id == user_id), None)
        user.user_admin_queues.append(q_id)
        return q_id

    def join_user_to_queue(self, user_id, queue_id):
        self.queues[queue_id].put(user_id)
        user = next((element for element in self.users if element.user_id == user_id), None)
        user.user_queues.append(queue_id)

    def separate_queue(self, user_id, queue_id):
        self.queues[queue_id].remove(user_id)
        user = next((element for element in self.users if element.user_id == user_id), None)
        user.user_queues.remove(queue_id)

    def user_queues(self, user_id) -> list[int]:
        user = next((element for element in self.users if element.user_id == user_id), None)
        return user.user_queues

    def admin_queues(self, user_id) -> list[int]:
        user = next((element for element in self.users if element.user_id == user_id), None)
        return user.user_admin_queues

    def get_user_from_queue(self, queue_id) -> int:
        id = self.queues[queue_id].get()
        self.users[[u.user_id for u in self.users].index(id)].user_queues.remove(queue_id)
        return id

    def queue_name(self, queue_id):
        return self.queues[queue_id].name

    def remove_queue(self, user_id, queue_id):
        # TODO: получение user_id из db для этого нужен owner для очереди
        user = next((element for element in self.users if element.user_id == user_id), None)
        user.user_admin_queues.remove(queue_id)
        # TODO: удаление у каждого пользователя id очереди из списка ожидания
        self.queues.pop(queue_id)

    def place_in_queue(self, user_id, queue_id) -> int:
        # TODO: дописать получение места в очереди
        return 0

    def user_count(self, queue_id) -> int:
        return 0

    def __first_empty_q_id(self) -> int:
        keys = set(self.queues.keys())
        for i in range(len(keys)):
            if i not in keys:
                return i
        return len(keys)


if __name__ == "__main__":
    db = DataBase()

    db.create_user(234)
    db.create_user(542)
    db.create_user(462)

    qid = db.create_queue(234, "nothing")

    db.join_user_to_queue(542, qid)
    db.join_user_to_queue(462, qid)

    db.separate_queue(542, qid)
    print(db.user_queues(542))

    print(db.admin_queues(234))
    db.remove_queue(234, qid)
    print(db.admin_queues(234))
