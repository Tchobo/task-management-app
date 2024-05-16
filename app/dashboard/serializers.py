from tasks.serializers import TaskSerializer
from core.models import Dashboard, TaskCategorie
from rest_framework import serializers




class TaskCategorieSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, required=False, read_only=True)
    class Meta:
        model=TaskCategorie
        fields= ("id", "name", "indexColor", "indexNumber", "defaultTaskCategory", "dashboard", "tasks",)
        read_only_fields = ("id","defaultTaskCategory")

    def create(self, validated_data):
        new_position = 60000.00
       
        last_indexNumber = TaskCategorie.objects.last().indexNumber
        print("voici ", last_indexNumber)
        if last_indexNumber is not None:
            print("indexNumber ", last_indexNumber)
            validated_data['indexNumber'] = float(last_indexNumber)+  new_position
           
        else:
             validated_data['indexNumber'] =  new_position
        #task_Categories = validated_data.pop('task_Categorie', [])
        categorie = TaskCategorie.objects.create(**validated_data)

       

        return categorie


   


class DashboardSerializer(serializers.ModelSerializer):
    """Serializer for Dashboard"""
    categories = TaskCategorieSerializer(many=True, required=False, read_only=True)
    

    
    class Meta:
        model = Dashboard
        fields = ("id", "user", "bordName", "bordDescription", "bordBack", "categories", "slug")
        read_only_fields = ("id","user")

    def create(self, validated_data):
        new_position = 60000
        validated_data['user'] = self.context['request'].user
       
        #task_Categories = validated_data.pop('task_Categorie', [])
        dashboard = Dashboard.objects.create(**validated_data)

       

        return dashboard
    
    def update(self, instance, valivade_data):
        valivade_data.pop('user', None)
        """  task_Categories = valivade_data.pop('task_Categorie', [])
        if task_Categories is not None:
            instance.task_Categorie.clear()
            self._get_or_create_(task_Categories, instance) """

        for attr, value in valivade_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

