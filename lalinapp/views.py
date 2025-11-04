from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.models import User, auth
from datetime import datetime, timedelta
from django.db.models import Sum, Max
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from django.shortcuts import render, redirect, get_object_or_404





# Create your views here.
def home(request):
    if request.user.is_authenticated:
        title = 'Home'
        for user in User.objects.all():
            user.save()
        context = {'title': title}
        return render(request, 'pages/home.html', context)
    else:
        return redirect('login')


def login(request):
    title = 'Đăng nhập'
    form_li = SignInForm()
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Tài khoản không hợp lệ!')
            return redirect('login')
    context = {'title': title,
               'form_li': form_li}
    return render(request, 'pages/login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('/')


def profile_detail(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user:
        if request.user.is_superuser or request.user.username == username:
            title = f'Hồ sơ {username}'
            departments = Department.objects.all()
            positions = Position.objects.filter(department=user.profile.position.department)

            context = {
                'title': title,
                'user': user,
                'positions': positions,
                'departments': departments
            }
            return render(request, 'pages/profile_detail.html', context)
        else:
            return redirect('profile-detail', username=request.user.username)
    else:
        return redirect('home')


def time_keeping(request):
    if request.user.is_authenticated:
        title = 'Check In'
        date = datetime.now().date()
        if request.POST:
            check = request.POST.get('check', '')
            if check == 'in':
                Timesheet.objects.create(user=request.user, date=datetime.now().date(), checkin=datetime.now().time())
                messages.success(request, 'Check-in thành công, làm việc nào!!!')
            if check == 'out':
                sheet = Timesheet.objects.filter(user=request.user, date=datetime.now().date()).order_by('-id').first()
                sheet.checkout = datetime.now().time()
                sheet.save()
                messages.success(request, 'Cảm ơn bạn đã đi làm ngày hôm nay!!!')
            return redirect('home')
        context = {'title': title, 'date': date}
        return render(request, 'pages/time_keeping.html', context)
    else:
        messages.error(request, 'Vui lòng đăng nhập')
        return redirect('login')


def timesheet(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    if user and request.user.is_authenticated:
        if request.user.username == username:
            title = f'Bảng chấm công {username}'
            sheets = Timesheet.objects.filter(user=user).order_by('-date')
            sheets.total_hour = sheets.aggregate(total_hour=Sum('work_hour'))['total_hour']
            sheets.count_late = sheets.filter(status='Muộn').count()
            status = request.GET.get('status', '')
            start_date = request.GET.get('start-date', '')
            end_date = request.GET.get('end-date', '')
            if status:
                sheets = sheets.filter(status=status)
            if start_date and end_date:
                sheets = sheets.filter(date__range=[start_date, end_date])
            elif start_date:
                sheets = sheets.filter(date__range=[start_date, datetime.now().date()])
            elif end_date:
                sheets = sheets.filter(date__range=[datetime.now().date(), end_date])

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
            context = {'title': title,
                       'start_date': start_date,
                       'end_date': end_date,
                       'status': status,
                       'page_obj': page_obj,
                       'query_params': query_params.urlencode()}

            return render(request, 'pages/timesheet.html', context)
        else:
            messages.warning(request, 'Hãy vào tài khoản của mình để xem')
            return redirect('timesheet', username=request.user.username)
    else:
        messages.error(request, 'Vui lòng đăng nhập')
        return redirect('home')


def complaint(request):
    if request.user.is_authenticated:
        title = 'Đơn khiếu nại'
        form = ComplaintForm(request.POST or None)
        my_complaint = Complaint.objects.filter(user=request.user).order_by('-created_at')

        if request.POST and form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return render(request, 'pages/complaint.html', {
                'title': title,
                'form': form,  # reset form
                'my_complaint': my_complaint,
                'success': True
            })

        context = {
            'title': title,
            'form': form,
            'my_complaint': my_complaint
        }
        return render(request, 'pages/complaint.html', context)
    else:
        return redirect('login')


def complaint_detail(request, id):
    try:
        letter = Complaint.objects.get(id=id)
        if request.user == letter.user or request.user.is_superuser:
            title = 'Chi tiết khiếu nại'
            if request.POST:
                letter.status = 'Đã xử lý'
                letter.save()
                messages.success(request, 'Đã xử lý khiếu nại')
                return redirect('complaint')
            return render(request, 'pages/complaint_detail.html', {'title': title, 'complaint': complaint})
        else:
            return redirect('complaint')
    except Complaint.DoesNotExist:
        return redirect('complaint')



def request_absence(request, username):
    # Lấy user hoặc trả 404 nếu không tồn tại (gọn hơn try/except)
    user = get_object_or_404(User, username=username)

    title = 'Danh sách nghỉ phép'

    # Lấy danh sách đơn nghỉ phép, sắp xếp mới nhất
    absence_requests = AbsenceRequest.objects.filter(user=user).order_by('-start_date')

    # Lấy ngày kết thúc gần nhất (nếu có)
    max_end_date = absence_requests.aggregate(max_end_date=Max('end_date'))['max_end_date']
    if max_end_date:
        max_end_date += timedelta(days=1)

    # Tạo form (POST hoặc GET)
    form = AbsenceRequestForm(request.POST or None, request.FILES or None)

    # Nếu người dùng gửi form
    if request.method == 'POST':
        if form.is_valid():
            absence = form.save(commit=False)
            absence.user = user  # nên dùng user đang xem, hoặc request.user nếu muốn người đăng nhập
            absence.save()
            messages.success(request, 'Gửi yêu cầu nghỉ phép thành công!')
            return redirect('request-absence', username=username)
        else:
            messages.error(request, 'Có lỗi xảy ra, vui lòng kiểm tra lại thông tin!')

    # Context truyền qua template
    context = {
        'title': title,
        'day_off_requests': absence_requests,
        'form': form,
        'max_end_date': max_end_date
    }

    return render(request, 'pages/request_absence.html', context)