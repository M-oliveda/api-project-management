import unittest
from unittest.mock import MagicMock
from uuid import uuid4
from app.schemas.task import TaskCreate, TaskUpdate, TaskStatus
from app.models import Task
from app.services import (
    create_task,
    update_task,
    delete_task,
    get_task_by_id,
    get_tasks,
    get_tasks_by_project,
)


class TestTaskService(unittest.TestCase):
    def setUp(self):
        # Set up mock data
        self.mock_db = MagicMock()
        self.mock_task_id = uuid4()
        self.mock_project_id = uuid4()

        self.task_data_create = TaskCreate(
            title="Test Task",
            description="Test Description",
            project_id=self.mock_project_id,
        )

        self.task_data_update = TaskUpdate(
            title="Updated Task",
            description="Updated Description",
            status=TaskStatus.IN_PROGRESS,
        )

        self.mock_task = MagicMock(
            id=self.mock_task_id,
            title="Test Task",
            description="Test Description",
            status="Pending",
            project_id=self.mock_project_id,
        )

        self.mock_user = MagicMock(id=uuid4(), email="test@example.com")

        self.mock_project = MagicMock(
            id=self.mock_project_id, owner_id=self.mock_user.id
        )

    def test_create_task(self):
        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.refresh = MagicMock()

        result = create_task(self.mock_db, self.task_data_create)

        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(result)
        self.assertEqual(result.title, self.task_data_create.title)
        self.assertEqual(result.project_id, self.task_data_create.project_id)

    def test_update_task(self):
        self.mock_db.query().filter().first.return_value = self.mock_task

        result = update_task(self.mock_db, self.mock_task_id, self.task_data_update)

        self.assertIsNotNone(result)
        self.assertEqual(result.title, self.task_data_update.title)
        self.assertEqual(result.description, self.task_data_update.description)
        self.assertEqual(result.status, self.task_data_update.status)
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(result)

    def test_update_task_not_found(self):
        self.mock_db.query().filter().first.return_value = None

        result = update_task(self.mock_db, self.mock_task_id, self.task_data_update)

        self.assertIsNone(result)
        self.mock_db.commit.assert_not_called()

    def test_delete_task(self):
        self.mock_db.query().filter().first.return_value = self.mock_task

        result = delete_task(self.mock_db, self.mock_task_id)

        self.mock_db.delete.assert_called_once_with(self.mock_task)
        self.mock_db.commit.assert_called_once()
        self.assertEqual(result, self.mock_task)

    def test_delete_task_not_found(self):
        self.mock_db.query().filter().first.return_value = None

        result = delete_task(self.mock_db, self.mock_task_id)

        self.assertIsNone(result)
        self.mock_db.delete.assert_not_called()
        self.mock_db.commit.assert_not_called()

    def test_get_task_by_id(self):
        self.mock_db.query().filter().first.return_value = self.mock_task

        result = get_task_by_id(self.mock_db, self.mock_task_id)

        self.assertEqual(result, self.mock_task)
        self.mock_db.query().filter().first.assert_called_once()

    def test_get_tasks(self):
        # Mock the first query for the user
        self.mock_db.query().filter().first.return_value = self.mock_user

        # Mock the second query for the projects owned by the user
        self.mock_db.query().filter().all.return_value = [self.mock_project]

        # Mock the third query for the tasks associated with the projects
        self.mock_db.query().filter().all.return_value = [self.mock_task]

        result = get_tasks(self.mock_db, "test@example.com")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_task)
        self.mock_db.query().filter().all.assert_called()

    def test_get_tasks_by_project(self):
        self.mock_db.query().filter().all.return_value = [self.mock_task]

        result = get_tasks_by_project(
            self.mock_db, self.mock_project_id, "test@example.com"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.mock_task)
