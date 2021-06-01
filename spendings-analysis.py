import matplotlib.pyplot as plt
%matplotlib inline
import seaborn as sns
import numpy as np
import pandas as pd
import datetime
path = 'C:/Users/Jakob/Desktop/Diverses/Lebensstatistik/'

###Spendings Data
# split spendings data and fahrzeit data
data = pd.read_csv('spendings_data_2021.txt', sep=" ", header=None, names=["day", "date", "amount", "currency", "category", "item", "ext_1", "ext_2", "typ"], encoding='utf-8')
# add platzhalter "spendings" so the boxplot overlay doesn't skip categories
platzhalter = pd.read_csv('spendings_data_2021_platzhalter.txt', sep=" ", header=None, names=["day", "date", "amount", "currency", "category", "item", "ext_1", "ext_2", "typ"], encoding='utf-8')
platzhalter.amount = str('0')

for i in range(len(data)):
    if data.amount[i] == "RS-TW":
        data.typ[i] = "Fahrzeit"
    elif data.amount[i] == "TW-RS":
        data.typ[i] = "Fahrzeit"
    else:
        data.typ[i] = "Ausgabe"

spendings_data = data[data["typ"] == "Ausgabe"]
spendings_data = spendings_data.append(platzhalter)
spendings_data = spendings_data.reset_index()
fahrzeit_data = data[data["typ"] == "Fahrzeit"]
fahrzeit_data = fahrzeit_data.reset_index()


for i in range(len(spendings_data)):
    date = str(spendings_data.date[i]) + '2021'
    spendings_data.date[i] = datetime.datetime.strptime(date, '%d.%m.%Y')
    spendings_data.amount[i] = float(spendings_data.amount[i].replace(",","."))


spendings_data['month'] = spendings_data['date'].dt.month_name()

###Create Summaries
# create summary down to item including months
spendings_summary_month_item = spendings_data.groupby(['category', 'month', 'item'])['amount'].sum()
spendings_summary_month_item = spendings_summary_month_item.to_frame()
spendings_summary_month_item = spendings_summary_month_item.reset_index()

# create summary down to category level including months
spendings_summary_month_category = spendings_data.groupby(['category', 'month'])['amount'].sum()
spendings_summary_month_category = spendings_summary_month_category.to_frame()
spendings_summary_month_category = spendings_summary_month_category.reset_index()


# create summary down to item excluding months
spendings_summary_nomonth_item = spendings_data.groupby(['category', 'item'])['amount'].sum()
spendings_summary_nomonth_item = spendings_summary_nomonth_item.to_frame()
spendings_summary_nomonth_item = spendings_summary_nomonth_item.reset_index()

# create summary down to category level excluding months
spendings_summary_nomonth_category = spendings_data.groupby(['category'])['amount'].sum()
spendings_summary_nomonth_category = spendings_summary_nomonth_category.to_frame()
spendings_summary_nomonth_category = spendings_summary_nomonth_category.reset_index()


# create filter for less important spending categories and also the current month
ausgefiltert = 'category != "Andere" & category != "Aussehen" & category != "Beneto" & category != "Dokumente" & category != "Ersatz" & category != "Freizeit" & category != "Gesundheit" & category != "Hobby"'

### Pie-Plot for Total Spendings
# prepare imput data
# all time, all categories
temp = spendings_summary_nomonth_category
# all time, all items of specific category
#temp = spendings_summary_nomonth_item.query('category == "Konsum"')

labels = temp['category'] # for item change to 'item'
values = temp['amount']

# function for the label inside the pie - show amount in money and percent (for just % use autopct="%.1f%%")
def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{v:d} €'.format(v=val) # for both amount and percent replace this line with >return '{p:.2f}%  ({v:d} €)'.format(p=pct,v=val)
    return my_autopct

# plot Pie (Matplotlib)
pie, ax = plt.subplots(figsize=[20,12])
plt.pie(x=values, autopct=make_autopct(values), explode=[0.05]*len(labels), labels=labels, pctdistance=0.5, shadow = False, labeldistance = 1.1)
plt.title("Ausgaben Gesamt Jan-Mai 2021", fontsize=14, weight='bold', color = 'black')
plt.show()
#pie.savefig("ausgaben_kuchen_gesamt_2021.png")

###Boxplot for Median Spendings
# prepare input data
# all time, all months, largest categories
#temp = spendings_summary_month_category.query('month != "June" & ' + ausgefiltert)
# all time, all months, all categories
temp = spendings_summary_month_category.query('month != "June"') # all categories
# last month, largest categories
#temp_lastmonth = spendings_summary_month_category.query('month == "May" & ' + ausgefiltert) # just last Month
# last month, all categories
temp_lastmonth = spendings_summary_month_category.query('month == "May"') # just last Month


# Boxplot der Durchschnittsausgaben
box = sns.boxplot(y='amount', x='category',
                 data=temp,
                 palette="Pastel1")
box.set(xlabel='Kategorie', ylabel='monatliche Ausgaben in €', title = "Vergleich Ausgaben Mai (rot) zu Jan-Mai")


# Marker setzen, wie die Ausgaben im letzten Monat waren
box = sns.stripplot(y='amount', x='category',
                 data=temp_lastmonth,
                   jitter=False,
                   marker='.',
                   size = 10,
                   alpha=1,
                   color='red'
                   )
box.set(xlabel='Kategorie', ylabel='monatliche Ausgaben in €', title = "Vergleich Ausgaben Mai (rot) zu Jan-Mai")
# IMPORTANT: This Plot-Overlay only works because of "Platzhalter-Ausgaben" of 0 € every month. If one category is not featured in the most recent month, it fucks up the overlay.

#box.figure.savefig("ausgaben_boxplot_ausgewählt_2021.png")

###Barplot for Total Spendings over Months
# prepare input data
# all time, all months, largest categories
temp = spendings_summary_month_category.query('month != "June" & ' + ausgefiltert)



# Draw a nested barplot by species and sex
bar = sns.catplot(
    data=temp, kind="bar",
    x="month", y="amount", hue="category",
    ci="sd", palette="colorblind", alpha=.6, height=6,
    order=["January", "February", "March", "April", "May"]
)
bar.despine(left=True)
bar.set(xlabel='', ylabel='Ausgaben in €', title = "Hauptausgaben 2021 pro Monat")
#bar.savefig("ausgaben_barplot_ausgewählt_monate.png")
