"""REST API views for the survey application."""
from __future__ import annotations

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from survey.models import PersonalityItem, SurveyResult
from survey.services import create_survey_result

from .serializers import (
    PersonalityItemSerializer,
    SurveyScoreRequestSerializer,
    serialize_result_payload,
)


class PersonalityItemListView(generics.ListAPIView):
    """Return all registered personality items in display order."""

    queryset = PersonalityItem.objects.order_by("order")
    serializer_class = PersonalityItemSerializer
    permission_classes = [permissions.AllowAny]


class SurveyScoreView(APIView):
    """Score survey responses and persist the result."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        items = list(PersonalityItem.objects.order_by("order"))
        serializer = SurveyScoreRequestSerializer(
            data=request.data,
            context={"items": items},
        )
        serializer.is_valid(raise_exception=True)

        result = create_survey_result(items, serializer.validated_data["responses"])
        payload = serialize_result_payload(result)
        return Response(payload, status=status.HTTP_201_CREATED)


class SurveyResultDetailView(APIView):
    """Return a previously computed survey result."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk: str, *args, **kwargs):
        result = generics.get_object_or_404(SurveyResult, pk=pk)
        payload = serialize_result_payload(result)
        return Response(payload, status=status.HTTP_200_OK)
