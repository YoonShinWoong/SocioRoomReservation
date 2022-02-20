from django.shortcuts import render, get_object_or_404, redirect
from .models import Reservation, Blog
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json, time
from django.db.models import Q

# library function
def myrange(start, end, step):
    r = start
    while(r<end):
        yield r
        r += step

########################## C
@login_required
def new(request,room_type):
    # 요일 가져오기
    today =  datetime.now()
    today_day = today.weekday()
    weekday_mark = 0

    # 평일의 경우
    if today_day < 5:
        start_day = today -timedelta(days=today_day) # 시작 월요일 
        start_day_diff = 0 - today_day # 차이 넣기 

    # 토, 일 경우 -> 다음주와 돌아오는 그 다음주까지 예약가능
    elif today_day>=5:
        start_day_diff = 7-today_day # 차이
        weekday_mark = 7-today_day # 주말차이 표시
        start_day = today +timedelta(weekday_mark)
        today_day -= 7
    date_diff = 4-today_day # 마지막 날짜

    # 현재 예약 상황 넘겨 주기
    reservations = Reservation.objects.all()
    day_list = []
    
    # 월~금
    for i in range(0,5):
        day = start_day + timedelta(days=i) # 요일 증가
        reservations_day = reservations.filter(room_type=room_type, user=request.user.username, room_date=day).order_by('room_start_time')
        temp_list = []
        for res in reservations_day:
            temp_list.extend(myrange(res.room_start_time, res.room_finish_time, 0.5))
        day_list.append(temp_list) # 요일 추가

    return render(request, 'reservation/new.html', {'room_type':room_type, 'date_diff':date_diff, 'weekday_mark':weekday_mark, 'day_list':day_list, 'start_day_diff':start_day_diff})

# ajax 통신
def check(request):
    room_type_vr = request.POST.get('room_type', None)
    room_date_vr = request.POST.get('room_date', None) # ajax 통신을 통해서 template에서 POST방식으로 전달
    room_start_time_vr = request.POST.get('room_start_time', None)
    room_finish_time_vr = request.POST.get('room_finish_time', None)
    
    reservations = Reservation.objects.all()
    reserve_date = datetime.strptime(room_date_vr, "%Y-%m-%d ").date()
    check_error = 0 # 정상

    # print(room_type_vr, room_date_vr, room_start_time_vr, room_finish_time_vr)

    # 하루 2건 검사
    if reservations.filter(user=request.user.username, room_date=reserve_date).count() >= 2:
        message="해당일에 이미 2건의 예약을 하셨습니다"
        check_error = 1
        context = { 'message': message,
                    'check_error': check_error}
        return HttpResponse(json.dumps(context), content_type="application/json")


    # 겹치는 시간 있는지 체크
    message="이미 예약된 시간입니다"

    # <1> 오른쪽 겹치기
    if reservations.filter(room_type=room_type_vr,room_date=reserve_date, room_finish_time__gt=room_start_time_vr, room_start_time__lt=room_finish_time_vr ).count() != 0:
        check_error = 1   
        context = { 'message': message,
                    'check_error': check_error}
        return HttpResponse(json.dumps(context), content_type="application/json")
    # <2> 사이 들어가기
    if reservations.filter(room_type=room_type_vr,room_date=reserve_date, room_start_time__lte=room_start_time_vr, room_finish_time__gte=room_finish_time_vr ).count() != 0:
        check_error = 1   
        context = { 'message': message,
                    'check_error': check_error}
        return HttpResponse(json.dumps(context), content_type="application/json")
    # <3> 오른쪽 포개지기
    if reservations.filter(room_type=room_type_vr,room_date=reserve_date, room_start_time__lt=room_finish_time_vr, room_finish_time__gt=room_start_time_vr ).count() != 0:
        check_error = 1   
        context = { 'message': message,
                    'check_error': check_error}
        return HttpResponse(json.dumps(context), content_type="application/json")
    # <4> 밖에 감싸기
    if reservations.filter(room_type=room_type_vr,room_date=reserve_date, room_start_time__gte=room_start_time_vr, room_finish_time__lte=room_finish_time_vr ).count() != 0:
        check_error = 1   
        context = { 'message': message,
                    'check_error': check_error}
        return HttpResponse(json.dumps(context), content_type="application/json")

    # <4> 가능
    context = { 'message': message,
                'check_error': check_error}
    return HttpResponse(json.dumps(context), content_type="application/json")

