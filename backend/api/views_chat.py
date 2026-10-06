"""
Views for the AI chat functionality.
"""
import json
import uuid
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.response import Response
from rest_framework import status

from .models import ChatSession, ChatMessage
from .grok_client import grok_client


class ChatMessageThrottle(AnonRateThrottle):
    """Rate limiting for anonymous chat users: 20/minute"""
    rate = '20/minute'
    scope = 'chat_message'
    

class AuthenticatedChatMessageThrottle(UserRateThrottle):
    """Rate limiting for authenticated chat users: 60/minute"""
    rate = '60/minute'
    scope = 'auth_chat_message'


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_message(request):
    """
    Handle POST requests for chat messages.
    Creates or retrieves a chat session and generates a response from Grok AI.
    """
    try:
        data = request.data
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        # Validate user message
        if not user_message:
            return Response(
                {"error": "Message cannot be empty"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get or create a session
        if not session_id:
            # Generate a new unique session ID
            session_id = str(uuid.uuid4())
            session = ChatSession.objects.create(
                session_id=session_id,
                user=request.user if request.user.is_authenticated else None
            )
        else:
            try:
                session = ChatSession.objects.get(session_id=session_id)
                # Update the user if they are now authenticated
                if request.user.is_authenticated and not session.user:
                    session.user = request.user
                    session.save()
            except ObjectDoesNotExist:
                # If session ID is invalid, create a new one
                session_id = str(uuid.uuid4())
                session = ChatSession.objects.create(
                    session_id=session_id,
                    user=request.user if request.user.is_authenticated else None
                )
        
        # Store the user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Get session history for context
        history = list(session.messages.values('role', 'content'))
        
        # Send to Grok API and get response
        grok_response = grok_client.send_message(history[:-1], user_message)
        
        # Add a development mode flag if we're using fallback responses
        is_development = 'development' in grok_response.get('metadata', {}).get('model', '')
        
        # Store the assistant's reply
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=grok_response['reply']
        )
        
        # Return the response
        return Response({
            'reply': grok_response['reply'],
            'session_id': session_id,
            'development_mode': is_development,
            'metadata': grok_response.get('metadata', {})
        })
    
    except Exception as e:
        # Log the error but don't expose details
        print(f"Error in chat_message view: {str(e)}")
        return Response(
            {
                "error": "An unexpected error occurred. Please try again.",
                "session_id": session_id if 'session_id' in locals() else str(uuid.uuid4())
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def chat_history(request, session_id):
    """
    Retrieve chat history for a given session ID.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        if session.user and request.user != session.user and not getattr(request.user, 'is_staff', False):
            return Response(
                {"error": "You don't have permission to access this chat history."},
                status=status.HTTP_403_FORBIDDEN
            )
    except ObjectDoesNotExist:
        return Response(
            {"error": "Chat session not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    messages = list(session.messages.values('role', 'content', 'timestamp'))
    return Response({
        'session_id': session_id,
        'messages': messages,
        'created_at': session.created_at,
        'updated_at': session.updated_at
    })

@api_view(['DELETE'])
@permission_classes([AllowAny])
def chat_clear(request, session_id):
    """
    Clear or delete a chat session.
    """
    try:
        session = ChatSession.objects.get(session_id=session_id)
        if session.user and request.user != session.user and not getattr(request.user, 'is_staff', False):
            return Response(
                {"error": "You don't have permission to clear this chat session."},
                status=status.HTTP_403_FORBIDDEN
            )
        session.messages.all().delete()
        return Response({
            'status': 'success',
            'message': 'Chat history cleared successfully'
        })
    except ObjectDoesNotExist:
        return Response(
            {"error": "Chat session not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in chat_clear view: {str(e)}")
        return Response(
            {"error": "An error occurred clearing chat history"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_summary(request):
    """
    Generate a summary of the chat conversation.
    """
    try:
        data = request.data
        session_id = data.get('session_id')
        
        if not session_id:
            return Response(
                {"error": "Session ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        session = ChatSession.objects.get(session_id=session_id)
        
        # Only allow access if the session belongs to the user or is anonymous
        if session.user and request.user != session.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to summarize this chat"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Get session history
        history = list(session.messages.values('role', 'content'))
        
        if len(history) < 2:
            return Response(
                {"error": "Not enough messages to generate a summary"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Create a summary request
        summary_request = "Please provide a brief summary of our conversation so far."
        
        # Send to Grok API
        grok_response = grok_client.send_message(history, summary_request)
        
        return Response({
            'summary': grok_response['reply'],
            'session_id': session_id
        })
        
    except ObjectDoesNotExist:
        return Response(
            {"error": "Chat session not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in chat_summary view: {str(e)}")
        return Response(
            {"error": "An error occurred generating summary"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )