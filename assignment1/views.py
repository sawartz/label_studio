from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect,reverse
from users.functions import login
from users.models import User
from projects.models import Project
from .models import Assignment,QcStatus,Projects,FolderProjectMapping
from core import views
from organizations.models import Organization

#used
def add_qc_status(request):
   if request.method == 'POST':
       status = request.POST['status']
       task_id = request.POST['task_id']
       if task_id == None:
           return JsonResponse({'status':'missing task id'},safe=False)
       try:
               qc_status = QcStatus.objects.get(task_id=task_id)
               qc_status.status = status
               qc_status.save()
               return JsonResponse({'status':'StatusUpdated'},safe=False)
       except QcStatus.DoesNotExist:
                  qc_status = QcStatus(task_id=task_id, status=status)
                  qc_status.save()
                  return JsonResponse({'status':'StatusUpdated'},safe=False)


#####
from label_studio_sdk import Client
from django.http import JsonResponse
from django.http import HttpResponse
LABEL_STUDIO_URL = 'http://13.232.114.25:8080/'
user = User.objects.get(email='aaa@gmail.com')
API_KEY = user.auth_token


#used
# def fetch_qc_status(request):
#    if request.method == 'POST':
#       task_id = request.POST['task_id']
#       try:
#          status = QcStatus.objects.get(task_id=task_id).status
#       except:
#          status = 'Pending'
#       return JsonResponse({'status':status},safe=False)

#used
def get_user_list(request):
   if request.method == 'POST':
      all_users = User.objects.exclude(email="aaa@gmail.com")
      user_list = []
      for user in all_users:
         user_list.append({
            "id" : user.id,
            'email' : user.email
         })
      return JsonResponse(user_list,safe=False)

#used
def assign_bucket(request):
    if request.method == 'POST':
       bucket_id =request.POST.get('bucket_id')
       assigned_to = request.POST.get('assigned_to')
       qc_person = request.POST.get('qc_person')
       if bucket_id == None:
          return JsonResponse({'status':'missing project_id'},safe=False)
       try:
            assignment = Assignment.objects.get(project_id=bucket_id)
            assignment.assigned_to = assigned_to
            assignment.qc_person = qc_person
            assignment.save()
            return JsonResponse({'assigned_to':assigned_to,'qc_person':qc_person},safe=False)
       except Assignment.DoesNotExist:
            assignment = Assignment(project_id=bucket_id, assigned_to=assigned_to,qc_person=qc_person)
            assignment.save()
            return JsonResponse({'assigned_to':assigned_to,'qc_person':qc_person},safe=False)
             
#used
# def fetch_assigned_project(request):
#    if request.method == 'POST':
#       project_id = request.POST['project_id']
#       try:
#          assigned_to = Assignment.objects.get(project_id=project_id).assigned_to
#       except:
#          assigned_to = 'Pending'
#       return JsonResponse({'status':assigned_to},safe=False)

#used
def delete_users(request):
    if request.method == 'POST':
      user_ids = request.POST.get('user_ids')
      for user_id in user_ids:
        user_email = User.objects.get(id=user_id).email
        if user_email != 'aaa@gmail.com':
            user = User.objects.get(email=user_email)
            user.delete()
            try:
               Assignment.objects.filter(assigned_to=user_email).delete()
            except:
               pass
      return JsonResponse({'status':'UsersDeleted'},safe=False)
    
def delete_bucket(request):
    if request.method == 'POST':
      bucket_id = request.POST.get('bucket_id')
      if bucket_id == None:
           return JsonResponse({'status':'missing bucket_id'},safe=False)
      # first delete all tasks
      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      for task in ls.get_project(bucket_id).get_tasks():
         task_id = task["id"]
         try:
            QcStatus.objects.get(task_id=task_id).delete()
         except:
            pass
      
      Project.objects.get(id=bucket_id).delete()
      FolderProjectMapping.objects.get(folder_name=ls.get_project(bucket_id).title).delete()
      try:
         Assignment.objects.get(project_id=bucket_id).delete()
      except:
         pass
      FolderProjectMapping.objects.get(folder_name=ls.get_project(bucket_id).title).delete()
      return JsonResponse({'status':'Project(s)Deleted'},safe=False)

def create_bucket(request):
    if request.method == 'POST':
      bucket_name = request.POST.get('bucket_name')
      project_id = request.POST.get('project_id')
      if bucket_name == None or project_id == None:
           return JsonResponse({'status':'missing bucket_name or project_id'},safe=False)

      # create folder
      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      buckets = ls.get_projects()
      for bucket in buckets:
         if str(bucket_name).lower() == str(bucket.title).lower():
            return JsonResponse({'status':'BucketAlreadExists'},safe=False)
      ls.start_project(title=bucket_name)
      mapping = FolderProjectMapping(folder_name=bucket_name, project_name=Projects.objects.get(id=project_id).project_name)
      mapping.save()
      return JsonResponse({'status':'BucketCreated'},safe=False)


def create_project(request):
    if request.method == 'POST':
      project_name = request.POST.get('project_name')
      projects = Projects.objects.all()
      for project in projects:
         if str(project_name).lower() == str(project.project_name).lower():
            return JsonResponse('Already a project with same name!')
      new_project = Projects(project_name=project_name)
      new_project.save()
      return JsonResponse({'status':'ProjectCreated'},safe=False)
    


def get_project_list(request):
   if request.method == 'POST':
      all_projects = Projects.objects.all()
      project_list = []
      for project in all_projects:
         project_list.append({
            "id" : project.id,
            'project_name' : project.project_name,
         })
      return JsonResponse(project_list,safe=False)


def get_task_list(request):
  if request.method == 'POST':
      bucket_id = request.POST.get('bucket_id')
      if bucket_id == None:
            return JsonResponse({'status':'missing bucket_id'})

      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      bucket = ls.get_project(bucket_id)
      task_urls = []

      for task in bucket.get_tasks():
         task_id = task["id"]
         task_url = f'{LABEL_STUDIO_URL}projects/{str(bucket_id)}/data?tab=&task={str(task_id)}'
         completed_at = task["completed_at"]
         created_at = task["created_at"]
         updated_at = task["updated_at"]
         if completed_at == None:
             task_status = None
         else:
             task_status = 'In Progress'
             
         try:
            qc_status = QcStatus.objects.get(task_id=task_id).status
         except:
            qc_status =  None

         try:
            project_name = FolderProjectMapping.objects.get(folder_name=bucket.title).project_name
         except:
            project_name = None

         try:
            qc_person = Assignment.objects.get(project_id=bucket_id).qc_person
         except:
            qc_person = None

         try:
            assigned_to = Assignment.objects.get(project_id=bucket_id).assigned_to
         except:
            assigned_to = None
            
         task_urls.append(
               {
                  "task_id": task_id,
                  "task_url": task_url,
                  "completed_at": completed_at,
                  "created_at" : created_at,
                  "updated_at" : updated_at,
                  "bucket_title":bucket.title,
                  "projetc_name" : project_name,
                  "assigned_to" : assigned_to,
                  "qc_person" : qc_person,
                  "qc_status" : qc_status,
                  "task_status" : task_status
               }
         )
      return JsonResponse(task_urls, safe=False)


def delete_project(request):
    if request.method == 'POST':
      project_name = request.POST.get('project_name')
      if project_name == None:
           return JsonResponse({'status':'missing project_name'},safe=False)
      project_id = Projects.objects.get(project_name=project_name).id
      # first delete all tasks
      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      requested_project_buckets = FolderProjectMapping.objects.filter(project_name=Projects.objects.get(id=project_id).project_name)
      all_buckets = ls.get_projects()

      for a_bucket in requested_project_buckets:
         for bucket in all_buckets:
             if bucket.title == a_bucket.folder_name:
               for task in bucket.get_tasks():
                  task_id = task["id"]
                  try:
                     QcStatus.objects.get(task_id=task_id).delete()
                  except:
                     pass
               try:
                  Assignment.objects.get(project_id=bucket.id).delete()
               except:
                  pass
               FolderProjectMapping.objects.get(folder_name=bucket.title).delete()
               Project.objects.get(id=bucket.id).delete()
      Projects.objects.get(id=project_id).delete()
      return JsonResponse({'status':'ProjectDeleted'},safe=False)
      

def delete_bucket(request):
    if request.method == 'POST':
      bucket_id = request.POST.get('bucket_id')
      if bucket_id == None:
           return JsonResponse({'status':'missing bucket_id'},safe=False)
      # first delete all tasks
      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      #1
      for task in ls.get_project(bucket_id).get_tasks():
         task_id = task["id"]
         try:
            QcStatus.objects.get(task_id=task_id).delete()
         except:
            pass
      #2
      try:
         Assignment.objects.get(project_id=bucket_id).delete()
      except:
         pass
      #3
      for i in FolderProjectMapping.objects.filter(folder_name=ls.get_project(bucket_id).title):
         i.delete()
      #4
      Project.objects.get(id=bucket_id).delete()
      return JsonResponse({'status': 'BucketDeleted'},safe=False)
    

# def get_user_bucket_list(request):
#    if request.method == 'POST':
#       project_id = request.POST.get('project_id')
#       if project_id == None:
#          return JsonResponse({'status':'missing project_name'},safe=False)
#       project_name = Projects.objects.get(id=project_id).project_name
#       project_folders = FolderProjectMapping.objects.filter(project_name=project_name)
#       all_folders = Project.objects.all()
#       folder_list = []

#       for folder in all_folders:
#          for project_folder in project_folders:
#             if folder.title == project_folder.folder_name:    
#                try:
#                   assigned_to = Assignment.objects.get(project_id=folder.id).assigned_to
#                except:
#                   assigned_to = None
#                try:
#                   qc_person = Assignment.objects.get(project_id=folder.id).qc_person
#                except:
#                   qc_person = None
#                folder_list.append({
#                   "id" : folder.id,
#                   'title' : folder.title,
#                   "assigned_to": assigned_to,
#                   "qc_person" : qc_person,
#                }) 
#       return JsonResponse(folder_list,safe=False)


# used
def get_bucket_list(request):
   if request.method == 'POST':
      project_id = request.POST.get('project_id')
      if project_id == None:
         return JsonResponse({'status':'missing project_name'},safe=False)
      project_name = Projects.objects.get(id=project_id).project_name
      project_buckets = FolderProjectMapping.objects.filter(project_name=project_name)
      ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
      all_buckets = ls.get_projects()
      bucket_list = []

      for bucket in all_buckets:
         for project_bucket in project_buckets:
            if bucket.title == project_bucket.folder_name:
               accepted_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Accepted").count()
               rejected_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Rejected").count()
               total_tasks = len(bucket.get_tasks())

               try:
                  assigned_to = Assignment.objects.get(project_id=bucket.id).assigned_to
               except:
                  assigned_to = None
               try:
                  qc_person = Assignment.objects.get(project_id=bucket.id).qc_person
               except:
                  qc_person = None
               try:
                   assigned_at = Assignment.objects.get(project_id=bucket.id).assigned_at
               except:
                   assigned_at = None

               bucket_list.append({
                  "bucket_id" : bucket.id,
                  'bucket_title' : bucket.title,
                  "assigned_to": assigned_to,
                  "qc_person" : qc_person,
                  "project_name" : project_name,
                  "project_id" : project_id,
                  "created_at" : bucket.created_at,
                  "assigned_at" : assigned_at,
                  "accepted_tasks" : accepted_tasks,
                  "rejected_tasks" : rejected_tasks,
                  "total_tasks" :total_tasks,
                  
               }) 
      return JsonResponse(bucket_list,safe=False)
   

def get_user_bucket_list(request):
  if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role')
        project_name = request.POST.get('project_name')
        project_id =Projects.objects.get(project_name=project_name).id
        if email == None or role== None or project_name == None:
             return JsonResponse({'status':'missing role or email or project_name'},safe=False)
        
        project_all_buckets = FolderProjectMapping.objects.filter(project_name=project_name)

        ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
        buckets = ls.get_projects()

        filter_p = Assignment.objects.filter(assigned_to=email)
        
        user_all_buckets = {}
        for i in filter_p:
            try:
               bucket_id = i.project_id
               bucket_name = Project.objects.get(id=bucket_id).title
               user_all_buckets[bucket_name] = bucket_id 
            except:
               pass
        fl = []
        for j in project_all_buckets:
           if j.folder_name in user_all_buckets:
               fl.append(user_all_buckets[j.folder_name])

        filter_buckets = []
        for bucket in buckets:
            if int(bucket.id) in fl:
                    accepted_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Accepted").count()
                    rejected_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Rejected").count()
                    total_tasks = len(bucket.get_tasks())
                    try:
                       qc_person = Assignment.objects.get(project_id=bucket.id).qc_person
                    except:
                       qc_person = None

                    try:
                       assigned_to = Assignment.objects.get(project_id=bucket.id).assigned_to
                    except:
                       assigned_to = None

                    try:
                        assigned_at = Assignment.objects.get(project_id=bucket.id).assigned_at
                    except:
                        assigned_at = None
                           
                    filter_buckets.append(
                        {
                            'bucket_id':bucket.id,
                            "bucket_title":bucket.title,
                            "assigned_to" : assigned_to,
                            "qc_person" : qc_person,
                            "project_name" : project_name,
                            "project_id" : project_id,
                            "created_at" : bucket.created_at,
                            "assigned_at" : assigned_at,
                            "accepted_tasks" : accepted_tasks,
                            "rejected_tasks" : rejected_tasks,
                            "total_tasks" :total_tasks,
                        }
                    )
        return JsonResponse(filter_buckets, safe=False)



def get_qc_person_bucket_list(request):
  if request.method == 'POST':
        email = request.POST.get('email')
        if email == None:
             return JsonResponse({'status':'missing email'},safe=False)

        ls = Client(url=LABEL_STUDIO_URL, api_key=str(API_KEY))
        buckets = ls.get_projects()
        filter_buckets = []

        filter_p = Assignment.objects.filter(qc_person=email)

        fl = []
        for i in filter_p:
            fl.append(i.project_id)

        for bucket in buckets:
            if int(bucket.id) in fl:
                    accepted_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Accepted").count()
                    rejected_tasks = QcStatus.objects.filter(project_id=bucket.id, status="Rejected").count()
                    total_tasks = len(bucket.get_tasks())
                    try:
                       qc_person = Assignment.objects.get(project_id=bucket.id).qc_person
                    except:
                       qc_person = None

                    try:
                       assigned_to = Assignment.objects.get(project_id=bucket.id).assigned_to
                    except:
                       assigned_to = None

                    try:
                        assigned_at = Assignment.objects.get(project_id=bucket.id).assigned_at
                    except:
                        assigned_at = None

                    project_name = FolderProjectMapping.objects.get(folder_name=bucket.title).project_name
                    project_id = Projects.objects.get(project_name=project_name).id
                     
                    filter_buckets.append(
                        {
                            'bucket_id':bucket.id,
                            "bucket_title":bucket.title,
                            "assigned_to" : assigned_to,
                            "qc_person" : qc_person,
                            "project_name" : project_name,
                            "project_id" : project_id,
                            "created_at" : bucket.created_at,
                            "assigned_at" : assigned_at,
                            "accepted_tasks" : accepted_tasks,
                            "rejected_tasks" : rejected_tasks,
                            "total_tasks" :total_tasks,
                        }
                    )
        return JsonResponse(filter_buckets, safe=False)