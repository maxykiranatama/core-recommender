from django.conf import settings
# Create your views here.
from rest_framework.views import APIView

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from .client import perform_search
from.models import Convo, Snippet
from .serializers import ConvoSerializer


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                'q',
                OpenApiTypes.STR,
                description='Query Suggestion'
            ),
            OpenApiParameter(
                'is_initiate',
                OpenApiTypes.BOOL,
                description='Is initiate convo?'
            ),
            OpenApiParameter(
                'convo_id',
                OpenApiTypes.STR,
                description='convo ID'
            )
        ]
    )
)


class SearchListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _create_default_snippet(self):
        new_convo = Convo.objects.create(
            user=self.request.user
        )
        data = [
            {
                "snippet_type": "FRAMING",
                "text": settings.TRUNCATED_FRAMING,
                "is_initiate": True,
                "convo": new_convo
            },
            {
                "snippet_type": "ASSISTANT MESSAGE",
                "text": settings.GREETING,
                "is_initiate": True,
                "convo": new_convo
            }
        ]
        for snippet in data:
            Snippet.objects.create(**snippet)
        return new_convo

    def get(self, request, *args, **kwargs):
        user = self.request.user
        query = request.GET.get('q')
        is_initiate = request.GET.get('is_initiate', False)
        convo_id = request.GET.get('convo_id', "")
        if not query:
            if is_initiate == "true":
                new_convo = self._create_default_snippet()
                serializer = ConvoSerializer(new_convo)
                return Response(serializer.data, status=200)
        if convo_id:
            convo_existing = Convo.objects.filter(user=user, convo_id=convo_id).latest("created_date")
            convo = perform_search(query, convo_existing)
            serializer = ConvoSerializer(convo)
            return Response(serializer.data)
        convo_existing = Convo.objects.filter(user=user).latest("created_date")
        convo = perform_search(query, convo_existing)
        serializer = ConvoSerializer(convo)
        return Response(serializer.data)