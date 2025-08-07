from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
from django.shortcuts import get_object_or_404
# from rest_framework.authentication import BasicAuthentication
from .models import *
from .serializers import *
from .services.ai_gateway import call_ai_agent

import os

User = get_user_model()

# ==================== Root Agent View ====================
class RootAgentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        query = request.data.get("query")
        file = request.FILES.get("file")
        user = request.user

        file_path = None
        if file:
            os.makedirs('temp', exist_ok=True)
            file_path = f"temp/{file.name}"
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

        result = call_ai_agent("root", query, file_path)

        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return Response(result)


# ==================== Individual Agent View ====================
def save_uploaded_file(uploaded_file, folder="temp"):
    if uploaded_file:
        os.makedirs(folder, exist_ok=True)
        saved_path = os.path.join(folder, uploaded_file.name)
        with open(saved_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        return saved_path
    return None


class AgentAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, agent_name):
        query = request.data.get("query")
        file = request.FILES.get("file")
        print("query :", query)
        print("file :", file)
        csv_file = request.FILES.get("csv")
        agent_name = agent_name or request.data.get("agent_name")
        user = request.user

        file_path = save_uploaded_file(file)
        csv_file_path = save_uploaded_file(csv_file)

        result = call_ai_agent(agent_name, query, file_path, csv_file=csv_file_path)

        # Clean up files after processing
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if csv_file_path and os.path.exists(csv_file_path):
            os.remove(csv_file_path)

        return Response({
            "response": result,
            "used_agent": agent_name
        })

# ==================== CRUD ViewSets ====================
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AgentViewSet(ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAuthenticated]


class AgentIntegrationViewSet(ModelViewSet):
    queryset = AgentIntegration.objects.all()
    serializer_class = AgentIntegrationSerializer
    permission_classes = [IsAuthenticated]


class ConversationViewSet(ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ChatMessageViewSet(ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(conversation__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class TokenLogViewSet(ModelViewSet):
    queryset = TokenLog.objects.all()
    serializer_class = TokenLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TokenLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RootAgentMemoryViewSet(ModelViewSet):
    queryset = RootAgentMemory.objects.all()
    serializer_class = RootAgentMemorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RootAgentMemory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class APIKeyViewSet(ModelViewSet):
    queryset = APIKey.objects.all()
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AgentFeedbackViewSet(ModelViewSet):
    queryset = AgentFeedback.objects.all()
    serializer_class = AgentFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AgentFeedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicAgentListView(ListAPIView):
    queryset = Agent.objects.filter(is_featured=True).order_by('display_order')
    serializer_class = AgentSerializer
    permission_classes = [AllowAny]


class PublicAgentDetailView(RetrieveAPIView):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # or use 'name' if URLs use names

# ==================== Auth: SignUp, Login, Logout ====================
from rest_framework.response import Response
from rest_framework import status

class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Account created successfully!"}, status=status.HTTP_201_CREATED)



class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Get tokens from serializer
        data = serializer.validated_data
        return Response({
            "message": "Login successful!",
            "access": data["access"],
            "refresh": data["refresh"]
        }, status=status.HTTP_200_OK)




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=205)
        except Exception as e:
            return Response({"error": str(e)}, status=400)




class IntegrationSnippetAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, agent_name):
        user = request.user

        # Get agent
        agent = get_object_or_404(Agent, name=agent_name)

        # Get API key
        api_key = APIKey.objects.filter(user=user, agent=agent).first()
        if not api_key:
            return Response({"error": "API key not found for this agent."}, status=403)

        # Get agent integration info
        integration = AgentIntegration.objects.filter(agent=agent).first()
        if not integration:
            return Response({"error": "Integration details not found."}, status=404)

        # Generate code snippet safely
        snippet = f"""import requests

url = "{integration.url}"
headers = {{
    "Authorization": "Bearer {api_key.key}",
    "Content-Type": "application/json"
}}
data = {integration.body}

response = requests.{integration.method.lower()}(url, headers=headers, json=data)

print(response.status_code)
print(response.json())
"""

        return Response({
            "agent": agent.name,
            "description": agent.description,
            "integration_snippet": snippet
        }, status=200)
    