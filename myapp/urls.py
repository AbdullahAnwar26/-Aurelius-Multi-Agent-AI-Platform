from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

# 🚀 CRUD API Router for Models
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'agents', AgentViewSet)
router.register(r'agent-integrations', AgentIntegrationViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'chat-messages', ChatMessageViewSet)
router.register(r'token-logs', TokenLogViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'root-memories', RootAgentMemoryViewSet)
router.register(r'api-keys', APIKeyViewSet)
router.register(r'agent-feedbacks', AgentFeedbackViewSet)

urlpatterns = [
    # 🔁 Agent APIs
    path('api/root-agent/', RootAgentAPIView.as_view(), name='root_agent'),
    path('api/agent/<str:agent_name>/', AgentAPIView.as_view(), name='agent_api'),

    # 🔐 Auth APIs
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/login/', CustomLoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🧱 Model CRUD endpoints
    path('api/', include(router.urls)),
    path('api/integration-snippet/<str:agent_name>/', IntegrationSnippetAPIView.as_view(), name='integration_snippet'),
]

