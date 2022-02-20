from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class Reservation(models.Model): # Resrvation 라는 이름의 객체 틀(Model) 생성
    user = models.CharField(max_length=10) # 예약자학번
    room_type = models.CharField(max_length=10) # 방 종류
    room_date =  models.DateField(max_length=20) # 예약 날짜
    room_start_time = models.FloatField() # 시작 시간 0900
    room_finish_time = models.FloatField() # 종료 시간 2100
    pub_date = models.DateTimeField(default=timezone.now) # pub_date 라는 날짜 시간 데이터 저장

class Blog(models.Model): # Blog 라는 이름의 객체 틀(Model) 생성
    category = models.CharField(max_length=20, default='공지사항') # 공지사항인지 아닌지(주인 찾아요, 물건 찾아요, 공지사항)
    title = models.CharField(max_length=200) # title 라는 최대 200 글자의 문자 데이터 저장
    pub_date = models.DateTimeField('date published') # pub_date 라는 날짜 시간 데이터 저장
    # body = models.TextField() # body 라는 줄글 문자 저장
    description = RichTextUploadingField(blank=True,null=True) # editor
    # 이 객체를 가르키는 말을 title로 정하겠다
    def __str__(self):
        return self.title