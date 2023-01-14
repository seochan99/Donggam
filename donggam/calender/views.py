import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from django.urls import reverse
from .models import *
import calendar
from .utils import Calendar, ReservationForm, RegularReservationForm

def index(request):
    return render(request, 'calender/index.html')

def group_notice(request):
    return render(request, 'calender/group_notice.html')

def regular_notice(request):
    return render(request, 'calender/regular_notice.html')

class CalendarView(generic.ListView):
    model = Reservation
    template_name = 'calender/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get('month', None))
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d) 
        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)

        change_status()
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - datetime.timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + datetime.timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def reservation(request, reservation_id=None):
    instance = get_object_or_404(Reservation, pk=reservation_id)
    if instance.status == '1' or instance.status == '0':    
        form = ReservationForm(request.POST or None, instance=instance)
        if request.POST and form.is_valid():
            instance.status = '1'
            form.save()
            return HttpResponseRedirect(reverse('calender:calendar'))
        return render(request, 'calender/reservation.html', {'form': form})
    else :
        return redirect('calender:reservation_check', reservation_id=reservation_id)

def reservationCheck(request, reservation_id):
    instance = get_object_or_404(Reservation, pk=reservation_id)
    if instance.status == '1':
        status = '신청대기'
    elif instance.status == '2':
        status = '검토중'
    elif instance.status == '3':
        status = '승인완료'
    date = str(instance.date).split('-')
    date = date[0] + '년 ' + date[1] + '월 ' + date[2] + '일'
    time = instance.time + ':00'
    datetime = date + ' / ' + time
    return render(request, 'calender/group_check.html', 
    {
        'reservation' : instance,
        'status': status,
        'datetime': datetime,
    })

def password(request, reservation_id):
    return render(request, 'calender/password.html', {'reservation_id' : reservation_id})

def pw_check(request, reservation_id):
    instance = get_object_or_404(Reservation, pk=reservation_id)
    password = instance.phone.split('-')[-1]
    if password == request.POST['pw']:
        return redirect('calender:reservation_edit', reservation_id=reservation_id)
    else :
        return redirect('calender:password', reservation_id = reservation_id)

def change_status():
    print(datetime.datetime.today())
    beforedates = Reservation.objects.filter(date__range=[datetime.datetime.today() - datetime.timedelta(days=30), datetime.datetime.today() - datetime.timedelta(days=1)])
    targets = beforedates.filter(status = '0')
    for t in targets:
        t.status = '4'
        t.save()
    return 

from django.core.paginator import Paginator

def regular_list(request):
    instances = RegularReservation.objects.all().order_by('-pk')
    page = request.GET.get('page', '1')
    paginator = Paginator(instances, '5')
    page_obj = paginator.page(page)

    tourdates = RegularDate.objects.filter(date__range=[datetime.datetime.today(), datetime.datetime.today() + datetime.timedelta(days=31)])
    return render(request, 'calender/regular_list.html', 
    {
        'page_obj': page_obj,
        'tour_dates': tourdates, 
    })

def regular_form(request, reservation_id=None):
    if reservation_id != None:
        instance = get_object_or_404(RegularReservation, pk=reservation_id)
    else :
        instance = RegularReservation()
    form = RegularReservationForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        instance.status = '1'
        form.save()
        return HttpResponseRedirect(reverse('calender:regular_list'))
    return render(request, 'calender/regular_form.html', {'form': form})

def regular_detail(request, reservation_id):
    instance = get_object_or_404(RegularReservation, pk = reservation_id)
    if instance.age == 'u':
        age = '14세이상'
    else :
        age = '14세미만'
    if instance.grade == 'n':
        grade = '기타'
    else :
        grade = str(instance.grade) + '학년'
    return render(request, 'calender/regular_detail.html', 
    {
        'reservation' : instance,
        'age' : age,
        'grade' : grade,

    })

def regular_pw(request, reservation_id):
    if request.method ==  'GET':
        return render(request, 'calender/regular_password.html', {'reservation_id' : reservation_id})
    
    elif request.method == 'POST':
        instance = get_object_or_404(RegularReservation, pk=reservation_id)
        password = instance.phone.split('-')[-1]
        if password == request.POST['pw']:
            return redirect('calender:regular_detail', reservation_id = reservation_id)
        else :
            return redirect('calender:regular_pw', reservation_id = reservation_id)

def regular_delete(request, reservation_id):
    instance = get_object_or_404(RegularReservation, pk = reservation_id)
    instance.delete()
    return redirect('calender:regular_list')