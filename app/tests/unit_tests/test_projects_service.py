import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from app.services import (
    create_project,
    get_project,
    get_user_projects,
    update_project,
    delete_project,
)
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models import Project, User


class TestProjectService(unittest.TestCase):

    def setUp(self):
        # Mock the database session
        self.db = MagicMock(spec=Session)
        # Mock a user object
        self.user = User(id=uuid4(), email="test@example.com")
        # Mock project data
        self.project_data = ProjectCreate(
            name="Test Project", description="A test project"
        )
        self.updated_project_data = ProjectUpdate(
            name="Updated Project", description="Updated description"
        )
        # Mock project
        self.project = Project(
            id=uuid4(),
            name="Test Project",
            description="A test project",
            owner_id=self.user.id,
        )

    def test_create_project(self):
        # Set up mocks for the database
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        self.db.query.return_value.filter.return_value.first.return_value = None

        created_project = create_project(self.db, self.user, self.project_data)

        # Assertions
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        assert created_project.name == self.project_data.name
        assert created_project.description == self.project_data.description
        assert created_project.owner_id == self.user.id

    def test_get_project_success(self):
        # Mock a successful query response
        self.db.query.return_value.filter.return_value.first.return_value = self.project

        with patch("app.services.get_project", return_value=self.project):
            found_project = get_project(self.db, self.project.id, self.user)
        self.assertEqual(found_project, self.project)

    def test_get_project_not_found(self):
        # Mock a failed query response
        self.db.query.return_value.filter.return_value.first.return_value = None

        with patch("app.services.get_project", return_value=self.project):
            with self.assertRaises(HTTPException) as context:
                get_project(self.db, uuid4(), self.user)

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Project not found")

    def test_get_user_projects(self):
        self.db.query().filter().offset().limit().all.return_value = [self.project]

        projects = get_user_projects(self.db, self.user)
        print(projects)

        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0], self.project)

    def test_update_project_success(self):
        # Mock successful retrieval and update
        self.db.query.return_value.filter.return_value.first.return_value = self.project
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

        updated_project = update_project(
            self.db, self.project.id, self.user, self.updated_project_data
        )

        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(updated_project.name, self.updated_project_data.name)
        self.assertEqual(
            updated_project.description, self.updated_project_data.description
        )

    def test_delete_project_success(self):
        # Mock successful retrieval and deletion
        self.db.query.return_value.filter.return_value.first.return_value = self.project
        self.db.delete = MagicMock()
        self.db.commit = MagicMock()

        response = delete_project(self.db, self.project.id, self.user)

        self.db.delete.assert_called_once_with(self.project)
        self.db.commit.assert_called_once()
        self.assertEqual(response, {"message": "Project deleted successfully"})
