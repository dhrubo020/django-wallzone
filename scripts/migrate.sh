#!/bin/bash


pipenv run manage.py makemigrations
pipenv run manage.py migrate