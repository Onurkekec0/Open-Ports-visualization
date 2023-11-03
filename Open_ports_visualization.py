import psycopg2
import requests
import json
import shodan
import csv
import pandas as pd
import folium
from bs4 import BeautifulSoup
import requests

country_code_dictionary = {}
lat_long_dictionary = {}
m = folium.Map(location=[38.963745, 35.243322], zoom_start=12)

port_to_search = int(input("Please enter the port number you want to search for!"))

def create_dictionary():
    Web = requests.Session()
    site = Web.get("https://developers.google.com/public-data/docs/canonical/countries_csv")
    BS4 = BeautifulSoup(site.content, "html.parser")
    general = BS4.find_all('td')
    a = 0
    country_code_list, country_list = list(), list()
    lat_list, long_list = list(), list()

    for i in range(len(general)):
        if a == 4:
            a = 0
        if a == 0:
            country_code_list.append(str(general[i]).split(">")[1].split("<")[0])
            a += 1
        elif a == 1:
            lat_list.append(str(general[i]).split(">")[1].split("<")[0])
            a += 1
        elif a == 2:
            long_list.append(str(general[i]).split(">")[1].split("<")[0])
            a += 1
        elif a == 3:
            country_list.append(str(general[i]).split(">")[1].split("<")[0])
            a += 1
    for i in range(len(country_code_list)):
        country_code_dictionary[country_code_list[i]] = country_list[i]
        lat_long_dictionary[country_code_list[i]] = lat_list[i] + "/" + long_list[i]

# Country information that we couldn't retrieve automatically
country_code_dictionary["AX"] = "Åland"
lat_long_dictionary["AX"] = "52.5816/50.1840"
country_code_dictionary["SX"] = "Saint Martin"
lat_long_dictionary["SX"] = "30.9972/36.0036"
country_code_dictionary["CW"] = "Cook Islands"
lat_long_dictionary["CW"] = "-21.227169706727473/-159.7715380672931"
country_code_dictionary["MF"] = "Sint Maarten"
lat_long_dictionary["MF"] = "18.039711859207955/-63.05562335001955"
country_code_dictionary["SS"] = "South Sudan"
lat_long_dictionary["SS"] = "7.7205178066220626/29.77996549946886"
country_code_dictionary["BQ"] = "Sint Eustatius"
lat_long_dictionary["BQ"] = "17.488463808589845/-62.97632860492824"
country_code_dictionary["BL"] = "Saint Barthélemy"
lat_long_dictionary["BL"] = "17.899269565684502/-62.83385874874736"

def plot_on_map(port, count, country, org_param, os_param, product_param, city_param, color, icon):
    lat_long = str(lat_long_dictionary[country]).split("/")
    lat = float(lat_long[0])
    long = float(lat_long[1])
    tooltip = "click here"
    iframe = folium.IFrame("<h1><strong>{}</strong></h1><p><strong>{}</strong> open port(s) with number <strong>{}</strong> are available on the server.<br/>"
                           "Most used organizer:<br/>"
                           "{}<br/>"
                           "Most used operating system:<br/>"
                           "{}<br/>"
                           "Most used product:<br/>"
                           "{}<br/>"
                           "Most used city:<br/>"
                           "{}</p>"
                           .format(
        country_code_dictionary[country], count, port, org_param, os_param, product_param, city_param))
    popup = folium.Popup(iframe,
                        min_width=300,
                        max_width=300)
    folium.Marker(
        [lat, long], popup=popup, tooltip=tooltip, icon=folium.Icon(color=color, icon=icon)).add_to(m)

create_dictionary()
color = "darkgreen"
icon = "glyphicon glyphicon-ok"
for i in range(port_to_search, port_to_search + 1):
    url1 = "https://api.shodan.io/shodan/host/count?key=IwnQDI7fB6w1tAmOS2AnzShd58SOQ5no&query=port:" + str(i) + "&facets=country:300"
    response1 = requests.get(url1)
    json_format = response1.json()
    list_section = json_format["facets"]["country"]
    for a in list_section:
        org, os, product, city = "", "", "", ""
        url2 = "https://api.shodan.io/shodan/host/count?key=IwnQDI7fB6w1tAmOS2AnzShd58SOQ5no&query=port:" + str(
         i) + " country:" + a["value"]+"&facets=org:1,os:1,product:1,city:1"
        response2 = requests.get(url2)
        detail_json = response2.json()
        try:
            detail_json_org = detail_json["facets"]["org"]
            org = detail_json_org[0]["value"] + "=" + str(detail_json_org[0]["count"]) + " adet"
        except:
            org = "N/A"
            pass
        try:
            detail_json_os = detail_json["facets"]["os"]
            os = detail_json_os[0]["value"] + "=" + str(detail_json_os[0]["count"]) + " adet"
        except:
            os = "N/A"
            pass
        try:
            detail_json_product = detail_json["facets"]["product"]
            product = detail_json_product[0]["value"] + "=" + str(detail_json_product[0]["count"]) + " adet"
        except:
            product = "N/A"
            pass
        try:
            detail_json_city = detail_json["facets"]["city"]
            city = detail_json_city[0]["value"] + "=" + str(detail_json_city[0]["count"]) + " adet"
        except:
            city = "N/A"
            pass
        if a["count"] > 100000:
            color = "darkred"
            icon = "glyphicon glyphicon-fire"
        elif 50000 < a["count"] < 100000:
            color = "orange"
            icon = "glyphicon glyphicon-warning-sign"
        plot_on_map(str(i).strip(), str(a["count"]).strip(), str(a["value"]).strip(), org, os, product, city, color, icon)
        color = "darkgreen"
        icon = "glyphicon glyphicon-ok"

print("If the port count is greater than 100,000, it will be displayed in red.(Critic)")
print("If the port count is between 50,000 and 100,000, it will be displayed in orange.(Normal)")
print("If the port count is less than 50,000, it will be displayed in green.(Safe)")

m.save('map-location.html')
