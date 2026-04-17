from rest_framework import serializers

from .models import AuditLog, Report


class ReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source="reporter.username", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "reporter",
            "reporter_name",
            "campaign",
            "reason",
            "details",
            "status",
            "created_at",
            "resolved_at",
        ]
        read_only_fields = ["reporter", "resolved_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "actor", "actor_name", "action", "target_model", "target_id", "metadata", "created_at"]