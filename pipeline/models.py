from django.db import models

# Create your models here.


class BuildPipeline(models.Model):
  project_name = models.CharField(max_length=20)
  scm_type = models.CharField(max_length=30)
  scm_url = models.CharField(max_length=30)
  scm_branch = models.CharField(max_length=10)
  credential = models.CharField(max_length=40)
  mirror_type = models.IntegerField(max_length=2)
  mirror_script_type = models.IntegerField(max_length=2)
  mirror_script = models.CharField(max_length=1000)
  auto_delpoy = models.BooleanField()
  deploy_stack = models.CharField(max_length=20)
  deploy_stack_id = models.CharField(max_length=20)
  deploy_service = models.CharField(max_length=20)
  deploy_service_id = models.CharField(max_length=20)
  deploy_project = models.CharField(max_length=20)
  deploy_project_id = models.CharField(max_length=20)
  username = models.CharField(max_length=30)
  password = models.CharField(max_length=30)
  api_key = models.CharField(max_length=100)