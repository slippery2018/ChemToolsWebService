# coding: UTF-8
import uuid
import os
import simplejson
import datetime
import re

from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
import pybel

from backend.logging import loginfo
from calcore.models import SingleTask, ProcessedFile, SuiteTask
from const.models import ModelCategory
from const import ORIGIN_DRAW, ORIGIN_SMILE, ORIGIN_UPLOAD
from const.models import StatusCategory, FileSourceCategory
from const import STATUS_WORKING
from const import MODEL_SPLITS
from users.models import UserProfile
from gui.tasks import *


def response_minetype(request):
    if "application/json" in request.META["HTTP_ACCEPT"]:
        return "application/json"
    else:
        return "text/plain"


class JSONResponse(HttpResponse):
    """Json response class"""
    def __init__(self, obj='', json_opts={}, mimetype="application/json",
                 *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


def calculate_tasks(pid_list, smile, mol, models):
    """
    Calculate all tasks
    """
    loginfo(p=pid_list, label="files")
    loginfo(p=smile, label="smile")
    loginfo(p=mol, label="mol")

    number = 0
    if len(pid_list) != 1 or pid_list[0] != "":
        number = len(pid_list)

    number = number + (1 if smile else 0)
    number = number + (1 if mol else 0)

    if number == 0:
        return 0

    number = number * len(models.keys())

    loginfo(p=number, label="calculate_tasks")
    return number


def save_record(f, model_name, sid, source_type, smile=None, arguments=None):
    """
    Here, we use decoartor design pattern,
    this function is the real function
    """

    task = SingleTask()
    task.sid = SuiteTask.objects.get(sid=sid)
    task.pid = str(uuid.uuid4())
    #TODO: add arguments into task
    task.model = ModelCategory.objects.get(category=model_name)

    if source_type == ORIGIN_UPLOAD:
        #here, f is ProcessedFile record instance
        f.file_source = FileSourceCategory.objects.get(category=source_type)
        f.file_type = "mol"
        task.file_obj = f
        f.save()
        task.status = StatusCategory.objects.get(category=STATUS_WORKING)
        task.save()
        calculateTask.delay(task, model_name)
    elif source_type == ORIGIN_SMILE or source_type == ORIGIN_DRAW:
        #here, f is a file path
        processed_f = ProcessedFile()
        obj = File(open(f, "r"))
        processed_f.title = os.path.basename(obj.name)
        processed_f.file_type = source_type
        processed_f.file_source = FileSourceCategory.objects.get(category=source_type)
        processed_f.file_obj = obj
        if smile:
            processed_f.smiles = smile
            #TODO: add database search local picture into here
        processed_f.save()
        task.file_obj = processed_f
        obj.close()
        task.status = StatusCategory.objects.get(category=STATUS_WORKING)
        task.save()
        calculateTask.delay(task, model_name, arguments)
    else:
        loginfo(p=source_type, label="Cannot recongize this source type")
        return

    #TODO: call task query process function filename needs path
    #global molpathtemp


def get_FileObj_by_smiles(smile):
    """
    convert smile into mol file
    Output: file path
    """
    name = str(uuid.uuid4()) + ".mol"
    if not os.path.exists(settings.MOL_CONVERT_PATH):
        os.makedirs(settings.MOL_CONVERT_PATH)
    name_path = os.path.join(settings.MOL_CONVERT_PATH, name)

    mol = pybel.readstring('smi', str(smile))
    mol.addh()
    mol.make3D()
    mol.write('mol', name_path, overwrite=True)

    return name_path


def start_files_task(files_list, model_name, sid, arguments=None):
    """
    start a group task from files list
    It will write a record into SingleTask and send this task
    into system-task query.
    First, it shoud read files_list and convert them into MolFile
    """
    if len(files_list) == 1 and files_list[0] == "" or not files_list:

        loginfo(p=files_list,
                label="Sorry, we cannot calculate files")
        return False

    for fid in files_list:
        record = ProcessedFile.objects.get(fid=fid)
        loginfo(p=record, label="files upload")
        save_record(record, model_name, sid, ORIGIN_UPLOAD, arguments)

    loginfo(p=model_name, label="finish start files task")
    return True


def start_smile_task(smile, model_name, sid, arguments=None):
    """
    start a group task from smile string
    It will write a record into SingleTask and send this task
    into system-task query
    """
    if not smile:
        loginfo(p=smile,
                label="Sorry, we cannot calculate smiles")
        return False

    f = get_FileObj_by_smiles(smile)
    save_record(f, model_name, sid, ORIGIN_SMILE, smile, arguments)

    loginfo(p=model_name, label="finish start smile task")
    return True


def start_moldraw_task(moldraw, model_name, sid, arguments=None):
    """
    start a group task from mol string
    It will write a record into SingleTask and send this task
    into system-task query
    First it should write moldraw into a file and clear the useless lines
    """
    #TODO: maybe we should clear the first three lines which are chemwrite info
    if not moldraw:
        loginfo(p=moldraw,
                label="Sorry, we cannot calculate draw mol files")
        return False

    name = str(uuid.uuid4()) + ".mol"
    path = os.path.join(settings.MOL_CONVERT_PATH, name)
    f = File(open(path, "w"))
    f.write(moldraw)
    f.close()

    save_record(path, model_name, sid, ORIGIN_DRAW, arguments)

    os.remove(path)

    loginfo(p=model_name, label="finish start smile task")

    return True


def get_model_category(model_name):
    try:
        category = ModelCategory.objects.get(category=model_name).\
                                 origin_type.get_category_display()
    except Exception, err:
        loginfo(err)
        loginfo(model_name)
        category = ""

    return category


def get_models_name(models):
    """
    Parse models json into models name and models type name,
    which are CSV format, use MODEL_SPLITS in const.__init__

    Out: a tuple, models_str + models_category_str
    """
    categorys = set()
    for model in models.keys():
        categorys.add(get_model_category(model))

    models_str = MODEL_SPLITS.join(models.keys())
    categorys_str = MODEL_SPLITS.join(list(categorys))

    return (models_str, categorys_str)


def get_email(email=None, backup_email=None):
    if bool(re.match(r"^.+@([a-zA-Z0-9]+\.)+([a-zA-Z]{2,})$", email)):
        return email
    else:
        #TODO: here, we should add email force-varify in registration page
        return backup_email


def suitetask_process(request, smile=None, mol=None, notes=None,
                      name=None, email=None, unique_names=None,
                      models=None):
    """
    real record operation
    Out:
        is_submitted, True or False
        message: summit message
    """
    is_submitted = False
    message = None

    #TODO: we should check remaining counts
    if request.user.is_anonymous():
        is_submitted = False
        message = "anonymous auth failed!"
        return (is_submitted, message)

    total_tasks = calculate_tasks(unique_names, smile, mol, models)

    if total_tasks == 0:
        is_submitted = False
        message = "Please choice one model or input one search!"
        return (is_submitted, message)

    suite_task = SuiteTask()
    suite_task.sid = str(uuid.uuid4())
    suite_task.user = UserProfile.objects.get(user=request.user)
    suite_task.total_tasks = int(total_tasks)
    suite_task.has_finished_tasks = 0
    suite_task.start_time = datetime.datetime.now()
    suite_task.end_time = datetime.datetime.now()
    suite_task.name = name
    suite_task.notes = notes
    suite_task.models_str, suite_task.models_category_str = get_models_name(models)
    suite_task.status = StatusCategory.objects.get(category=STATUS_WORKING)
    suite_task.email = get_email(email, request.user.email)
    suite_task.save()

    loginfo(p="finish suite save")

    flag = False
    try:
        for k, v in models.items():
            flag = flag | start_smile_task(smile, k, suite_task.sid, v['temperature'])
            flag = flag | start_moldraw_task(mol, k, suite_task.sid, v['temperature'])
            flag = flag | start_files_task(unique_names, k, suite_task.sid, v['temperature'])
    except Exception, err:
        loginfo(err)
        flag = False

    if flag:
        is_submitted = True
        message = "Congratulations to you! calculated task has been submitted!"
    else:
        is_submitted = False
        message = "No one tasks can be added into calculated task queue successful!"
        suite_task.delete()

    return (is_submitted, message)


def get_models_selector(models_str):
    """
    get models name and color flag

    Out:
        a list, element is a two-tuple.
    """
    colors = ("badge-success", "badge-warning", "badge-important",
              "badge-info", "badge-inverse", " ")
    models_list = models_str.split(MODEL_SPLITS)

    result = []

    for i in range(0, len(models_list)):
        e = {}
        e["color"] = colors[i % len(colors)]
        e["value"] = models_list[i]
        result.append(e)

    return result
