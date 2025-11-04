from django.db import models

# Create your models here.
from datetime import time, datetime, timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=255)
    base_salary = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    salary_coef = models.DecimalField(max_digits=4, decimal_places=1)

    def __str__(self):
        return f'{self.name} - {self.department.name}'


class Profile(models.Model):
    image = models.ImageField(upload_to='')
    cccd = models.CharField(max_length=12,unique=True)
    gender = models.CharField(max_length=10, choices=[('Nam', 'Nam'), ('Nữ', 'Nữ')])
    dob = models.DateField()
    phone_number = models.CharField(max_length=15,unique=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255)
    major = models.CharField(max_length=100)
    degree = models.CharField(max_length=20, choices=[('Đại học', 'Đại học'), ('Cao đẳng', 'Cao đẳng')])
    contract_period = models.CharField(max_length=20)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gross_salary = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=0)
    STATUS_CHOICES = [
        ('working', 'Đang làm việc'),
        ('on_leave', 'Nghỉ phép'),
        ('resigned', 'Đã nghỉ việc'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')

    def __str__(self):
        return f'Profile: {self.user.username}'

    def save(self, *args, **kwargs):
        self.gross_salary = self.position.salary_coef * self.position.department.base_salary
        super().save(*args, **kwargs)


class Topic(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    title = models.CharField(max_length=255, default='Không có tiêu đề')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_anonymous = models.BooleanField(default=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    content = models.TextField()
    status = models.CharField(max_length=30, choices=[('Đang xử lý', 'Đang xử lý'), ('Đã xử lý', 'Đã xử lý')],
                              default='Đang xử lý')
    evidence = models.FileField(upload_to='complaints/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.is_anonymous:
            title = f'Khiếu nại của {self.user} - {self.topic.name}'
        else:
            title = f'Khiếu nại ẩn danh - {self.topic.name}'
        return title


class Timesheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    checkin = models.TimeField()
    checkout = models.TimeField(blank=True, null=True)
    work_hour = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Đi đúng giờ', 'Đi đúng giờ'), ('Đi làm trễ', 'Đi làm trễ')],
                              default='Đi đúng giờ')
    ot = models.IntegerField(null=True, blank=True, default=1)
    late_time = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f'{self.user.username} - {self.date}'

    def update_status(self):
        # Standard check-in time (8:00 AM)
        standard_checkin = time(8, 0, 0)
        if self.checkin:  # Ensure check-in time is set
            checkin_datetime = datetime.combine(self.date, self.checkin)
            standard_datetime = datetime.combine(self.date, standard_checkin)
            if self.checkin > standard_checkin:
                late_delta = checkin_datetime - standard_datetime
                self.late_time = late_delta.seconds // 3600  # Convert seconds to minutes
                self.status = 'Đi làm trễ'
            else:
                self.late_time = 0
                self.status = 'Đi đúng giờ'
        if self.work_hour:
            self.ot = max(0, int(self.work_hour - 9))

    def save(self, *args, **kwargs):
        if self.checkin and self.checkout:
            checkin = datetime.combine(self.date, self.checkin)
            checkout = datetime.combine(self.date, self.checkout)
            self.work_hour = (checkout - checkin).seconds / 3600

        self.update_status()
        super().save(*args, **kwargs)


class AbsenceRequest(models.Model):
    STATUS_CHOICES = [
        ('Đang chờ', 'Đang chờ'),
        ('Đã duyệt', 'Đã duyệt'),
        ('Từ chối', 'Từ chối'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Đang chờ')
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"

