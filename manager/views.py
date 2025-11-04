from django.shortcuts import render, redirect
from django.db.models import Count, Q,Case, When, F, Sum, ExpressionWrapper, fields
from django.contrib import messages
from datetime import datetime, timedelta, date
from lalinapp.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal
from .forms import *
from lalinapp.models import AbsenceRequest, Department



# Create your views here.
def home(request):
    if request.user.is_superuser:
        # for profile in Profile.objects.all():
        #   profile.save()
        title = 'Dashboard'
        count_emp = User.objects.count()
        count_emp_male = User.objects.filter(profile__gender='Nam').count()
        count_emp_female = User.objects.filter(profile__gender='Nữ').count()
        today = timezone.now().date()
        count_late = Timesheet.objects.filter(date=today, status='Đến Muộn').exclude(checkin=None).count()
        count_ontime = Timesheet.objects.filter(date=today, status='Đúng Giờ').exclude(checkin=None).count()
        count_manage = User.objects.filter(profile__position__name='Trưởng phòng').count()
        count_employee = User.objects.filter(profile__position__name='Nhân viên').count()
        # count_leave_today = DayOffRequest.objects.filter(start_date__lte=datetime.now().date(), end_date__gte=datetime.now().date(), status='approved').count()
        count_leave_today = AbsenceRequest.objects.filter(status='pending').count()
        count_dpm = Department.objects.count()
        count_it = User.objects.filter(profile__position__department__name='IT').count()
        count_nhansu = User.objects.filter(profile__position__department__name='Nhân sự').count()
        count_kinhdoanh = User.objects.filter(profile__position__department__name='Kinh doanh').count()
        count_taichinh = User.objects.filter(profile__position__department__name='Tài chính').count()
        count_thietke = User.objects.filter(profile__position__department__name='Thiết kế').count()
        count_sanxuat = User.objects.filter(profile__position__department__name='Sản xuất').count()
        count_mkt = User.objects.filter(profile__position__department__name='Marketing').count()
        it_work = Timesheet.objects.filter(user__profile__position__department__name='IT', date=datetime.now().date()).count()
        nhansu_work = Timesheet.objects.filter(user__profile__position__department__name='Nhân sự', date=datetime.now().date()).count()
        kinhdoanh_work = Timesheet.objects.filter(user__profile__position__department__name='Kinh doanh', date=datetime.now().date()).count()
        taichinh_work = Timesheet.objects.filter(user__profile__position__department__name='Tài chính', date=datetime.now().date()).count()
        thietke_work = Timesheet.objects.filter(user__profile__position__department__name='Thiết kế', date=datetime.now().date()).count()
        sanxuat_work = Timesheet.objects.filter(user__profile__position__department__name='Sản xuất', date=datetime.now().date()).count()
        mkt_work = Timesheet.objects.filter(user__profile__position__department__name='Marketing', date=datetime.now().date()).count()
        complaint_pending = Complaint.objects.filter(created_at__date=date.today()).count()
        absence_pending = AbsenceRequest.objects.filter(status='pending').count()
        context = {'title': title,
                  'today': today,
                  'count_late': count_late,
                  'count_ontime': count_ontime,
                  'count_manage': count_manage,
                  'count_employee': count_employee,
                  'count_emp': count_emp,
                  'count_emp_male': count_emp_male,
                  'count_emp_female': count_emp_female,
                  'count_leave_today': count_leave_today,
                  'count_dpm': count_dpm,
                  'count_it': count_it,
                  'count_nhansu': count_nhansu,
                  'count_kinhdoanh': count_kinhdoanh,
                  'count_thietke': count_thietke,
                  'count_taichinh': count_taichinh,
                  'count_sanxuat': count_sanxuat,
                  'count_mkt': count_mkt,
                  'it_work': it_work,
                  'nhansu_work': nhansu_work,
                  'kinhdoanh_work': kinhdoanh_work,
                  'taichinh_work': taichinh_work,
                  'thietke_work': thietke_work,
                  'sanxuat_work': sanxuat_work,
                  'mkt_work': mkt_work,
                  'complaint_pending': complaint_pending,
                  'absence_pending': absence_pending}
        return render(request, 'pages/management.html', context)
    else:
        messages.warning(request, 'Không có quyền truy cập')
        return redirect('/')

