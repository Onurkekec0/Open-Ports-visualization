import psycopg2
import requests
import json
import shodan
import csv
import pandas as pd
import folium
from bs4 import BeautifulSoup
import requests
sözlük_ulke_kıs = {}
sözlük_lat_long = {}
m = folium.Map(location=[38.963745, 35.243322], zoom_start=12)
port_ara=int(input("aranmasını istediğiniz port numarasını giriniz!"))
def sozluk_olustur():
   Web = requests.Session()
   site = Web.get("https://developers.google.com/public-data/docs/canonical/countries_csv")
   BS4 = BeautifulSoup(site.content, "html.parser")
   genel = BS4.find_all('td')
   a = 0
   kısalt_ilk, ulke_ilk = list(), list()
   lat_ilk, long_ilk = list(), list()

   for i in range(len(genel)):
      if (a == 4):
         a = 0
      if (a == 0):
         kısalt_ilk.append(str(genel[i]).split(">")[1].split("<")[0])
         a += 1
      elif (a == 1):
         lat_ilk.append(str(genel[i]).split(">")[1].split("<")[0])
         a += 1
      elif (a == 2):
         long_ilk.append(str(genel[i]).split(">")[1].split("<")[0])
         a += 1
      elif (a == 3):
         ulke_ilk.append(str(genel[i]).split(">")[1].split("<")[0])
         a += 1
   for i in range(len(kısalt_ilk)):
      sözlük_ulke_kıs[kısalt_ilk[i]] = ulke_ilk[i]
      sözlük_lat_long[kısalt_ilk[i]] = lat_ilk[i] + "/" + long_ilk[i]
sözlük_ulke_kıs["AX"]="Åland"
sözlük_lat_long["AX"]="52.5816/50.1840"
sözlük_ulke_kıs["SX"]="Saint Martin"
sözlük_lat_long["SX"]="30.9972/36.0036"
sözlük_ulke_kıs["CW"]="Cook Islands"
sözlük_lat_long["CW"]="-21.227169706727473/-159.7715380672931"
sözlük_ulke_kıs["MF"]="Sint Maarten"
sözlük_lat_long["MF"]="18.039711859207955/-63.05562335001955"
sözlük_ulke_kıs["SS"]="South Sudan"
sözlük_lat_long["SS"]="7.7205178066220626/29.77996549946886"
sözlük_ulke_kıs["BQ"]="Sint Eustatius"
sözlük_lat_long["BQ"]="17.488463808589845/-62.97632860492824"
sözlük_ulke_kıs["BL"]="Saint Barthélemy"
sözlük_lat_long["BL"]="17.899269565684502/-62.83385874874736"


def haritalastır(port, sayı, ülke,org_par,os_par,product_par,city_par,renk,icon):
   lat_long = str(sözlük_lat_long[ülke]).split("/")
   lat = float(lat_long[0])
   long = float(lat_long[1])
   tooltip = "click here"
   iframe = folium.IFrame("<h1><strong>{}</strong></h1><p><strong>{}</strong> adet <strong>{}</strong> numaralı portu açık, sunucu bulunmaktadır.<br/>"
                         "En çok kullanılan organizatör:<br/>"
                         "{}<br/>"
                          "En çok kullanılan işletim sistemi:<br/>"
                         "{}<br/>"
                         "En çok kullanılan ürün:<br/>"
                         "{}<br/>"
                         "En çok kullanan şehir<br/>"
                         "{}</p>"
         .format(
         sözlük_ulke_kıs[ülke], sayı, port,org_par,os_par,product_par,city_par))
   popup = folium.Popup(iframe,
                        min_width=300,
                        max_width=300)
   folium.Marker(
      [lat, long], popup=popup, tooltip=tooltip,icon=folium.Icon(color=renk,icon=icon)).add_to(m)
sozluk_olustur()
#shodan_id=shodan.Shodan("IwnQDI7fB6w1tAmOS2AnzShd58SOQ5no")
#id=1
renk = "darkgreen"
icon = "glyphicon glyphicon-ok"
for i in range(port_ara,port_ara+1):
    url1 = "https://api.shodan.io/shodan/host/count?key=IwnQDI7fB6w1tAmOS2AnzShd58SOQ5no&query=port:"+str(i)+"&facets=country:300"
    gönder1 = requests.get(url1)
    #burada gönderiyoruz
    json_format = gönder1.json()
    #burada json formatına çeviriyoruz
    list_bolumu=json_format["facets"]["country"]
    for a in list_bolumu:
        #burada tek tek alıyoruz
        org, os, product, city = "","","",""
        #bunlara en çok kullanılan org, os, product, city leri alıyoruz9
        #burada dikkat edilmesi gerekilen yer query kısmında birden fazla sorgu yazarken arada boşluk bırakıp yazıyoruz
        #örn port:11 country:TR
        #ama facets yazarken arada , olmalı örn org,os,product
        url2 = "https://api.shodan.io/shodan/host/count?key=IwnQDI7fB6w1tAmOS2AnzShd58SOQ5no&query=port:" + str(
         i) + " country:"+a["value"]+"&facets=org:1,os:1,product:1,city:1"
        gönder2 = requests.get(url2)
        detail_json = gönder2.json()
        try:
            #burada her ülke için ayrı ayrı sorgu yapıp org os product ve city leri alıyoruz
            detail_json_org = detail_json["facets"]["org"]
            org = detail_json_org[0]["value"] + "=" + str(detail_json_org[0]["count"]) + " adet"
        except:
            org = "yok"
            pass
        try:
            detail_json_os = detail_json["facets"]["os"]
            os = detail_json_os[0]["value"] + "=" + str(detail_json_os[0]["count"]) + " adet"
        except:
            os = "yok"
            pass
        try:
            detail_json_product = detail_json["facets"]["product"]
            product = detail_json_product[0]["value"] + "=" + str(detail_json_product[0]["count"]) + " adet"
        except:
            product = "yok"
            pass
        try:
            detail_json_city = detail_json["facets"]["city"]
            city=detail_json_city[0]["value"]+"="+str(detail_json_city[0]["count"])+" adet"
        except:
            city = "yok"
            pass
        if(a["count"]>100000):
            renk="darkred"
            icon="glyphicon glyphicon-fire"
        elif(50000<a["count"]<100000):
            renk="orange"
            icon="glyphicon glyphicon-warning-sign"
        haritalastır(str(i).strip(),str(a["count"]).strip(),str(a["value"]).strip(),org,os,product,city,renk,icon)
        renk = "darkgreen"
        icon="glyphicon glyphicon-ok"
        #burada tek tek ülkeleri haritamıza ekliyoruz
m.save('map-location.html')
