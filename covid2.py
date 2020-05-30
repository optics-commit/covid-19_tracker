import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
import matplotlib.dates as mdates
from matplotlib import pyplot as plt

import datetime
from datetime import date
import time

import tkinter as tk
from tkinter import ttk

import sqlite3
import json
import requests

url = "https://corona.lmao.ninja/v2/countries/"

payload = {}
headers = {}

style.use("seaborn-whitegrid")

fontLabel = ("Verdana", 12)
fontBlock = ("Verdana", 16)
countries = ["India", "India" ,"USA", "Italy", "Germany", "Iran", "Spain"]

f = plt.figure()
a = plt.gca()

formatter = mdates.DateFormatter("%d-%m")
locator = mdates.DayLocator()

x_values = []
y_cases = []
y_deaths = []
y_recovered = []

conn = sqlite3.connect('covid19.sqlite')
cur = conn.cursor()

class covid(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args , **kwargs)

        tk.Tk.wm_title(self, "Covid-19")

        s = ttk.Style()
        s.configure("TMenubutton", background = "#23EDF9", foreground = "#23EDF9" )

        self.bind("<Escape>", close)

        canvas = FigureCanvasTkAgg(f, self)

        graph = tk.StringVar(self, "1")
        scvar = tk.StringVar(self, "India")

        types = {"Cases" : "1", "Deaths" : "2", "Recovered" : "3"}

        countryL = ttk.Label(self, text = "Country", font = (fontLabel))
        countryS = ttk.OptionMenu(self, scvar, *countries, command = lambda x: self.UpdateCountry(canvas, scvar.get(), TotalCases, Deaths, Recovered, graph))
        RD1 = tk.Radiobutton(self, text = "Cases", variable = graph, indicator = 0, value = "1", command = lambda : self.UpdateGraph(canvas, graph.get(), scvar.get()))
        RD2 = tk.Radiobutton(self, text = "Deaths", variable = graph, indicator = 0, value = "2", command = lambda : self.UpdateGraph(canvas, graph.get(), scvar.get()))
        RD3 = tk.Radiobutton(self, text = "Recovered", variable = graph, indicator = 0, value = "3", command = lambda : self.UpdateGraph(canvas, graph.get(), scvar.get()))
        TotalCasesT = ttk.Label(self, text = "Total Cases", font = (fontBlock), anchor = "center")
        TotalCases = ttk.Label(self, text = "0", font = (fontBlock), anchor = "center")
        DeathsT = ttk.Label(self, text = "Deaths", font = (fontBlock), anchor = "center")
        Deaths = ttk.Label(self, text = "0", font = (fontBlock), anchor = "center")
        RecoveredT = ttk.Label(self, text = "Recovered", font = (fontBlock), anchor = "center")
        Recovered = ttk.Label(self, text = "0" , font = (fontBlock), anchor = "center")

        Update()
        self.UpdateCountry(canvas, "India", TotalCases, Deaths, Recovered, graph);

        canvas.draw()
        canvas.get_tk_widget().place(x = 150, y = 100)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.place(x = 330, y = 70, width = 800)

        countryL.place(x = 2, y = 7, anchor = tk.NW)
        countryS.place(x = 120, y = 5, anchor = tk.NW, width = 1000)

        TotalCasesT.place(x = 50, y = 100, width = 130)
        TotalCases.place(x = 50, y = 135, width = 130)

        DeathsT.place(x = 50, y = 200, width = 130)
        Deaths.place(x = 50, y = 235, width = 130)

        RecoveredT.place(x = 50, y = 300, width = 130)
        Recovered.place(x = 50, y = 335, width = 130)

        RD1.place(x = 330, y = 45, width = 50)
        RD2.place(x = 380, y = 45, width = 50)
        RD3.place(x = 430, y = 45,)


    def UpdateCountry(self, canvas, country, C, D, R, G):

        cur.execute('''SELECT * from '''+ country)
        global x_values, y_cases, y_deaths, y_recovered
        x_values = []
        y_cases = []
        y_deaths = []
        y_recovered = []

        for row in cur:
            x_values.append(datetime.datetime.strptime(row[0], "%m/%d/%y").date())
            y_cases.append(row[1])
            y_deaths.append(row[2])
            y_recovered.append(row[3])

        a.clear()
        a.xaxis.set_major_formatter(formatter)
        a.tick_params(axis = 'x' , rotation = 70)
        a.plot(x_values, y_cases)
        a.set_title(country)
        a.set_ylabel("No. of confirmed Cases")
        canvas.draw()

        G.set("1")

        cur.execute("SELECT * from "+ country +" ORDER BY cases DESC LIMIT 1")
        for x in  cur:
            C['text'] = x[1]
            D['text'] = x[2]
            R['text'] = x[3]

    def UpdateGraph(self, canvas, tyGraph, country):
        a.clear()
        a.xaxis.set_major_formatter(formatter)
        a.tick_params(axis = 'x', rotation = 70)
        if(tyGraph == '1'):
            a.plot(x_values, y_cases)
            a.set_title(country)
            a.set_ylabel("No. of Conformed Cases")
            canvas.draw()
        elif (tyGraph == '2'):
            a.plot(x_values, y_deaths)
            a.set_title(country)
            a.set_ylabel("No. of Deaths")
            canvas.draw()
        elif (tyGraph == '3'):
            a.plot(x_values, y_recovered)
            a.set_title(country)
            a.set_ylabel("No. of Patients Recovered")
            canvas.draw()

def close(event):
    sys.exit()


def Update():
    cur.execute("SELECT * from India ORDER BY cases DESC LIMIT 1")
    response = requests.request("GET", url + "India", headers = headers, data = payload)
    data = response.json()
    for x in cur:
        if x[1] < data["cases"]:
            today = date.today()
            d  = today.strftime("%#m/%#d/%y")
            print(d)
            print(type(d))
            for country in countries[1:]:
                response2 = requests.request("GET", url + country, headers = headers, data = payload)
                data2 = response2.json()
                print(country)
                print(data2["cases"], data2["deaths"], data2["recovered"])
                cur.execute('''REPLACE INTO ''' + country + ''' (dat, cases, deaths, recovered) VALUES (?, ?, ?, ?)''', (d, data2["cases"], data2["deaths"], data2["recovered"]))

            conn.commit()


app = covid()
app.geometry("1200x620")
#app.resizable(False, False)
app.mainloop()