def employee(request):
    if request.user.is_superuser:
        title = 'Tất cả nhân viên'
        emps = User.objects.exclude(username='admin').order_by('-profile__start_date')
        departments = Department.objects.all()

        # Xử lý khi thay đổi trạng thái
        if request.POST:
            id = request.POST.get('change_status')
            status = request.POST.get('status')
            emp = Profile.objects.get(user__id=id)
            emp.status = status
            emp.save()
            messages.success(request, f"Trạng thái của nhân viên đã được cập nhật thành {dict(Profile.STATUS_CHOICES).get(status)}")
            return redirect('employee')

        # Bộ lọc và phân trang
        keyword = request.GET.get('keyword', '')
        position = request.GET.get('position', '')
        start_date = request.GET.get('start-date', '')
        end_date = request.GET.get('end-date', '')
        department = request.GET.get('department', '')
        if keyword:
            emps = emps.filter(Q(first_name__icontains=keyword)|Q(last_name__icontains=keyword))
        if position:
            emps = emps.filter(profile__position__name=position)
        if department:
            emps = emps.filter(profile__position__department__name=department)
        if start_date and end_date:
            emps = emps.filter(profile__start_date__range=[start_date, end_date])
        elif start_date:
            emps = emps.filter(profile__start_date__gte=start_date)
        elif end_date:
            emps = emps.filter(profile__start_date__lte=end_date)

        if not emps.exists():
            messages.error(request, 'Không tìm thấy người dùng nào.')

        paginator = Paginator(emps, 10)
        page_number = request.GET.get('page', '')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        context = {
            'title': title,
            'page_obj': page_obj,
            'departments': departments,
            'position': position,
            'department': department,
            'keyword': keyword,
            'start_date': start_date,
            'end_date': end_date,
            'query_params': query_params.urlencode(),
        }
        return render(request, 'pages/employee.html', context)
    else:
        messages.warning(request, 'Không có quyền truy cập')
        return redirect('/')

def create_employee(request):
   if request.user.is_authenticated:
       title = 'Thêm nhân viên'
       form_e = EmployeeCreateForm(request.POST or None)
       form_p = ProfileForm(request.POST or None, request.FILES or None)

       if request.POST:
           # Kiểm tra nếu form không hợp lệ
           if not form_e.is_valid() or not form_p.is_valid():
               messages.error(request, 'Thông tin nhập không hợp lệ. Vui lòng kiểm tra lại.')

           # Kiểm tra trùng lặp email
           elif User.objects.filter(email=form_e.cleaned_data.get('email')).exists():
               messages.error(request, 'Email đã tồn tại trong hệ thống.')
           else:
               # Lưu thông tin nhân viên và profile
               emp = form_e.save()
               profile = form_p.save(commit=False)
               profile.user = emp
               profile.save()
               messages.success(request, 'Thêm nhân viên thành công')
               return redirect('employee')

       context = {
           'title': title,
           'form_e': form_e,
           'form_p': form_p
       }
       return render(request, 'pages/create_employee.html', context)
   else:
       return redirect('/')

def update_employee(request, username):
    if request.user.is_superuser:
        try:
            user = User.objects.get(username=username)
            title = f'Sửa hồ sơ {user.username}'
            form_e = EmployeeUpdateForm(request.POST or None, instance=user)
            form_p = ProfileForm(request.POST or None, request.FILES or None, instance=user.profile)
            if request.POST:
                if form_e.is_valid() and form_p.is_valid():
                    form_e.save()
                    form_p.save()
                    messages.success(request, 'Chỉnh sửa hồ thành công')
                    return redirect('profile-detail', username=user.username)
            context = {'title': title,
                       'user': user,
                       'form_e':form_e,
                       'form_p':form_p}
            return render(request, 'pages/update_employee.html', context)
        except User.DoesNotExist:
            return redirect('home')
    else:
        return redirect('home')

