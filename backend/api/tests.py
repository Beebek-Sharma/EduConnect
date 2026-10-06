from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .authentication import JWTCookieAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
import datetime
import uuid
import json

User = get_user_model()

class JWTCookieAuthenticationTests(TestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		self.auth = JWTCookieAuthentication()

	def test_authenticate_with_valid_token_in_cookie(self):
		fake_user = User.objects.create_user(username='user_123', email='u@example.com')
		token = str(RefreshToken.for_user(fake_user).access_token)
		request = self.factory.get('/api/me/')
		request.COOKIES['access_token'] = token
		user, returned_token = self.auth.authenticate(request)
		self.assertEqual(user.username, 'user_123')

	def test_authenticate_with_valid_token_in_header(self):
		fake_user = User.objects.create_user(username='user_456', email='u456@example.com')
		token = str(RefreshToken.for_user(fake_user).access_token)
		request = self.factory.get('/api/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
		user, returned_token = self.auth.authenticate(request)
		self.assertEqual(user.username, 'user_456')

	def test_authenticate_no_credentials(self):
		request = self.factory.get('/api/me/')
		result = self.auth.authenticate(request)
		self.assertIsNone(result)

class ChatAPITestCase(TestCase):
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create a test session
        self.session_id = str(uuid.uuid4())
        from .models import ChatSession, ChatMessage
        self.session = ChatSession.objects.create(session_id=self.session_id)
        
        # Add some test messages
        ChatMessage.objects.create(
            session=self.session,
            role='user',
            content='Hello, test message'
        )
        
        ChatMessage.objects.create(
            session=self.session,
            role='assistant',
            content='Hello! How can I help you today?'
        )
    
    @patch('api.views_chat.grok_client')
    def test_chat_message_valid(self, mock_grok_client):
        """Test sending a valid chat message"""
        # Mock the grok_client response
        mock_response = {
            'reply': 'This is a test response from the mock Grok client',
            'metadata': {'model': 'test-model', 'usage': {'total_tokens': 10}}
        }
        mock_grok_client.send_message.return_value = mock_response
        
        # Send a test message
        url = reverse('chat_message')
        data = {
            'message': 'Hello, this is a test',
            'session_id': self.session_id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reply'], mock_response['reply'])
        self.assertEqual(response.data['session_id'], self.session_id)
        
        # Check that the message was saved to the database
        from .models import ChatMessage
        self.assertEqual(
            ChatMessage.objects.filter(session__session_id=self.session_id).count(),
            4  # 2 initial messages + 1 user message + 1 assistant response
        )
    
    @patch('api.views_chat.grok_client')
    def test_chat_message_new_session(self, mock_grok_client):
        """Test sending a message without a session ID (creates new session)"""
        # Mock the grok_client response
        mock_response = {
            'reply': 'This is a test response for a new session',
            'metadata': {'model': 'test-model', 'usage': {'total_tokens': 10}}
        }
        mock_grok_client.send_message.return_value = mock_response
        
        # Send a test message without a session ID
        url = reverse('chat_message')
        data = {'message': 'Hello, new session'}
        
        response = self.client.post(url, data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reply'], mock_response['reply'])
        self.assertIsNotNone(response.data['session_id'])
        
        # Check that a new session was created
        from .models import ChatSession
        session_id = response.data['session_id']
        self.assertTrue(ChatSession.objects.filter(session_id=session_id).exists())
        
    def test_chat_message_empty(self):
        """Test sending an empty message (should return 400)"""
        url = reverse('chat_message')
        data = {
            'message': '',
            'session_id': self.session_id
        }
        
        response = self.client.post(url, data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_chat_history_valid(self):
        """Test retrieving valid chat history"""
        url = reverse('chat_history', args=[self.session_id])
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['session_id'], self.session_id)
        self.assertEqual(len(response.data['messages']), 2)
    
    def test_chat_history_invalid(self):
        """Test retrieving chat history with invalid session ID"""
        url = reverse('chat_history', args=['invalid-session-id'])
        response = self.client.get(url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_chat_clear(self):
        """Test clearing a chat session"""
        url = reverse('chat_clear', args=[self.session_id])
        response = self.client.delete(url)
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the messages were deleted
        from .models import ChatMessage
        self.assertEqual(
            ChatMessage.objects.filter(session__session_id=self.session_id).count(),
            0
        )
        
        # Check that the session still exists
        from .models import ChatSession
        self.assertTrue(ChatSession.objects.filter(session_id=self.session_id).exists())
    
    @patch('api.views_chat.grok_client')
    def test_chat_summary(self, mock_grok_client):
        """Test generating a chat summary"""
        # Mock the grok_client response
        mock_response = {
            'reply': 'This is a test summary of the conversation',
            'metadata': {'model': 'test-model', 'usage': {'total_tokens': 10}}
        }
        mock_grok_client.send_message.return_value = mock_response
        
        url = reverse('chat_summary')
        data = {'session_id': self.session_id}
        
        response = self.client.post(url, data, format='json')
        
        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['summary'], mock_response['reply'])
        self.assertEqual(response.data['session_id'], self.session_id)
