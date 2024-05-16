from decimal import Decimal
from rest_framework import serializers

from core.models import MediaFile, Task, TaskCategorie, TaskComment
from django.contrib.auth import get_user_model
from rest_framework.serializers import ValidationError
from rest_framework.test import APIClient
from django.db import transaction
class TaskCommentSerializer(serializers.ModelSerializer):
    """Task comment serializer"""
    class Meta:
        model=TaskComment
        fields= ("id", "user", "text", "task",)
        read_only_fields = ("id","user")


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        task = validated_data.pop('task', None)
        # Assuming task is a Task object
        taskComment = TaskComment.objects.create(task=task, **validated_data)

        return taskComment
    

    def update(self, instance, valivade_data):
        valivade_data.pop('user', None)
        for attr, value in valivade_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    


class FileSerializer(serializers.ModelSerializer):
    """Media File serializer"""
    class Meta:
        model = MediaFile
        fields= ['id', 'file', 'task']
        read_only_fields = ['id']
        extra_kwargs = {'file':{'required': True}}


class TaskSerializer(serializers.ModelSerializer):
    """Task serializer"""
    comments = TaskCommentSerializer(many=True, required=False,  read_only=True)
    files = FileSerializer(many=True, required=False, read_only=True)  # Assuming files_list is a related field on Task model
    uploaded_files = serializers.ListField(
       child=serializers.FileField( max_length=1000000, allow_empty_file=True, use_url=False), write_only=True, required=False
    )
    
    class Meta:
        model=Task
        fields = ("id", "creator", "title", "description", "tags", "badgeColor", "created", "deadline", "comments", "uploaded_files","files", "taskCategorie", "position")
        read_only_fields = ("id", "creator", "files", "comments", )
        extra_kwargs = {'description': {'required': False}}


    
    


    def _get_or_add_images(self, task, files,  request=None):
        auth_user = request.user if request else None
        if auth_user:
            existing_files = task.files.all()
            if existing_files.exists():
                # Task already has files, delete them
                existing_files.delete()
            with transaction.atomic():
                for task_file in files:
                    file_obj = MediaFile.objects.create( task=task, file=task_file,)
                    print("file created ", file_obj)

           


    def create(self, validated_data):
        request = self.context.get('request')
        auth_user = request.user if request else None
        default_position  = 60000.0000
        if auth_user : 

            validated_data['creator'] = auth_user
            last_task = Task.objects.last()

            if last_task is not None:
                # If the last_task exists, get its position
                position = last_task.position

                if position is not None:
                    # If position is not None, calculate the new position
                    validated_data['position'] = Decimal(default_position) + position
                else:
                    # Handle the case where position is None
                    validated_data['position'] = Decimal(default_position)
            else:
                # Handle the case where last_task is None
                validated_data['position'] = Decimal(default_position)

            print("Contenu de position ",  validated_data['position'])
            task_categorie_id = validated_data.pop('taskCategorie', None)

            files = validated_data.pop('uploaded_files', [])
            if task_categorie_id is not None:
                # Assuming TaskCategorie is the related model
               validated_data['taskCategorie'] = task_categorie_id
            task = Task.objects.create(**validated_data)

           
            if files is not None:  # Check for None
                self._get_or_add_images(task, files, request)
            self._get_or_add_images(task,files, request)
            return task
        else:
            raise serializers.ValidationError("Authentication required to create a task.")
            
    


    def update(self, instance, validate_data):
        request = self.context.get('request')
        if not request:
            raise ValidationError("Request context is required for update.")
        
        
        validate_data.pop('creator', None)

        files = validate_data.pop('uploaded_files', [])

        print("contenu du fichier ", len(files))
       
        if len(files) is not 0:
            self._get_or_add_images( instance, files,request)
       

       
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance





class TaskFileSerializer(TaskSerializer):
    """Serializer for task detail view."""
    files = FileSerializer(many=True, required=False)  # Assuming files_list is a related field on Task model
    uploaded_files = serializers.ListField(
       child=serializers.FileField( max_length=1000000, allow_empty_file=False, use_url=False), write_only=True
    )

    class Meta(TaskSerializer.Meta):
        fields = TaskSerializer.Meta.fields + ('files','uploaded_files' )

