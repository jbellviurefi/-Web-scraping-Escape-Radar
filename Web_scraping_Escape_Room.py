
#Es recullen amb exit les següents informacions:
#    ESCAPE NAME
#    VALORACIO
#    TERROR
#    COMPANY NAME
#    LOCATION ZONE
#    NUMBER OF PLAYERS
#    ESTIMATED TIME
#    PRICE RANGE
#    DIFFICULTY
#    YEARS
#    TAG
#    Notes dels comentaris quan estan disponibles
#    ADDRESS
#    GENRE
#    SUBTYPE
#    PUBLIC
#    APTE EMBARASSADES
#    ANGLÈS
#    ADAPTAT DIVERSITAT FUNCIONAL
#    APTE CLAUSTROFÒBICS
#    COMPANY ADDRESS
#    COMPANY PHONE
#    COMPANY EMAIL
#    COMPANY WEB
#    ROOM STATE
#
# Falta extreure:
#      Logo de la empresa del escape
#      Logo/Imatge del escape
#
# També falta filtrar correctament les URLs del site-map ja que es colen algunes d'incorrectes.
#       XÈNIA: Crec que ho he arreglat una mica amb un condicional que hi he afegit al veure que retornava pàgines en blanc.
# Al final falta tota la part de crear la base de dades, les dades que siguin intervals es podrien subdividir en 2 columnes (rang max i rang min...)
# Algunes sales al titol tenen "Proximamente", "Cerrada", "Cerrada temporalmente"... Aixo crec que sera interesant per crear una columna de datos amb el estat de la sala 0-Oberta, 1- Tancada, 2-Tancada temporalment, 2-Proxima obertura (i borrar la coletilla del titol)
#       XÈNIA: Ho he aconseguit treure del títol. Quan ho tinguem en un dataset podrem extreure els valors únics i substituïr-los pel que vulguem.
# Si el codi acaba sortint massa facil crec que tocara fer la disponibilitat d'hores. Si aconseguim dominar la flecha de siguiente del calendari crec que es facil contar disponibilitats, aixo podria servir per avaluar la demanda de les sales.
# Afegir wait times entre consultes si el status code no es correcte (temps exponencial d'espera)
#
# Xenia
#   - Etiquetes cadira rodes, claustrofobia i angles (i si trobesim algun mes). FET. En principi he trobat aquests tres. Potser quan traiem totes les dades n'apareix algun más. 
#   - Dades d'empreses. FET.
#   - Extreure els estats tipus "(CERRADO)" del nom de la sala i guardar-los en una nova variable. FET.
#   - Si hi ha temps el Pandas per guardar les coses. M'HO GUARDO PER MIRAR LA SETMANA QUE VE.
#
# Jordi
#   - Intentar contar hores lliures de la taula de disponibilitats
#   - Intentar afegir Wait times entre consultes
#

import re
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.relativedelta import relativedelta

def buscarElement(iTag,tosearch,defValue):
    toret = defValue
    itemprop = iTag.get("itemprop")
    iclass = iTag.get("class")
    if ((itemprop is not None and itemprop == tosearch) or (iclass is not None and len(iclass) >=2 and iclass[1] == tosearch)):
        for child2 in iTag.parent.find_all("span"):
            for child3 in child2.descendants:
                toret = child3
    return toret

def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list
    
    
url = 'https://www.escaperadar.com'
url_sitemap = url + '/sitemap.xml'
url_robots = url + '/robots.txt'

rp = urllib.robotparser.RobotFileParser()
rp.set_url(url_robots)
rp.read()
print(rp)

headers = {
    'User-Agent': 'UOC 1.0',
}


