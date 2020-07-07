from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db.models import Q
from .models import *
from django.template.defaulttags import register
from django.core.paginator import Paginator
import datetime

@register.filter
def convert_bytes(num):
	num = int(num)
	for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
		if num < 1024.0:
			return "%3.1f %s" % (num, x)
		num /= 1024.0

@register.filter
def count_file(folder):
	file = File.objects.filter(path=folder)
	return len(file)


def home(request):
	folders = Folder.objects.all().order_by('-date_modified')
	query = request.GET.get('query')
	folder = request.GET.get('folder')
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	date = request.GET.get('date')
	st_time = request.GET.get('st_time')
	en_time = request.GET.get('en_time')
	if start_date and end_date:
		start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
		end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')
		folders = folders.filter(date_modified__range=[start_date, end_date])
	if folder:
		folder = folder.replace("/", "\\")
		folders = folders.filter(path=folder)
	if query:
		folders = folders.filter(name__contains=query)
	if date:
		date = datetime.datetime.strptime(date, '%d-%m-%Y')
		folders = folders.filter(date_modified__date=date.strftime('%Y-%m-%d'))
	if st_time and en_time:
		st_time = [int(i) for i in st_time.split(":")]
		en_time = [int(i) for i in en_time.split(":")]
		folders = folders.filter(
			date_modified__time__range=(
				datetime.time(st_time[0],st_time[1]),
				datetime.time(en_time[0],en_time[1])
				))
	page = request.GET.get('page', 1)
	paginator = Paginator(folders, 20)
	try:
		folders = paginator.page(page)
	except PageNotAnInteger:
		folders = paginator.page(1)
	except EmptyPage:
		folders = paginator.page(paginator.num_pages)
	return render(request, 'index.html', {'folders':folders})

def file(request):
	files = File.objects.all().order_by('-date_modified')
	query = request.GET.get('query')
	folder = request.GET.get('folder')
	start_date = request.GET.get('start_date')
	end_date = request.GET.get('end_date')
	date = request.GET.get('date')
	st_time = request.GET.get('st_time')
	en_time = request.GET.get('en_time')
	if start_date and end_date:
		start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
		end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')
		files = files.filter(date_modified__range=[start_date, end_date])
	if folder:
		folder = folder.replace("/", "\\")
		folder = Folder.objects.get(path=folder)
		files = files.filter(path=folder)
	if query:
		files = files.filter(name__contains=query)
	if date:
		date = datetime.datetime.strptime(date, '%d-%m-%Y')
		files = files.filter(date_modified__date=date.strftime('%Y-%m-%d'))
	if st_time and en_time:
		st_time = [int(i) for i in st_time.split(":")]
		en_time = [int(i) for i in en_time.split(":")]
		files = files.filter(
			date_modified__time__range=(
				datetime.time(st_time[0],st_time[1]),
				datetime.time(en_time[0],en_time[1])
				))
	page = request.GET.get('page', 1)
	paginator = Paginator(files, 20)
	try:
		files = paginator.page(page)
	except PageNotAnInteger:
		files = paginator.page(1)
	except EmptyPage:
		files = paginator.page(paginator.num_pages)
	return render(request, 'file.html', {'files':files})

def settings(request):
	settings = Settings.objects.all()
	if request.method == "POST":
		file = request.FILES.get('file')
		folder_path = request.POST.get('folder_path')
		if file:
			data = file.read().decode("utf-8")
			file_lines = data.split("\n")
			for line in file_lines:
				Settings.objects.create(path=line)
			return redirect('settings')
		elif folder_path:
			Settings.objects.create(path=folder_path)
			return redirect('settings')
	status = request.GET.get('status')
	if status == "active_all":
		settings.update(status = True)
		return redirect('settings')
	elif status == "inactive_all":
		settings.update(status = False)
		return redirect('settings')
	elif status == "delete_all":
		settings.delete()
		return redirect('settings')
	return render(request, 'settings.html', {'settings':settings})

def Update_setting(request, id, status):
	settings = Settings.objects.get(id=id)
	if status == "True":
		settings.status = False
	else:
		settings.status = True
	settings.save()
	return redirect('settings')

def delete_settings(request, id):
	settings = Settings.objects.get(id=id)
	settings.delete()
	return redirect('settings')