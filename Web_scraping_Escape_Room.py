
#Es recullen amb exit les següents informacions:
#   ESCAPE NAME
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
#
# Falta extreure:
#      la ubicació exacta (de moment sols esta la zona). A BCN per exemple surt la parada de metro mes propera, l'extreiem?
#      els tags de tipus de escape (Accio, terror, aventura...)
#      telefon del escape
#      email del escape
#      web del escape
#      Logo de la empresa del escape
#      Logo/Imatge del escape
#      Puntuacions detallades dels comentaris si estan disponibles
#
# També falta filtrar correctament les URLs del site-map ja que es colen algunes d'incorrectes
# El codi esta fatal, s'ha d'ordenar, crear funcions, afegir comentaris... Pero de funcionar funciona que ja es algo
# Al final falta tota la part de crear la base de dades, les dades que siguin intervals es podrien subdividir en 2 columnes (rang max i rang min...)
# Algunes sales al titol tenen "Proximamente", "Cerrada", "Cerrada temporalmente"... Aixo crec que sera interesant per crear una columna de datos amb el estat de la sala 0-Oberta, 1- Tancada, 2-Tancada temporalment, 2-Proxima obertura (i borrar la coletilla del titol)
# Si el codi acaba sortint massa facil crec que tocara fer la disponibilitat d'hores. Si aconseguim dominar la flecha de siguiente del calendari crec que es facil contar disponibilitats, aixo podria servir per avaluar la demanda de les sales.


import requests
from bs4 import BeautifulSoup
r =requests.get('https://www.escaperadar.com/sitemap.xml')
soup = BeautifulSoup(r.content)
h = 0
for link in soup.find_all('loc'):
    for child in link.children:   
        if "escaperadar.com/escape-room/" in child and h < 10:
        
            escapeName = " "
            companyName = " "
            locationZone = " "
            numberPlayers = " "
            timeRequired = " "
            aggregateOffer = " "
            difficultyLevel = " "
            peopleAudience = " "
            category = " "
            horror = "-"
            
            h = h + 1
            room =requests.get(child)
            roomSoup = BeautifulSoup(room.content)
            titleTag = roomSoup.find('h1')
            for child2 in titleTag.descendants:
                escapeName = child2
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
                itemprop = iTag.get("itemprop")
                iclass = iTag.get("class")
                                
                if ((itemprop is not None and itemprop == "numberOfPlayers") or (iclass is not None and len(iclass) >=2 and iclass[1] == "numberOfPlayers")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            numberPlayers = child3
                
                if ((itemprop is not None and itemprop == "timeRequired") or (iclass is not None and len(iclass) >=2 and iclass[1] == "timeRequired")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            timeRequired = child3
                if ((itemprop is not None and itemprop == "fa-euro-sign") or (iclass is not None and len(iclass) >=2 and iclass[1] == "fa-euro-sign")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            aggregateOffer = child3
                if ((itemprop is not None and itemprop == "fa-brain") or (iclass is not None and len(iclass) >=2 and iclass[1] == "fa-brain")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            difficultyLevel = child3
                if ((itemprop is not None and itemprop == "icon-people-white") or (iclass is not None and len(iclass) >=2 and iclass[1] == "icon-people-white")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            peopleAudience = child3
                if ((itemprop is not None and itemprop == "fa-tag") or (iclass is not None and len(iclass) >=2 and iclass[1] == "fa-tag")):
                    for child2 in iTag.parent.find_all("span"):
                        for child3 in child2.descendants:
                            category = child3
        
            print("ESCAPE NAME........"+escapeName)
            print("VALORACIO.........."+punctuation)
            print("TERROR............."+horror)
            print("COMPANY NAME......."+companyName)
            print("LOCATION ZONE......"+locationZone)
            print("NUMBER OF PLAYERS.."+numberPlayers)
            print("ESTIMATED TIME....."+timeRequired)
            print("PRICE RANGE........"+aggregateOffer)
            print("DIFFICULTY........."+difficultyLevel)
            print("YEARS.............."+peopleAudience)
            print("TAG................"+category)
            print("-----------------------------")