r =requests.get(url_sitemap, headers = headers)
print(r.status_code)
soup = BeautifulSoup(r.content)
h = 0
for link in soup.find_all('loc'):
    for child in link.children:   
        #if "escaperadar.com/escape-room/" in child and h < 19:
        if "www.escaperadar.com/escape-room/granollers-experience/bandidos" in child and h < 19:
            
            
            escapeName = " "
            punctuation = " "
            companyName = " "
            locationZone = " "
            numberPlayers = " "
            timeRequired = " "
            aggregateOffer = " "
            difficultyLevel = " "
            peopleAudience = " "
            category = " "
            horror = "-"
            address = " "
            genre = [ ]
            subtype = [ ]
            public = [ ]
            language = [ ]
            embarassades = "SI"
            angles = "NO"
            diversitatFuncional = "NO"
            claustrofobia = "SI"
            comentsPts = [-1,-1,-1,-1,-1]
            disponibles = -1
            ocupades = -1
            companyInformation = [ ]
            companyInformation2 = [ ]
            companyAddress = " "
            companyPhone = " "
            companyEmail = " "
            companyWeb = " "
            state = " "
            
            h = h + 1
            room =requests.get(child)
            roomSoup = BeautifulSoup(room.content)
            titleTag = roomSoup.find('h1')

            # Hi he afegit aquesta condició perquè he vist que és el que feia que fallés a vegades. Retorna algunes pàgines que
            # llegeix com una sala però queno tenen nom definit ni info. D'aquesta manera retorna únicament els que tenen valor a h1.
            if(titleTag is not None):
                for child2 in titleTag.descendants:
                    escapeNameFull = child2

                    escapeName = re.sub("[\(\[].*?[\)\]]", "", escapeNameFull)
                    
                    state = re.search(r'\((.*?)\)', escapeNameFull)
                    
                    if (state is not None):
                        state = state.group(1)
                    else:
                        state = "-"

            companyTag = roomSoup.find_all('a')
            for child2 in companyTag:
                v = child2.get("class")
                if v is not None:
                    for c in v:
                        if c == "company-name":
                            for child3 in child2.descendants:
                                companyName = child3
                        if c == "location-link":
                            for child3 in child2.descendants:
                                locationZone = child3
            spanTags = roomSoup.find_all('span')
            for spanTag in spanTags:
                spanTagTitle = spanTag.get("title")
                if spanTagTitle == "Puntuación de usuarios Escape Radar":
                    for child3 in spanTag.descendants:
                        punctuation = child3
                if spanTagTitle == "Puntuación terror":
                    for child3 in spanTag.descendants:
                        horror = child3
            iTags = roomSoup.find_all('i')
            for iTag in iTags:
                if (numberPlayers == " "): numberPlayers = buscarElement(iTag,"numberOfPlayers"," ")
                if (timeRequired == " "): timeRequired = buscarElement(iTag,"timeRequired"," ")
                if (aggregateOffer == " "): aggregateOffer = buscarElement(iTag,"fa-euro-sign"," ")    
                if (difficultyLevel == " "): difficultyLevel = buscarElement(iTag,"fa-brain"," ")
                if (peopleAudience == " "): peopleAudience = buscarElement(iTag,"icon-people-white"," ")  
                if (category == " "): category = buscarElement(iTag,"fa-tag"," ")  
                
                if (category == " "): category = buscarElement(iTag,"fa-tag"," ")  
                
                if (embarassades == "SI"):
                    iclass = iTag.get("class")
                    if (iclass is not None and len(iclass) >=3 and iclass[0] == "mr-1" and iclass[1] == "fas" and iclass[2] == "fa-female"):
                        embarassades = "NO" 

                if (angles == "NO"):
                    iclass = iTag.get("class")
                    if (iclass is not None and len(iclass) >=3 and iclass[0] == "mr-1" and iclass[1] == "fas" and iclass[2] == "fa-globe"):
                        angles = "SI"
                        
                if (diversitatFuncional == "NO"):
                    iclass = iTag.get("class")
                    if (iclass is not None and len(iclass) >=3 and iclass[0] == "mr-1" and iclass[1] == "fas" and iclass[2] == "fa-wheelchair"):
                        diversitatFuncional = "SI"
                        
                if (claustrofobia == "SI"):
                    iclass = iTag.get("class")
                    if (iclass is not None and len(iclass) >=3 and iclass[0] == "mr-1" and iclass[1] == "fas" and iclass[2] == "fa-exclamation-circle"):
                        claustrofobia = "NO" 

                iclass = iTag.get("class")
                itemprop = iTag.get("itemprop")
                if ((itemprop is not None and itemprop == "fa-map-marker-alt") or (iclass is not None and len(iclass) >=2 and iclass[1] == "fa-map-marker-alt")):
                    for child2 in iTag.parent.find_all("a"):
                        for child3 in child2.descendants:
                            address = child3  
                       
            divTags = roomSoup.find_all('div')
            for divTag in divTags:
                divClass = divTag.get("class")
                divId = divTag.get("id")
                if(divClass is not None and len(divClass) >=2 and divClass[0] == "row" and divClass[1] == "box-puntuacio"):
                    pos = 0
                    for p in divTag.find_all('p'):
                        if(p.get("class") is not None and len(p.get("class")) >= 1 and p.get("class")[0] == "txt_puntuacion"):
                            for child3 in p.descendants:
                                try:
                                    if(pos < 5):
                                        if(not "." in str(child3)):
                                            comentsPts[pos] = float(str(child3))
                                            pos = pos + 1
                                        if("." in str(child3)):
                                            comentsPts[pos-1] = comentsPts[pos-1] + float(str(child3))
                                except ValueError:
                                    pass
                
                if(divClass is not None and divClass[0] == "table-responsive" and divId is not None and divId == "week"):
                    disponibles = 0
                    ocupades = 0
                    trTags = divTag.find_all('tr')
                    for trTag in trTags:
                        date_formated = datetime.datetime.now().strftime("%d/%m/%Y")
                        if(not date_formated in str(trTag)):
                            print("Not avui")
                            disponibles = disponibles + str(trTag).count("btn available hour-block")
                            ocupades = ocupades + str(trTag).count("btn reserved disabled hour-disabled")
                    
                for child2 in divTag.parent.find_all("span"):
                    divItemprop = child2.get("itemprop")
                    divClass = child2.get("class")
                    if ((divItemprop is not None and divItemprop == "genre") and (divClass is not None and len(divClass) >=2 and divClass[0] == "d-flex" and divClass[1] == "tag-name")):
                        for child3 in child2.descendants:
                            genre.append(str(child3).strip())
                            
                    if (divClass is not None and len(divClass) >=3 and divClass[0] == "d-flex" and divClass[1] == "tag-name" and divClass[2] == "tag-type-1"):
                        for child3 in child2.descendants:
                            subtype.append(str(child3).strip())
                            
                    if (divClass is not None and len(divClass) >=3 and divClass[0] == "d-flex" and divClass[1] == "tag-name" and divClass[2] == "tag-type-2"):
                        for child3 in child2.descendants:
                            public.append(str(child3).strip())
                            
                if(divId is not None and divId == "mobile-empresa"):
                    for child2 in divTag.parent.find_all("li"):
                        for child3 in child2.parent.find_all("p"):
                            pClass = child3.get("class")
                            pText = child3.get("text")
                            
                            if (pClass is None):

                                companyInformation.append(child3.text)
                                
                                companyAddress = unique(companyInformation[0:2])
                                companyPhone = unique(companyInformation[-1:])
                                
                        for child3 in child2.parent.find_all("a"):
                            
                            companyInformation2.append(child3.text)
                                                      
                            if (len(companyInformation2) >3 ): 
                                                        
                                companyEmail = unique(companyInformation2[0:1])
                                companyWeb = unique(companyInformation2[-1:])
                            
                            else:
                                companyEmail = unique(companyInformation2[0:2])
                                companyWeb = "-"
            
                 
            print("ESCAPE NAME............"+escapeName)
            print("ROOM STATE............."+str(state))
            print("VALORACIO.............."+punctuation)
            print("TERROR................."+horror)
            print("COMPANY NAME..........."+companyName)
            print("COMPANY ADDRESS........"+str(" ".join(companyAddress)))
            print("COMPANY PHONE.........."+str(" ".join(companyPhone)))
            print("COMPANY EMAIL.........."+str(" ".join(companyEmail)))
            print("COMPANY WEB............"+str(" ".join(companyWeb)))
            print("LOCATION ZONE.........."+locationZone)
            print("NUMBER OF PLAYERS......"+numberPlayers)
            print("ESTIMATED TIME........."+timeRequired)
            print("PRICE RANGE............"+aggregateOffer)
            print("DIFFICULTY............."+difficultyLevel)
            print("YEARS.................."+peopleAudience)
            print("TAG...................."+category)
            print("ADDRESS................"+address)
            print("GENRE.................."+str(", ".join(unique(genre))))
            print("SUBTYPE................"+str(", ".join(unique(subtype))))
            print("PUBLIC................."+str(", ".join(unique(public))))
            print("Embarassades..........."+embarassades)
            print("Disponible anglès......"+angles)
            print("Adaptat div funcional.."+diversitatFuncional)
            print("Apte claustrofòbics...."+claustrofobia)
            print("Comentaris General....."+str(comentsPts[0]))
            print("Comentaris Ambient....."+str(comentsPts[1]))
            print("Comentaris Enigmas....."+str(comentsPts[2]))
            print("Comentaris Inmersi....."+str(comentsPts[3]))
            print("Comentaris Terror......"+str(comentsPts[4]))
            print("Hores disponibles......"+str(disponibles))
            print("Hores ocupades........."+str(ocupades))
            print("Hores totals..........."+str(disponibles+ocupades))
            print("Percentatge Ocupades..."+str(round((ocupades/(disponibles+ocupades))*100,2))+" %")
            print("-----------------------------")
