"""
Integration tests for authentication API endpoints.
"""

import pytest
from httpx import AsyncClient

from backend.db_models import UserDB


@pytest.mark.api
@pytest.mark.auth
@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    async def test_register_new_user(self, client: AsyncClient):
        """Should successfully register a new user."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePass123!",
                "full_name": "New User",
                "role": "viewer"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "hashed_password" not in data  # Password should not be returned
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: UserDB):
        """Should reject duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,  # Duplicate
                "password": "SecurePass123!",
                "role": "viewer"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_login_success(self, client: AsyncClient, test_user: UserDB):
        """Should successfully login with correct credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user: UserDB):
        """Should reject login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Should reject login for non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: UserDB):
        """Should return current user info with valid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Should reject request without authentication token."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No Authorization header
    
    async def test_refresh_token(self, client: AsyncClient, test_user: UserDB):
        """Should issue new tokens with valid refresh token."""
        # First login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new tokens
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