from lalinapp.models import Timesheet, Department
from datetime import datetime
def main_timesheet(request):
    if request.user.is_superuser:
        title = 'Bảng công'
        sheets = Timesheet.objects.all().order_by('-date')
        keyword = request.GET.get('keyword', '')
        status = request.GET.get('status', '')
        start_date = request.GET.get('start-date', '')
        end_date = request.GET.get('end-date', '')
        department = request.GET.get('department', '')
        today = request.GET.get('today', '')  # Lấy tham số "today"
        departments = Department.objects.all()

        # Bộ lọc
        if keyword:
            sheets = sheets.filter(user__username__icontains=keyword)
        if department:
            sheets = sheets.filter(user__profile__position__department__name=department)
        if status:
            sheets = sheets.filter(status=status)
        if today:  # Lọc theo ngày hôm nay
            sheets = sheets.filter(date=date.today())
        elif start_date and end_date:
            sheets = sheets.filter(date__range=[start_date, end_date])
        elif start_date:
            sheets = sheets.filter(date__range=[start_date, datetime.now().date()])
        elif end_date:
            sheets = sheets.filter(date__range=[datetime.now().date(), end_date])

        # Phân trang
        paginator = Paginator(sheets, 6)
        page_number = request.GET.get('page', '')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        query_params = request.GET.copy()
        if 'page' in query_params:
            query_params.pop('page')

        # Context
        context = {
            'title': title,
            'keyword': keyword,
            'start_date': start_date,
            'end_date': end_date,
            'status': status,
            'page_obj': page_obj,
            'department': department,
            'departments': departments,
            'query_params': query_params.urlencode()
        }
        return render(request, 'pages/main_timesheet.html', context)
    else:
        messages.warning(request, 'Không có quyền truy cập')
        return redirect('/')


def total_salary(request):
    if request.user.is_superuser:
        title = 'Bảng lương'
        sheets = Timesheet.objects.all()

        # Filter by keyword (username)
        keyword = request.GET.get('keyword', '')
        if keyword:
            sheets = sheets.filter(user__username__icontains=keyword)

        # Filter by department
        dpm_req = request.GET.get('dpm', '')
        if dpm_req and dpm_req != "Tất cả":
            sheets = sheets.filter(user__profile__position__department__name=dpm_req)

        # Get current month and year
        current_month = timezone.now().month
        current_year = timezone.now().year
        month_req = request.GET.get('month', current_month)
        year_req = request.GET.get('year', current_year)

        # Define constants
        num_days_in_month = 26

        # Fetch approved day-off requests
        approved_absence_requests = AbsenceRequest.objects.filter(
            status='approved',
            start_date__year=year_req
        ).annotate(
            days_off=ExpressionWrapper(
                (F('end_date') - F('start_date')) + 1,
                output_field=fields.IntegerField()
            )
        )

        # Query the sheets with aggregation
        sheets = sheets.filter(
            date__month=month_req,
            date__year=year_req
        ).values(
            'user__id', 'user__username', 'user__first_name', 'user__last_name'
        ).annotate(
            total_work_hour=Sum('work_hour'),
            total_salary=F('user__profile__gross_salary'),
            ot_sum=Sum('ot'),
            lt_sum=Sum('late_time'),
            days_worked=Count('date', distinct=True)
        ).order_by('user__id')

        # Calculate additional data for each sheet
        for sheet in sheets:

            previous_approved_absence = approved_absence_requests.filter(
                user__username=sheet['user__username'],
                start_date__month__lt=month_req
            ).aggregate(total_requests=Count('id'))['total_requests'] or 0

            approved_absence_current_month = approved_absence_requests.filter(
                user__username=sheet['user__username'],
                start_date__month=month_req
            ).aggregate( total_requests=Count('id'))['total_requests'] or 0

            # Adjust approved days off if yearly limit exceeds 12
            if previous_approved_absence + approved_absence_current_month > 12:
                approved_absence_current_month = max(0, 12 - previous_approved_absence)

            # Calculate attendance days
            sheet['prev_approved_absence'] = previous_approved_absence
            sheet['approved_absence'] = approved_absence_current_month
            sheet['att_day'] = sheet['days_worked'] + approved_absence_current_month

            # Calculate bonuses, penalties, and salary
            sheet['ot_sal'] = Decimal(100000) * Decimal(sheet['ot_sum'])
            sheet['awrd'] = Decimal(1000000) if sheet['ot_sum'] > 15 else Decimal(2000000) if sheet['ot_sum'] > 20 else 0
            sheet['neg_sal'] = Decimal(100000) * Decimal(sheet['lt_sum'])
            salary = sheet['total_salary'] or Decimal(0)
            sheet['real_salary'] = int(salary / Decimal(26) * sheet['att_day'])

            # Calculate deductions for BHXH and TNCN
            bhxh = 0
            tncn = 0
            if sheet['days_worked'] > 12:
                bhxh = int(sheet['total_salary'] * Decimal(10.5) / Decimal(100))
                tncn = int(sheet['total_salary'] * Decimal(5) / Decimal(100))

            sheet['bhxh'] = bhxh
            sheet['tncn'] = tncn

            # Calculate final salary
            real_sal = sheet['real_salary'] + sheet['awrd'] + sheet['ot_sal'] - sheet['neg_sal'] - bhxh - tncn
            sheet['real_sal'] = real_sal

        return render(request, 'pages/total_salary.html', {
            'sheets': sheets,
            'list_month': range(1, 13),
            'list_year': range(2023, 2026),
            'year_req': int(year_req),
            'title': title,
            'month_req': int(month_req),
            'keyword': keyword,
            'dpm_req': dpm_req,
            'dpms': Department.objects.all(),
        })

    else:
        messages.warning(request, 'Bạn không có quyền truy cập!')
        return redirect('/')

