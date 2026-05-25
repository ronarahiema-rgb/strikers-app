
from flask import render_template, Blueprint, request, redirect, url_for, session, flash, current_app

#function to take data out the form

def form_data(*args):
    data = []
    if request.method == "POST":
        for arg in args:
            data.append(request.form[arg])
    
    return data

