"""
Test suite for Mergington High School Activities API using AAA (Arrange-Act-Assert) pattern.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_success(self, client):
        """Test successful retrieval of all activities."""
        # Arrange
        # (setup done by fixtures)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_get_activities_structure(self, client):
        """Test that activity objects have correct structure."""
        # Arrange
        # (setup done by fixtures)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants(self, client):
        """Test that participants list is accessible for each activity."""
        # Arrange
        # (setup done by fixtures)
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            follow_redirects=True
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to the list."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count."""
        # Arrange
        activity_name = "Tennis Club"
        email = "newtennis@mergington.edu"
        
        # Get initial count
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count + 1
    
    def test_signup_duplicate_email_fails(self, client):
        """Test that signing up with an email already in the activity fails."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
    
    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for same activity."""
        # Arrange
        activity_name = "Debate Team"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Act
        response1 = client.post(f"/activities/{activity_name}/signup?email={email1}")
        response2 = client.post(f"/activities/{activity_name}/signup?email={email2}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        activities = response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from list."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        response = client.get("/activities")
        
        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
    
    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases the participant count."""
        # Arrange
        activity_name = "Drama Club"
        email = "isabella@mergington.edu"
        
        response_before = client.get("/activities")
        initial_count = len(response_before.json()[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/unregister?email={email}")
        
        # Assert
        response_after = client.get("/activities")
        final_count = len(response_after.json()[activity_name]["participants"])
        assert final_count == initial_count - 1
    
    def test_unregister_non_participant_fails(self, client):
        """Test that unregistering a non-participant fails."""
        # Arrange
        activity_name = "Chess Club"
        email = "nonparticipant@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"].lower()
    
    def test_unregister_and_reregister(self, client):
        """Test that a participant can unregister and re-register."""
        # Arrange
        activity_name = "Tennis Club"
        email = "alex@mergington.edu"
        
        # Act - Unregister
        response1 = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert unregister worked
        assert response1.status_code == 200
        
        # Act - Re-register
        response2 = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert re-register worked
        assert response2.status_code == 200
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity_name]["participants"]


class TestIntegration:
    """Integration tests for complex scenarios."""
    
    def test_signup_and_unregister_flow(self, client):
        """Test complete flow: signup, verify, unregister, verify."""
        # Arrange
        activity_name = "Programming Class"
        email = "integration@mergington.edu"
        
        # Act - Initial state
        response = client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"].copy()
        assert email not in initial_participants
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Assert - Participant added
        response = client.get("/activities")
        after_signup = response.json()[activity_name]["participants"]
        assert email in after_signup
        assert len(after_signup) == len(initial_participants) + 1
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Assert - Participant removed
        response = client.get("/activities")
        after_unregister = response.json()[activity_name]["participants"]
        assert email not in after_unregister
        assert len(after_unregister) == len(initial_participants)
    
    def test_multiple_operations_isolation(self, client):
        """Test that multiple operations don't interfere with each other."""
        # Arrange
        activity1 = "Art Studio"
        activity2 = "Science Club"
        email1 = "artist@mergington.edu"
        email2 = "scientist@mergington.edu"
        
        # Act - Sign up for both activities
        client.post(f"/activities/{activity1}/signup?email={email1}")
        client.post(f"/activities/{activity2}/signup?email={email2}")
        
        # Assert - Both signups worked independently
        response = client.get("/activities")
        activities = response.json()
        assert email1 in activities[activity1]["participants"]
        assert email2 in activities[activity2]["participants"]
        assert email1 not in activities[activity2]["participants"]
        assert email2 not in activities[activity1]["participants"]