def complaint(request):
  if request.user.is_authenticated:
    title = 'Danh sách đơn khiếu nại'
    complaints = Complaint.objects.all().order_by('-created_at')
    topics = Topic.objects.all()
    topic_rq = request.GET.get('topic', '')
    status = request.GET.get('status', '')
    time = request.GET.get('time', '')
    if topic_rq:
      complaints = complaints.filter(topic__name=topic_rq)
    if status:
      complaints = complaints.filter(status=status)
    if time:
      now = timezone.now()
      if time == 'Hôm nay':
        complaints=complaints.filter(created_at__date=now.date())
      elif 'ngày qua' in time:
          days = int(time.split()[0])
          time_days_ago = now - timedelta(days=days)
          complaints = complaints.filter(created_at__gte=time_days_ago)

    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page', '')
    try:
      page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
      page_obj = paginator.page(1)
    except EmptyPage:
      page_obj = paginator.page(paginator.num_pages)
    query_params = request.GET.copy()
    if 'page' in query_params:
      query_params.pop('page')
    context = {'title': title,
               'topics': topics,
               'time': time,
               'topic_rq': topic_rq,
               'status': status,
               'page_obj': page_obj,
               'query_params': query_params.urlencode()}
    return render(request, 'pages/main_complaint.html', context)
  else:
    messages.warning(request, 'Không có quyền truy cập')
    return redirect('/')

def absence_review(request):
    title = 'Đơn nghỉ phép'
    requests = AbsenceRequest.objects.order_by('-start_date')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start-date', '')
    end_date = request.GET.get('end-date', '')
    # Filter by keyword (username)
    keyword = request.GET.get('keyword', '')
    if keyword:
        requests = requests.filter(user__username__icontains=keyword)

    # Filter by department
    dpm_req = request.GET.get('dpm', '')
    if dpm_req and dpm_req != "Tất cả":
        requests = requests.filter(user__profile__position__department__name=dpm_req)
    if status:
      if status == 'Đang chờ':
        requests = requests.filter(status='pending')
      elif status == 'Đã duyệt':
        requests = requests.filter(status='approved')
      else:
        requests = requests.filter(status='rejected')
    if start_date and end_date:
      requests = requests.filter(start_date__range=[start_date, end_date])
    elif start_date:
      requests = requests.filter(start_date__range=[start_date, datetime.now().date()])
    elif end_date:
      requests = requests.filter(start_date__range=[datetime.now().date(), end_date])

    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page', '')
    try:
      page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
      page_obj = paginator.page(1)
    except EmptyPage:
      page_obj = paginator.page(paginator.num_pages)
    query_params = request.GET.copy()
    if 'page' in query_params:
      query_params.pop('page')
    if request.POST:
        accept = request.POST.get('accept', '')
        refuse = request.POST.get('refuse', '')
        absence_request = AbsenceRequest.objects.get(id=accept if accept else refuse)
        absence_request.status = 'approved' if accept else 'rejected'
        absence_request.save()
        messages.success(request, 'Đã duyệt yêu cầu' if accept else 'Đã từ chối yêu cầu')
        return redirect('absence')
    context = {'title': title,
               'start_date': start_date,
               'end_date': end_date,
               'status': status,
               'page_obj': page_obj,
               'query_params': query_params.urlencode(),
               'dpm_req': dpm_req,
               'dpms': Department.objects.all(),
               }
    return render(request, 'pages/absence_review.html', {
        'absences': requests,
        'title': title,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'page_obj': page_obj,
        'query_params': query_params.urlencode(),
        'dpm_req': dpm_req,
        'dpms': Department.objects.all(),
    })

def complaint(request):
    return render(request, 'pages/complaint.html')