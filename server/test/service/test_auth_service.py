"""
Comprehensive tests for auth_service.py

This module contains unit tests for all authentication service functions including:
- create_user: User registration with validation
- authenticate_user: User authentication with credentials
- login_user: User login with token generation
- logout_user: User logout with token blacklisting

All external dependencies are mocked for isolated testing.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add server directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from fastapi import HTTPException
from sqlalchemy.orm import Session
from service.auth_service import create_user, authenticate_user, login_user, logout_user
from schemas.user_schema import UserCreate
from model.model import User


class TestAuthService(unittest.TestCase):
    """Test suite for authentication service functions"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Mock database session
        self.mock_db = Mock(spec=Session)
        
        # Mock user data
        self.test_user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "phone": "+1234567890"
        }
        
        # Mock user create schema
        self.mock_user_create = UserCreate(**self.test_user_data)
        
        # Mock database user object
        self.mock_db_user = User(
            id=1,
            email=self.test_user_data["email"],
            username=self.test_user_data["username"],
            hashed_password="hashed_password_123",
            phone=self.test_user_data["phone"]
        )
        
        # Mock token
        self.mock_token = "mock_jwt_token_12345"
        
    def tearDown(self):
        """Clean up after each test method"""
        # Reset all mocks
        self.mock_db.reset_mock()
        
    # ==================== CREATE USER TESTS ====================
    
    @patch('service.auth_service.get_password_hash')
    def test_create_user_success(self, mock_get_password_hash):
        """Test successful user creation"""
        # Arrange
        mock_get_password_hash.return_value = "hashed_password_123"
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # Act
        result = create_user(self.mock_db, self.mock_user_create)
        
        # Assert
        mock_get_password_hash.assert_called_once_with(self.test_user_data["password"])
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
        self.assertIsInstance(result, User)
        self.assertEqual(result.email, self.test_user_data["email"])
        
    def test_create_user_email_already_exists(self):
        """Test user creation with existing email"""
        # Arrange
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_db_user
        
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            create_user(self.mock_db, self.mock_user_create)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Email already registered")
        
    @patch('service.auth_service.get_password_hash')
    def test_create_user_database_error(self, mock_get_password_hash):
        """Test user creation with database error"""
        # Arrange
        mock_get_password_hash.return_value = "hashed_password_123"
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        self.mock_db.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            create_user(self.mock_db, self.mock_user_create)
            
    # ==================== AUTHENTICATE USER TESTS ====================
    
    @patch('service.auth_service.verify_password')
    def test_authenticate_user_success(self, mock_verify_password):
        """Test successful user authentication"""
        # Arrange
        mock_verify_password.return_value = True
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_db_user
        
        # Act
        result = authenticate_user(self.mock_db, self.test_user_data["email"], self.test_user_data["password"])
        
        # Assert
        mock_verify_password.assert_called_once_with(self.test_user_data["password"], "hashed_password_123")
        self.assertEqual(result, self.mock_db_user)
        
    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user"""
        # Arrange
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = authenticate_user(self.mock_db, "nonexistent@example.com", "password")
        
        # Assert
        self.assertFalse(result)
        
    @patch('service.auth_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify_password):
        """Test authentication with wrong password"""
        # Arrange
        mock_verify_password.return_value = False
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.mock_db_user
        
        # Act
        result = authenticate_user(self.mock_db, self.test_user_data["email"], "wrong_password")
        
        # Assert
        mock_verify_password.assert_called_once_with("wrong_password", "hashed_password_123")
        self.assertFalse(result)
        
    # ==================== LOGIN USER TESTS ====================
    
    @patch('service.auth_service.create_access_token')
    @patch('service.auth_service.authenticate_user')
    def test_login_user_success(self, mock_authenticate_user, mock_create_access_token):
        """Test successful user login"""
        # Arrange
        mock_authenticate_user.return_value = self.mock_db_user
        mock_create_access_token.return_value = self.mock_token
        
        # Act
        result = login_user(self.mock_db, self.test_user_data["email"], self.test_user_data["password"])
        
        # Assert
        mock_authenticate_user.assert_called_once_with(self.mock_db, self.test_user_data["email"], self.test_user_data["password"])
        mock_create_access_token.assert_called_once_with(data={"sub": self.test_user_data["email"]})
        self.assertEqual(result["access_token"], self.mock_token)
        self.assertEqual(result["token_type"], "bearer")
        
    @patch('service.auth_service.authenticate_user')
    def test_login_user_invalid_credentials(self, mock_authenticate_user):
        """Test login with invalid credentials"""
        # Arrange
        mock_authenticate_user.return_value = False
        
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            login_user(self.mock_db, "invalid@example.com", "wrong_password")
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, "Invalid email or password")
        
    @patch('service.auth_service.create_access_token')
    @patch('service.auth_service.authenticate_user')
    def test_login_user_token_creation_error(self, mock_authenticate_user, mock_create_access_token):
        """Test login with token creation error"""
        # Arrange
        mock_authenticate_user.return_value = self.mock_db_user
        mock_create_access_token.side_effect = Exception("Token creation failed")
        
        # Act & Assert
        with self.assertRaises(Exception):
            login_user(self.mock_db, self.test_user_data["email"], self.test_user_data["password"])
            
    # ==================== LOGOUT USER TESTS ====================
    
    @patch('service.auth_service.blacklist_token')
    def test_logout_user_success(self, mock_blacklist_token):
        """Test successful user logout"""
        # Arrange
        mock_blacklist_token.return_value = None
        
        # Act
        result = logout_user(self.mock_db, self.mock_token)
        
        # Assert
        mock_blacklist_token.assert_called_once_with(self.mock_db, self.mock_token)
        self.assertEqual(result["message"], "Successfully logged out")
        
    @patch('service.auth_service.blacklist_token')
    def test_logout_user_blacklist_error(self, mock_blacklist_token):
        """Test logout with blacklist error"""
        # Arrange
        mock_blacklist_token.side_effect = Exception("Blacklist failed")
        
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            logout_user(self.mock_db, self.mock_token)
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Logout failed")
        
    def test_logout_user_empty_token(self):
        """Test logout with empty token"""
        # Act & Assert
        with self.assertRaises(HTTPException) as context:
            logout_user(self.mock_db, "")
        
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Logout failed")
        
    # ==================== INTEGRATION TESTS ====================
    
    @patch('service.auth_service.get_password_hash')
    @patch('service.auth_service.verify_password')
    @patch('service.auth_service.create_access_token')
    @patch('service.auth_service.blacklist_token')
    def test_full_user_lifecycle(self, mock_blacklist_token, mock_create_access_token, 
                                mock_verify_password, mock_get_password_hash):
        """Test complete user lifecycle: create -> login -> logout"""
        # Arrange
        mock_get_password_hash.return_value = "hashed_password_123"
        mock_verify_password.return_value = True
        mock_create_access_token.return_value = self.mock_token
        mock_blacklist_token.return_value = None
        
        # Setup database mocks for user creation
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [None, self.mock_db_user]
        self.mock_db.add = Mock()
        self.mock_db.commit = Mock()
        self.mock_db.refresh = Mock()
        
        # Act - Create user
        created_user = create_user(self.mock_db, self.mock_user_create)
        
        # Act - Login user
        login_result = login_user(self.mock_db, self.test_user_data["email"], self.test_user_data["password"])
        
        # Act - Logout user
        logout_result = logout_user(self.mock_db, login_result["access_token"])
        
        # Assert
        self.assertIsInstance(created_user, User)
        self.assertEqual(login_result["access_token"], self.mock_token)
        self.assertEqual(login_result["token_type"], "bearer")
        self.assertEqual(logout_result["message"], "Successfully logged out")
        
    # ==================== EDGE CASES ====================
    
    def test_create_user_with_special_characters(self):
        """Test user creation with special characters in data"""
        # Arrange
        special_user_data = {
            "email": "test+special@example.com",
            "username": "test_user-123",
            "password": "P@ssw0rd!@#$%",
            "phone": "+1-234-567-8900"
        }
        special_user_create = UserCreate(**special_user_data)
        
        with patch('service.auth_service.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_special_password"
            self.mock_db.query.return_value.filter.return_value.first.return_value = None
            self.mock_db.add = Mock()
            self.mock_db.commit = Mock()
            self.mock_db.refresh = Mock()
            
            # Act
            result = create_user(self.mock_db, special_user_create)
            
            # Assert
            self.assertIsInstance(result, User)
            mock_hash.assert_called_once_with(special_user_data["password"])
            
    def test_authenticate_user_case_sensitivity(self):
        """Test authentication with case-sensitive email"""
        # Arrange
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = authenticate_user(self.mock_db, "TEST@EXAMPLE.COM", self.test_user_data["password"])
        
        # Assert
        self.assertFalse(result)


class TestAuthServiceSetupTeardown(unittest.TestCase):
    """Test class for setup and teardown functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class - runs once before all tests"""
        cls.test_database_url = "sqlite:///:memory:"
        
    @classmethod
    def tearDownClass(cls):
        """Tear down test class - runs once after all tests"""
        pass
        
    def setUp(self):
        """Set up each test - runs before each test method"""
        self.addCleanup(self.cleanup_mocks)
        
    def cleanup_mocks(self):
        """Clean up mocks after each test"""
        # Reset any global state if needed
        pass


def run_auth_service_tests():
    """Run all auth service tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_suite.addTest(unittest.makeSuite(TestAuthService))
    test_suite.addTest(unittest.makeSuite(TestAuthServiceSetupTeardown))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Run tests when script is executed directly
    success = run_auth_service_tests()
    sys.exit(0 if success else 1)
