# VirtuOhm Connector

This is a tool to collect your information from VirtuOhm (*for students of TH Nuremberg*).

I created it so I do not have to bother using the web service too much and to be able to save the data as CSV and HTML (*Probably they just forgot to implement an export feature*).

![Display and save all grades](https://github.com/tweinreich/virtuohm-connector/raw/main/screenshot-all-grades.png)

## Features
- Display and export current semester grades or all existing grades to CSV and HTML
- Display how many credits (ECTS) you have earned
- Display Study Progress

## Installation
- (optional) set up a python virtual environment (*e.g. with pyenv*)
- install the libraries with `pip install -r requirements.txt`

## Usage
- run the app with `python main.py`

## Roadmap
This is just a collection of ideas without any commitment. Pull Requests are always welcome!

- add more features for the VirtuOhm service
    - download & display statistics for exams
    - gain insights from all collected data
    - persist data in the app (*e.g. with SQLite*)
    - add access to whole catalogue of modules 
    - show which modules are not yet done
- build a unified interface for dealing with all the Ohm services
    - connect to Ohm FBI service to get FWPF's and schedules
    - connect to Study Ohm service to get payment transactions
    - connect to website to get important data in an intuitive and convenient way
- package app to be deployed on Linux, MacOS and Windows to make it easy to install for students without knowledge of IT
