from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.
class PositionInline(admin.StackedInline):
  model = Position

class DepartmentAdmin(admin.ModelAdmin):
  model = Department


class ComplaintInline(admin.StackedInline):
  model = Complaint


class TopicAdmin(admin.ModelAdmin):
  model = Topic

admin.site.register(Profile)
admin.site.register(Department, DepartmentAdmin)

admin.site.register(Topic, TopicAdmin)
admin.site.register(Position)
admin.site.register(Timesheet)
admin.site.register(AbsenceRequest)
admin.site.register(Complaint)