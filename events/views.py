# from https://www.youtube.com/watch?v=4EJlrweJE-M&list=PLCC34OHNcOtqW9BJmgQPPzUpJ8hl49AGy&index=2

from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
from django.contrib.auth.models import User  # Since using django's user model
from .forms import VenueForm, EventForm, EventFormAdmin
from django.http import HttpResponseRedirect, HttpResponse, FileResponse
import csv
from django.contrib import messages
import io  # For PDF generator
# pip install reportlab
from reportlab.pdfgen import canvas  # For PDF generator
from reportlab.lib.units import inch  # For PDF generator
from reportlab.lib.pagesizes import letter  # For PDF generator
from django.core.paginator import Paginator  # For pagination


def admin_approval(request):
    event_count = Event.objects.all().count()
    venue_count = Venue.objects.all().count()
    user_count = User.objects.all().count()

    event_list = Event.objects.all().order_by('-date')
    if request.user.is_superuser:
        if request.method == 'POST':
            # unchecked boxes don't get passed back, so will uncheck
            # everything, then re-check those that are approved
            event_list.update(approved=False)
            # since checkboxes are named 'boxes' in HTML tag
            id_list = request.POST.getlist('boxes')
            # update the database
            for x in id_list:
                # since items in id_list are strings
                Event.objects.filter(pk=int(x)).update(approved=True)

            messages.success(
                request, 'Event List Approval Has Been Updated')
            return redirect('admin-approval')
        else:
            return render(request, 'events/admin_approval.html', {
                'event_list': event_list,
                'event_count': event_count,
                'venue_count': venue_count,
                'user_count': user_count,
            })
    else:
        messages.success(request, 'You\'re not authorized to view this page')
        return redirect('home')


def my_events(request):
    if request.user.is_authenticated:
        me = request.user.id
        events = Event.objects.filter(attendees=me)
        return render(request, 'events/my_events.html', {
            'events': events
        })
    else:
        messages.success(request, 'You Aren\'t Authorized to View This Page!')
        return redirect('home')


def venue_pdf(request):  # Generate PDF File Venue List
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # Create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)
    # Designate the model
    venues = Venue.objects.all()
    # Create blank list
    lines = []

    # Loop
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append('')

    for line in lines:
        textob.textLine(line)
    # Finish up
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    # Return something
    return FileResponse(buf, as_attachment=True, filename='venues.pdf')


def venue_csv(request):  # Generate CSV File Venue List
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename = venues.csv'
    # Create a csv writer
    writer = csv.writer(response)
    # Designate the model
    venues = Venue.objects.all()
    # Add column headers to the csv file
    writer.writerow(['Venue Name', 'Address', 'Zip Code',
                    'Phone', 'Web Address', 'Email'])
    # Loop through and output
    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code,
                        venue.phone, venue.web, venue.email_address])
    # Write to output file
    return response


def venue_text(request):  # Generate Text File Venue List
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename = venues.txt'
    # Designate the model
    venues = Venue.objects.all()
    lines = []
    # Loop through and output
    for venue in venues:
        lines.append(
            f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.phone}\n{venue.web}\n{venue.email_address}\n\n\n')
    # Write to textfile
    response.writelines(lines)
    return response


def delete_venue(request, venue_id):
    event = Venue.objects.get(pk=venue_id)
    event.delete()
    return redirect('list-venues')


def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user == event.manager:  # confirm user is owner before deleting
        event.delete()
        messages.success(request, 'Event deleted')
        return redirect('list-events')
    else:
        messages.success(request, 'Insufficient permission to delete event')
    return redirect('list-events')


def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    if request.user.is_superuser:
        form = EventFormAdmin(request.POST or None, instance=event)
    else:
        # 'instance=venue" loads current values
        form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        event = form.save()
        return redirect('list-events')

    return render(request, 'events/update_event.html', {
        # context dictionary
        'event': event,
        'form': form
    })