# C
@login_required
def create(request):
    reserve_date = datetime.strptime(request.GET['room_date'], "%Y-%m-%d ").date()

    # 만들기
    reservation = Reservation() # 객체 만들기
    reservation.user = request.GET['user']  # 내용 채우기
    reservation.room_type = request.GET['room_type']  # 내용 채우기
    reservation.room_date= reserve_date # 내용 채우기

    # 시간 구하기
    reservation.room_start_time = request.GET['room_start_time']  # 내용 채우기
    reservation.room_finish_time= request.GET['room_finish_time'] # 내용 채우기
    reservation.pub_date = timezone.datetime.now() # 내용 채우기
    reservation.save() # 객체 저장하기

    # 내 예약 주소
    return redirect('/reservation/my')               

########################## R
def home(request):
    today =  datetime.now()
    room_1A = Reservation.objects.filter(room_date = today, room_type ='1A')
    room_1B = Reservation.objects.filter(room_date = today, room_type ='1B')
    room_3A = Reservation.objects.filter(room_date = today, room_type ='3A')
    proportion = [0,0,0]
    for r in room_1A:
        proportion[0] += (r.room_finish_time - r.room_start_time)
    for r in room_1B:
        proportion[1] += (r.room_finish_time - r.room_start_time)
    for r in room_3A:
        proportion[2] += (r.room_finish_time - r.room_start_time)

    notice_list = Blog.objects.filter(category="공지사항").order_by('-pub_date') # 공지사항
    notices = notice_list[0:3]

    lost_list = Blog.objects.filter(category="분실물").order_by('-pub_date') # 공지사항
    losts = lost_list[0:3]

    return render(request, 'reservation/home.html', {'notices':notices, 'losts':losts,  'proportion':proportion})

# R 
def detail(request, blog_id) : 
    blog_detail = get_object_or_404(Blog, pk= blog_id) # 특정 객체 가져오기(없으면 404 에러)
    return render(request, 'reservation/detail.html', {'blog':blog_detail})

def index(request, category_name):
    blogs = Blog.objects.filter(category=category_name).order_by('-pub_date')
    category = category_name
    return render(request, 'reservation/index.html', {'category':category, 'blogs':blogs})
########################## U
def edit(request,reservation_id):
    reservation = get_object_or_404(Reservation, pk= reservation_id) # 특정 객체 가져오기(없으면 404 에러)
    min_date = datetime.now().strftime("%Y-%m-%d") # 오늘부터 
    max_date = (datetime.now() +timedelta(days=14)).strftime("%Y-%m-%d") # 14일 후까지 가능
    return render(request, 'reservation/edit.html', {'reservation':reservation, 'min_date':min_date, 'max_date':max_date})

# U
def update(request,reservation_id):
    reservation= get_object_or_404(Reservation, pk= reservation_id) # 특정 객체 가져오기(없으면 404 에러)
    reservation.room_type = request.GET['room_type']  # 내용 채우기
    reservation.room_date= request.GET['room_date'] # 내용 채우기
    reservation.room_start_time = request.GET['room_start_time']  # 내용 채우기
    reservation.room_finish_time= request.GET['room_finish_time'] # 내용 채우기
    reservation.save() # 객체 저장하기

    # 새로운 예약 url 주소로 이동
    return redirect('/reservation/' + str(reservation.id))

########################## D
def delete(request, reservation_id):
    reservation= get_object_or_404(Reservation, pk= reservation_id) # 특정 객체 가져오기(없으면 404 에러)
    if reservation.user == request.user.username:
        reservation.delete()
    return redirect('/reservation/my')                
    
########################## MY 예약
@login_required
def myreservation(request):
    today = date.today() # 오늘날짜
    now_time = datetime.now()
    now = now_time.hour + (now_time.minute / 60) 
    reservations = Reservation.objects.all()
    reservation_list = reservations.filter(Q(user=request.user.username, room_date__gt=today) | Q(user=request.user.username, room_date=today, room_finish_time__gte = now))
    return render(request, 'reservation/myreservation.html',{'reservation_list':reservation_list}) 
    