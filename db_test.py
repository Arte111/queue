import unittest

from db import DataBase, User, Queue


class TestQueue(unittest.TestCase):

    def test_queue_put_get(self):
        q = Queue("TestQueue")
        q.put(1)
        result = q.get()
        self.assertEqual(result, 1)

    def test_queue_remove(self):
        q = Queue("TestQueue")
        q.put(1)
        q.put(2)
        q.put(3)
        q.remove(2)
        result = [q.get(), q.get()]
        self.assertEqual(result, [1, 3])


class TestUser(unittest.TestCase):

    def test_user_creation(self):
        user = User(123)
        self.assertEqual(user.user_id, 123)
        self.assertEqual(user.user_admin_queues, [])
        self.assertEqual(user.user_queues, [])

    def test_user_str(self):
        user = User(123)
        self.assertEqual(str(user), "123")


class TestDataBase(unittest.TestCase):

    def setUp(self):
        self.db = DataBase()
        self.db.create_user(1)
        self.db.create_user(2)
        self.db.create_user(3)
        self.qid = self.db.create_queue(1, "TestQueue")

    def test_create_user(self):
        self.assertTrue(self.db.is_user_exist(1))
        self.assertTrue(self.db.is_user_exist(2))
        self.assertTrue(self.db.is_user_exist(3))
        self.assertFalse(self.db.is_user_exist(999))

    def test_create_queue(self):
        self.assertEqual(self.db.queue_name(self.qid), "TestQueue")
        self.assertIn(self.qid, self.db.admin_queues(1))

    def test_join_user_to_queue(self):
        self.db.join_user_to_queue(2, self.qid)
        self.assertIn(self.qid, self.db.user_queues(2))

    def test_separate_queue(self):
        self.db.join_user_to_queue(2, self.qid)
        self.db.separate_queue(2, self.qid)
        self.assertNotIn(self.qid, self.db.user_queues(2))

    def test_remove_queue(self):
        self.db.remove_queue(1, self.qid)
        self.assertNotIn(self.qid, self.db.admin_queues(1))
        self.assertNotIn(self.qid, self.db.queues)

    def test_get_user_from_queue(self):
        self.db.join_user_to_queue(2, self.qid)
        user_id = self.db.get_user_from_queue(self.qid)
        self.assertEqual(user_id, 2)
        self.assertNotIn(self.qid, self.db.user_queues(2))

    def test_first_empty_q_id(self):
        self.assertEqual(self.db._DataBase__first_empty_q_id(), 1)
        qid2 = self.db.create_queue(1, "SecondQueue")
        self.assertEqual(self.db._DataBase__first_empty_q_id(), 2)
        self.db.remove_queue(1, self.qid)
        self.assertEqual(self.db._DataBase__first_empty_q_id(), 0)


if __name__ == '__main__':
    unittest.main()
