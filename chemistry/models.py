# coding: UTF-8
import datetime
import uuid

from django.db import models
from django.conf import settings

from users.models import UserProfile
from chemistry import (FILE_CHOICES, MODEL_ORIGIN_CHOICES,
                       MODEL_CHOICES, STATUS_CHOICES, MOL_ORIGIN_CHOICES,
                       ORIGIN_UNDEFINED, STATUS_UNDEFINED, STATUS_WORKING,
                       ORIGIN_UPLOAD)


def get_sid():
    return str(uuid.uuid4())


class PresentationCategory(models.Model):
    category = models.CharField(max_length=30, blank=False, unique=True,
                                choices=FILE_CHOICES,
                                verbose_name=u"Attachment File Type")

    class Meta:
        verbose_name = "Attachment File Types"
        verbose_name_plural = "Attachment File Types"

    def __unicode__(self):
        return self.get_category_display()


class ModelTypeCategory(models.Model):
    category = models.CharField(max_length=30, blank=False, unique=True,
                                choices=MODEL_ORIGIN_CHOICES,
                                verbose_name=u"Calculate Model Type")

    class Meta:
        verbose_name = "Calculate Model Type"
        verbose_name_plural = "Calculate Model Type"

    def __unicode__(self):
        return self.get_category_display()


class ModelCategory(models.Model):
    category = models.CharField(max_length=30, blank=False, unique=True,
                                choices=MODEL_CHOICES,
                                verbose_name=u"Calculate Model")
    origin_type = models.ForeignKey(ModelTypeCategory, blank=False)
    desc = models.TextField(blank=True)

    class Meta:
        verbose_name = "Calculate Model"
        verbose_name_plural = "Calculate Model"

    def __unicode__(self):
        return self.get_category_display()


class StatusCategory(models.Model):
    category = models.CharField(max_length=30, blank=False, unique=True,
                                choices=STATUS_CHOICES,
                                verbose_name=u"calculate status")

    class Meta:
        verbose_name = "Calculate Status"
        verbose_name_plural = "Calculate Status"

    def __unicode__(self):
        return self.category


class FileSourceCategory(models.Model):
    category = models.CharField(max_length=30, blank=False, unique=True,
                                choices=MOL_ORIGIN_CHOICES,
                                default=ORIGIN_UNDEFINED)

    class meta:
        verbose_name = "file source"
        verbose_name_plural = "file source"

    def __unicode__(self):
        return self.get_category_display()


class ProcessedFile(models.Model):
    """
    File Storage
    """
    fid = models.CharField(max_length=50, unique=True, blank=False,
                           primary_key=True, default=get_sid)
    title = models.CharField(max_length=500, blank=False)
    file_type = models.CharField(max_length=100, blank=False)
    file_obj = models.FileField(upload_to=settings.PROCESS_FILE_PATH+"/%Y/%m/%d")
    file_source = models.ForeignKey(FileSourceCategory,
                                    default=lambda: FileSourceCategory.objects.get(category=ORIGIN_UPLOAD))
    image = models.FileField(blank=True, null=True,
                             upload_to=settings.PROCESS_FILE_PATH+"/%Y/%m/%d")
    smiles = models.CharField(max_length=2000, blank=True, null=True)

    class Meta:
        verbose_name = "Processed File"
        verbose_name_plural = "Processed File"

    def __unicode__(self):
        return self.title


class SuiteTask(models.Model):
    """
    A group of task, which defined the one calculate submit
    """
    sid = models.CharField(unique=True, blank=False, max_length=50,
                           verbose_name="id", primary_key=True,
                           default=get_sid)
    user = models.ForeignKey(UserProfile, blank=False, verbose_name="user")
    total_tasks = models.IntegerField(blank=False, verbose_name="total tasks")
    has_finished_tasks = models.IntegerField(blank=False, default=0,
                                             verbose_name="Finished number")
    start_time = models.DateTimeField(blank=False,
                                      default=lambda: datetime.datetime.now())
    end_time = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=2000, blank=True)
    notes = models.CharField(max_length=5000, blank=True)
    status = models.ForeignKey(StatusCategory, blank=False,
                               default=STATUS_UNDEFINED)
    models_str = models.CharField(max_length=2000, blank=True)
    models_category_str = models.CharField(max_length=200, blank=True)
    result_pdf = models.FileField(blank=True, null=True,
                                  upload_to=settings.PROCESS_FILE_PATH+"/%Y/%m/%d")
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = "Suite Task"
        verbose_name_plural = "Suite Task"

    def __unicode__(self):
        return self.sid


