import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas import TeamCreate, TeamUpdate, AddTeamMember, RemoveTeamMember
from app.models.team import Team
from app.models.user import User
from app.services import create_team, get_team, get_team_by_owned_by, update_team, delete_team, add_member_to_team, remove_member_from_team


class TestTeamService(unittest.TestCase):

    def setUp(self):
        # Mock the database session
        self.db = MagicMock(spec=Session)

        # Mock a user and a team
        self.mock_user_id = uuid4()
        self.mock_team_id = uuid4()
        self.mock_user = User(id=self.mock_user_id, email="test@example.com")
        self.mock_team = Team(id=self.mock_team_id, name="Test Team",
                              owner_id=self.mock_user_id, members=[self.mock_user])

        # Set up the db queries to return the mocked data
        self.db.query.return_value.filter.return_value.first.side_effect = lambda *args: self.mock_team if self.mock_team.id == self.mock_team_id else None
        self.db.query.return_value.filter.return_value.all.return_value = [
            self.mock_team]

    def test_create_team_success(self):
        team_data = TeamCreate(name="Test Team", owner_id=self.mock_user_id)

        # Mock no existing team with the same name
        self.db.query.return_value.filter.return_value.first.side_effect = [
            None, self.mock_user]

        with patch("app.services.create_team", return_value=self.mock_team):
            team = create_team(self.db, team_data)

        self.db.add.assert_called()
        self.db.commit.assert_called()
        self.db.refresh.assert_called()

        # Check if team has some properties
        assert team is not None
        assert team.name == team_data.name

    def test_create_team_already_exists(self):
        team_data = TeamCreate(name="Test Team", owner_id=self.mock_user_id)

        # Mock an existing team with the same name
        self.db.query.return_value.filter.return_value.first.return_value = self.mock_team

        with self.assertRaises(HTTPException) as context:
            create_team(self.db, team_data)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Team already exists")

    def test_get_team_success(self):
        team = get_team(self.db, self.mock_team_id)
        self.assertEqual(team.id, self.mock_team_id)

    def test_get_team_not_found(self):
        # Mock no team found
        self.db.query.return_value.filter.return_value.first.side_effect = lambda *args: None

        with self.assertRaises(HTTPException) as context:
            get_team(self.db, uuid4())

        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "Team not found")

    def test_update_team_success(self):
        team_data = TeamUpdate(name="Updated Team")
        updated_team = update_team(
            self.db, self.mock_team_id, self.mock_user_id, team_data)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(updated_team)
        self.assertEqual(updated_team.name, "Updated Team")

    def test_update_team_not_owner(self):
        team_data = TeamUpdate(name="Updated Team")

        with self.assertRaises(HTTPException) as context:
            update_team(self.db, self.mock_team_id, uuid4(), team_data)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail,
                         "You are not the owner of this team")

    def test_delete_team_success(self):
        response = delete_team(self.db, self.mock_user_id, self.mock_team_id)
        self.db.delete.assert_called_once_with(self.mock_team)
        self.db.commit.assert_called_once()
        self.assertEqual(response, {"message": "Team deleted successfully"})

    def test_delete_team_not_owner(self):
        with self.assertRaises(HTTPException) as context:
            delete_team(self.db, uuid4(), self.mock_team_id)

        self.assertEqual(context.exception.status_code, 403)
        self.assertEqual(context.exception.detail,
                         "You are not the owner of this team")

    def test_add_member_to_team_success(self):
        new_user_id = uuid4()
        new_user = User(id=new_user_id, email="newuser@example.com")

        # Mock returning the new user
        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team, new_user]

        add_team_member = AddTeamMember(
            team_id=self.mock_team_id, user_to_add_id=new_user_id)
        updated_team = add_member_to_team(
            self.db, self.mock_user_id, add_team_member)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(updated_team)
        self.assertIn(new_user, updated_team.members)

    def test_remove_member_from_team_success(self):
        # Add a new member who is not the owner
        new_user_id = uuid4()
        new_user = User(id=new_user_id, email="newuser@example.com")

        # Ensure the team has this new member and the owner is different
        self.mock_team.members.append(new_user)
        self.db.query.return_value.filter.return_value.first.side_effect = [
            self.mock_team, new_user]

        remove_member = RemoveTeamMember(
            team_id=self.mock_team_id, user_to_remove_id=new_user_id)
        updated_team = remove_member_from_team(
            self.db, self.mock_user_id, remove_member)

        # Verify that the new user was removed and the owner remains
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(updated_team)
        self.assertNotIn(new_user, updated_team.members)
        self.assertIn(self.mock_user, updated_team.members)

    def test_remove_owner_from_team(self):
        remove_member = RemoveTeamMember(
            team_id=self.mock_team_id, user_to_remove_id=self.mock_user_id)

        with self.assertRaises(HTTPException) as context:
            remove_member_from_team(self.db, self.mock_user_id, remove_member)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail,
                         "You cannot remove the owner of the team")


if __name__ == '__main__':
    unittest.main()
