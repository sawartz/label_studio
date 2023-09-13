from django.db import models

# Create your models here.
class Assignment(models.Model):
    project_id = models.IntegerField(null=False)
    assigned_to = models.CharField(null=True,max_length=100)
    qc_person = models.CharField(null=True,max_length=100)
    assigned_at = models.DateTimeField(auto_now=True,null=True)
    
class QcStatus(models.Model):
    project_id = models.IntegerField(null=True)
    task_id = models.IntegerField(null=True)
    status = models.CharField(null=True,max_length=100)
    reason = models.CharField(null=True,max_length=500)


class Projects(models.Model):
    project_name = models.CharField(null=True,max_length=100)


class FolderProjectMapping(models.Model):
    folder_name = models.CharField(null=True,max_length=100)
    project_name = models.CharField(null=True,max_length=100)

class Status(models.Model):
    bucket_id = models.IntegerField(null=True)
    status = models.CharField(null=True,max_length=50)

    