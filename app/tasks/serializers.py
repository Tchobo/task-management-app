from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from core.models import MediaFile, Task, TaskComment


class TaskCommentSerializer(serializers.ModelSerializer):
    """Task comment serializer."""

    class Meta:
        model = TaskComment
        fields = ("id", "user", "text", "task")
        read_only_fields = ("id", "user")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        task = validated_data.pop("task", None)
        return TaskComment.objects.create(task=task, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("user", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FileSerializer(serializers.ModelSerializer):
    """Media file serializer."""

    class Meta:
        model = MediaFile
        fields = ["id", "file", "task"]
        read_only_fields = ["id"]
        extra_kwargs = {"file": {"required": True}}


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer with optional user assignment (assign_To) and file uploads."""

    comments = TaskCommentSerializer(many=True, required=False, read_only=True)
    files = FileSerializer(many=True, required=False, read_only=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=True, use_url=False),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Task
        fields = (
            "id",
            "creator",
            "title",
            "description",
            "tags",
            "badgeColor",
            "created",
            "deadline",
            "comments",
            "uploaded_files",
            "files",
            "taskCategorie",
            "position",
            "assign_To",
        )
        read_only_fields = ("id", "creator", "files", "comments")
        extra_kwargs = {"description": {"required": False}}

    def _replace_task_files(self, task, files, request):
        """Delete existing files on a task and attach the newly uploaded ones."""
        auth_user = request.user if request else None
        if not auth_user or not files:
            return
        task.files.all().delete()
        with transaction.atomic():
            for task_file in files:
                MediaFile.objects.create(task=task, file=task_file)

    def _compute_default_position(self):
        """Compute the position for a new task (append at the end of the list)."""
        default_position = Decimal("60000.0000")
        last_task = Task.objects.last()
        if last_task is None or last_task.position is None:
            return default_position
        return default_position + last_task.position

    def create(self, validated_data):
        request = self.context.get("request")
        auth_user = request.user if request else None
        if not auth_user:
            raise serializers.ValidationError("Authentication required to create a task.")

        validated_data["creator"] = auth_user
        validated_data["position"] = self._compute_default_position()
        files = validated_data.pop("uploaded_files", [])

        task = Task.objects.create(**validated_data)
        self._replace_task_files(task, files, request)

        return task

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if not request:
            raise ValidationError("Request context is required for update.")

        validated_data.pop("creator", None)
        files = validated_data.pop("uploaded_files", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._replace_task_files(instance, files, request)

        return instance


class TaskFileSerializer(TaskSerializer):
    """Serializer for task detail view."""

    files = FileSerializer(many=True, required=False)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
    )

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ("files", "uploaded_files")