def add_event(request):
    submitted = False
    if request.method == 'POST':
        if request.user.is_superuser:
            form = EventFormAdmin(request.POST)
            if form.is_valid():  # validate against DB req's (format, blank)
                form.save()
                return HttpResponseRedirect('/add_event?submitted=True')
        else:
            form = EventForm(request.POST)  # pass POSTed data into EventForm
            if form.is_valid():
                event = form.save(commit=False)
                event.manager = request.user  # logged-in user
                event.save()
                # redirect back to page with variable submitted = True
                return HttpResponseRedirect('/add_event?submitted=True')
    else:
        # Just going to the page, not submitting
        if request.user.is_superuser:
            form = EventFormAdmin
        else:
            form = EventForm
        if 'submitted' in request.GET:  # means form was just submitted
            submitted = True
    return render(request, 'events/add_event.html', {'form': form, 'submitted': submitted})


def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    # request.FILES handles image uploads
    # 'instance=venue" loads current values
    form = VenueForm(request.POST or None,
                     request.FILES or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
    return render(request, 'events/update_venue.html', {
        # context dictionary
        'venue': venue,
        'form': form
    })


def search_venues(request):
    if request.method == 'POST':
        # retrieve 'searched' variable from POST
        searched = request.POST.get('searched')
        venues = Venue.objects.filter(name__contains=searched)
        return render(request, 'events/search_venues.html', {'searched': searched, 'venues': venues})
    else:
        return render(request, 'events/search_venues.html', {})


def search_events(request):
    if request.method == 'POST':
        # retrieve 'searched' variable from POST
        searched = request.POST.get('searched')
        events = Event.objects.filter(name__contains=searched)
        return render(request, 'events/search_events.html', {'searched': searched, 'events': events})
    else:
        return render(request, 'events/search_events.html', {})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue_owner = User.objects.get(pk=venue.owner)
    return render(request, 'events/show_venue.html', {
        # context dictionary
        'venue': venue,
        'venue_owner': venue_owner,
    })


def list_venues(request):
    # venue_list = Venue.objects.all().order_by('name')  # '?' will randomize
    venue_list = Venue.objects.all()
    # Setup pagination
    p = Paginator(Venue.objects.all(), 3)  # (what to paginate, # per page)
    page = request.GET.get('page')
    venues = p.get_page(page)
    return render(request, 'events/venues.html', {
        # context dictionary
        'venue_list': venue_list,
        'venues': venues,
    })


def add_venue(request):
    submitted = False
    if request.method == 'POST':
        # pass POSTed data and image file into VenueForm
        # request.FILES handles image uploads
        form = VenueForm(request.POST, request.FILES)
        if form. is_valid():  # validate against DB req's (format, blank)
            venue = form.save(commit=False)
            # to commit additional info that wasn't submitted in form
            venue.owner = request.user.id
            venue.save()
            # form.save()
            print('FORM SUBMITTED')
            # redirect back to page with variable submitted = True
            return HttpResponseRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:  # means form was just submitted
            submitted = True
    return render(request, 'events/add_venue.html', {'form': form, 'submitted': submitted})


def all_events(request):
    event_list = Event.objects.all().order_by(
        'name', 'venue')  # negative alphabetical = '-name'
    return render(request, 'events/event_list.html', {
        # context dictionary
        'event_list': event_list
    })


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):  # %B = month
    name = 'Craig'
    # month = month.title()  # capitalizes first letter of every word
    month = month.capitalize()  # capitalizes only first
    # convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)  # ensure that it's a number

    # Create a calendar
    cal = HTMLCalendar().formatmonth(year, month_number)

    # Get current year
    now = datetime.now()
    current_year = now.year

    # Get current time
    # %I = use 12 hour clock, %H = 24 hour clock
    time = now.strftime('%I:%M:%S %p')

    # Query the Events Model For Dates
    event_list = Event.objects.filter(
        date__year=year,
        date__month=month_number
    )

    return render(request, 'events/home.html', {
        # This stuff is called 'context dictionary' - gets passed to HTML
        'name': name,
        'year': year,
        'month': month,
        'month_number': month_number,
        'cal': cal,
        'current_year': current_year,
        'time': time,
        'event_list': event_list,
    })