class SingleTask(models.Model):
    """
    Every specific task
    """
    sid = models.ForeignKey(SuiteTask, blank=False)
    pid = models.CharField(max_length=50, unique=True, blank=False,
                           primary_key=True, default=get_sid)
    temperature = models.FloatField(blank=True, default=-0.0)
    humidity = models.FloatField(blank=True, default=-0.0)
    other = models.FloatField(blank=True, default=-0.0)
    model = models.ForeignKey(ModelCategory, blank=False)
    results = models.TextField(blank=True, null=None)
    result_state = models.CharField(max_length=1000, blank=True, null=None)
    status = models.ForeignKey(StatusCategory, blank=False,
                               default=STATUS_WORKING)
    start_time = models.DateTimeField(blank=False,
                                      default=lambda: datetime.datetime.now())
    end_time = models.DateTimeField(blank=True, null=True)

    file_obj = models.ForeignKey(ProcessedFile, blank=False)
    result_pdf = models.FileField(blank=True, null=True,
                                  upload_to=settings.PROCESS_FILE_PATH+"/%Y/%m/%d")

    class Meta:
        verbose_name = "Single Task"
        verbose_name_plural = "Single Task"

    def __unicode__(self):
        return self.sid.name


class SearchEngineModel(models.Model):
    """
    Search Engineer by Chemspider
    """
    nid = models.CharField(max_length=50, unique=True, blank=False,
                           primary_key=True, default=get_sid)
    commonname = models.CharField(max_length=2000, blank=False, null=True)
    smiles = models.CharField(max_length=1000, blank=False, null=True)
    inchi = models.CharField(max_length=1000, blank=False, null=True)
    inchikey = models.CharField(max_length=1000, blank=False, null=True)
    mf = models.CharField(max_length=2000, blank=False, null=True)
    molecularweight = models.CharField(max_length=200, blank=False, null=True)
    alogp = models.CharField(max_length=200, blank=False, null=True)
    xlogp = models.CharField(max_length=200, blank=False, null=True)
    averagemass = models.CharField(max_length=200, blank=False, null=True)
    monoisotopicmass = models.CharField(max_length=200, blank=False, null=True)
    search_query = models.CharField(max_length=2000, blank=False, null=True)
    image = models.FileField(upload_to=settings.PROCESS_FILE_PATH+"/%Y/%m/%d")

    class Meta:
        verbose_name = "Search Engine"
        verbose_name_plural = "Search Engine"

    def __unicode__(self):
        return self.commonname


class ChemInfoLocal(models.Model):
    """
    Chemistry database for locally search
    """
    cas = models.CharField(max_length=200, blank=False, unique=True)
    einecs = models.CharField(max_length=2000, blank=False)
    einecs_name = models.CharField(max_length=2000, blank=False)
    einecs_mf = models.CharField(max_length=2000, blank=False)
    frequency = models.IntegerField(blank=False)
    positive_atoms = models.IntegerField(blank=False)
    negative_atoms = models.IntegerField(blank=False)
    formal_charge = models.IntegerField(blank=False)
    h_acceptors = models.IntegerField(blank=False)
    h_donors = models.IntegerField(blank=False)
    molecular_solubility = models.FloatField(blank=False)
    alogp = models.FloatField(blank=False)
    logd = models.FloatField(blank=False)
    molecular_formula = models.CharField(max_length=2000, blank=False)
    smiles = models.CharField(max_length=2000, blank=False)
    inchl = models.CharField(max_length=2000, blank=False)
    molecular_savol = models.FloatField(blank=False)
    image = models.FileField(upload_to=settings.SEARCH_IMAGE_PATH, blank=True)

    class Meta:
        verbose_name = "Chemistry Info Local"
        verbose_name_plural = "Chemistry Info Local"

    def __unicode__(self):
        return self.cas
