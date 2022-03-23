# *************************************************************************
# *  Universitat Oberta de Catalunya                                      *
# *  Master de Data Science                                               *
# *  Tipologia i cicle de vida de les dades - Pràctica 1                  *
# *                                                                       *
# *        W E B   S C R A P I N G   D E   E S C A P E   R A D A R        *
# *                                                                       *
# *  Autors:                                                              *
# *   Jordi Bellciure Figueras                                            *
# *   Xenia Casanovas Díez                                                *
# *************************************************************************                                                                      

import pandas as pd
import re
import sys
import time
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
import datetime
from dateutil.relativedelta import relativedelta

escapeRoomDf = pd.DataFrame(columns=['id','name','punctuation','companyName','locZone','nPlayers','timelapse','lowPrice','highPrice','difLevel','audience','category','horror','address','genre','subtype','public','pregnant','english','funcDiversity','claustrofobia','ptsComenGen','ptsComenAmbi','ptsComenEnig','ptsComenInm','ptsComenHorror','availableTimes','unavailableTimes','companyAddress','companyPhone','companyEmail','companyWeb','state'])


# Funció que s'encarrega de fer la crida a les URLs.
#  Realitza reintents separats per 5 segons que van incrementant de 5 en 5.
#  Si s'arriba a un temps de 10 minuts entre intents i segueix donant error aborta el script
def requestWebPage(url,headers):
    status = 0
    tries = 0
    while status != 200:
        r =requests.get(url,headers = headers)
        status = r.status_code
        if(status != 200 and tries >= 600):
            print("Status Code: "+str(status))
            print("Execution aborted (Number of tries :"+str(tries)+")")
            sys.exit()
        if(status != 200):
            print("Status Code: "+str(status))
            tries = tries + 5
            time.sleep(tries)
    return r

# Funció per extreure informació emmagatzemada de forma similar al html
def buscarElement(iTag,tosearch,defValue,secondTag):
    toret = defValue
    itemprop = iTag.get("itemprop")
    iclass = iTag.get("class")
    if ((itemprop is not None and itemprop == tosearch) or (iclass is not None and len(iclass) >=2 and iclass[1] == tosearch)):
        for child2 in iTag.parent.find_all(secondTag):
            for child3 in child2.descendants:
                toret = child3
    return toret

# Eliminar duplicats d'una llista
def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

# Funció per analitzar i buscar possibles restriccions d'una escape room que s'emmagatzemen similar al html
def buscarRestriccions (iTag,defaultValue,locatedValue,actualValue,code):
    if (actualValue == defaultValue):
        iclass = iTag.get("class")
        if (iclass is not None and len(iclass) >=3 and iclass[0] == "mr-1" and iclass[1] == "fas" and iclass[2] == code):
            return  locatedValue
    return defaultValue
    
# Classe que emmagatzema les dades d'una sala d'Escape Room
class EscapeRoom:
    def __init__(self):
        self.id = -1
        self.name = " "
        self.punctuation = " "
        self.companyName = " "
        self.locZone = " "
        self.nPlayers = " "
        self.timelapse = " "
        self.lowPrice = -1
        self.highPrice = -1
        self.difLevel = " "
        self.audience = " "
        self.category = " "
        self.horror = "-"
        self.address = " "
        self.genre = [ ]
        self.subtype = [ ]
        self.public = [ ]
        self.pregnant = "SI"
        self.english = "NO"
        self.funcDiversity = "NO"
        self.claustrofobia = "SI"
        self.comentsPts = [-1,-1,-1,-1,-1]
        self.availableTimes = -1
        self.unavailableTimes = -1
        self.companyAddress = " "
        self.companyPhone = " "
        self.companyEmail = " "
        self.companyWeb = " "
        self.state = " "   
    
    def setPrice(self, price):
        price = price.replace('.','')
        price = price.replace(',','.')
        if ('-' in price):
            p = price.split('-')
            self.lowPrice  = float(p[0].strip())
            self.highPrice = float(p[1].strip())
        else:
            try:
                self.lowPrice = float(price.strip())
                self.highprice = float(price.strip())
            except:
                pass

    def addPublic(self,toadd):
        if(toadd is not None): 
            self.public.append(toadd)
            self.public = unique(self.public)
            
    def getPublic(self):
        if(len(self.public) == 0):
            return None
        else:
            return self.public
    
    def addGenre(self,toadd):
        if(toadd is not None): 
            self.genre.append(toadd)
            self.genre = unique(self.genre)
    
    def getGenre(self):
        if(len(self.genre) == 0):
            return None
        else:
            return self.genre

    def addSubtype(self,toadd):
        if(toadd is not None): 
            self.subtype.append(toadd)
            self.subtype = unique(self.subtype)
    
    def getSubType(self):
        if(len(self.subtype) == 0):
            return None
        else:
            return self.subtype
    
    def getPercAvailable(self):
        return round((self.availableTimes / (self.availableTimes + self.unavailableTimes))*100,2)
    
    def generateCSV(self):
        csv = str(self.id)
        csv = csv + ";" + self.name
        csv = csv + ";" + self.punctuation
        csv = csv + ";" + self.horror
        csv = csv + ";" + self.locZone
        csv = csv + ";" + self.address
        csv = csv + ";" + self.nPlayers
        csv = csv + ";" + self.timelapse
    
    def printEscapeRoom(self):
        print(" ")
        print(" < "+self.name+" > ")
        print(" ")
        print("  ID....................."+str(self.id))
        print("  Estat.................."+str(self.state))
        print("  Valoració.............."+self.punctuation)
        print("  Terror................."+self.horror)
        print("  Ciutat................."+self.locZone)
        print("  Adreça................."+self.address)
        print("  Numero de jugadors....."+self.nPlayers)
        print("  Temps estimat.........."+self.timelapse)
        print("  Rang de preu..........."+str(self.lowPrice)+"€ - "+str(self.highPrice)+"€")
        print("  Dificultat............."+self.difLevel)
        print("  Edats.................."+self.audience)
        print("  Públic objectiu........"+str(self.public))
        print("  Genere................."+str(", ".join(self.genre)))
        print("  Subtipus..............."+str(", ".join(self.subtype)))
        print("  Categories............."+self.category)
        print("  Embarassades..........."+self.pregnant)
        print("  Disponible anglès......"+self.english)
        print("  Adaptat div funcional.."+self.funcDiversity)
        print("  Apte claustrofòbics...."+self.claustrofobia)
        print("  VALORACIO DETALLADA")
        if (self.comentsPts[0] == -1):
            print ("    No Disponible")
        else:
            print("    Comentaris General..."+str(self.comentsPts[0]))
            print("    Comentaris Ambient..."+str(self.comentsPts[1]))
            print("    Comentaris Enigmas..."+str(self.comentsPts[2]))
            print("    Comentaris Inmersi..."+str(self.comentsPts[3]))
            print("    Comentaris Terror...."+str(self.comentsPts[4]))
        print("  DISPONIBILITATS")
        if (self.availableTimes == -1):
            print ("    No Disponible")
        else:
            print("    Hores disponibles...."+str(self.availableTimes))
            print("    Hores ocupades......."+str(self.unavailableTimes))
            print("    Hores totals........."+str(self.availableTimes+self.unavailableTimes))
            print("    Percentatge Ocupades."+str(self.getPercAvailable())+" %")
        print("  INFORMACIÓ EMRPESA")
        print("    Nom.................."+self.companyName)
        print("    Adreça..............."+str(" ".join(self.companyAddress)))
        print("    Telefon.............."+str(" ".join(self.companyPhone)))
        print("    E-mail..............."+str(" ".join(self.companyEmail)))
        print("    Pàgina web..........."+str(" ".join(self.companyWeb)))
        print(" ")
        print(" ")

# Estructura amb que emmagatzema totes les sales de Escape Room
class EscapeRoomList:
    def __init__(self):
        self.escapeRoomList = [ ]
        self.nEscapes = 0
        
    def addEscape(self,toadd):
        self.escapeRoomList.append(toadd)
        self.nEscapes = self.nEscapes + 1
        
    def printAll(self):
        for escape in self.escapeRoomList:
            escape.printEscapeRoom()
    
    def getNextId(self):
        return self.nEscapes
            

print("*************************************************************************")
print("*  Universitat Oberta de Catalunya                                      *")
print("*  Master de Data Science                                               *")
print("*  Tipologia i cicle de vida de les dades - Pràctica 1                  *")
print("*                                                                       *")
print("*        W E B   S C R A P I N G   D E   E S C A P E   R A D A R        *")
print("*                                                                       *")
print("*  Autors:                                                              *")
print("*   Jordi Bellciure Figueras                                            *")
print("*   Xenia Casanovas Díez                                                *")
print("*************************************************************************")
print("                                                                         ")

# URLs de partida
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
r = requestWebPage(url_sitemap, headers)
soup = BeautifulSoup(r.content)
escapeRoomList = EscapeRoomList()

# Indicates the number of Escapes Rooms that are going to be collected. -1 to set to All
nEscapes = 50

if( nEscapes > 0 ):
    print("WARNING")
    print("   The max number of escape rooms to retrieve is limitet to "+ str(nEscapes))
    print(" ")
    
for link in soup.find_all('loc'):
    for roomUrl in link.children:   
        if "escaperadar.com/escape-room/" in roomUrl and nEscapes >= 0:
        #if "www.escaperadar.com/escape-room/granollers-experience/bandidos" in roomUrl and h < 19:
            
            escapeRoom = EscapeRoom()
            companyInfo = [ ]
            companyInfo2 = [ ]
            
            room = requestWebPage(roomUrl, headers)
            
            nEscapes = nEscapes - 1
            
            roomSoup = BeautifulSoup(room.content)
            titleTag = roomSoup.find('h1')

            escapeRoom.id = escapeRoomList.getNextId()

            # Hi he afegit aquesta condició perquè he vist que és el que feia que fallés a vegades. Retorna algunes pàgines que
            # llegeix com una sala però queno tenen nom definit ni info. D'aquesta manera retorna únicament els que tenen valor a h1.
            if(titleTag is not None):
                for child2 in titleTag.descendants:
                    escapeNameFull = child2

                    escapeRoom.name = re.sub("[\(\[].*?[\)\]]", "", escapeNameFull)
                    
                    states = re.search(r'\((.*?)\)', escapeNameFull)
                    
                    if (states is not None):
                        escapeRoom.state = states.group(1)
                    else:
                        escapeRoom.state = "Oberta"

            # Look for Escape Name and the zone where is located which are inside an "a" tag
            companyTag = roomSoup.find_all('a')
            for child2 in companyTag:
                v = child2.get("class")
                if v is not None:
                    for c in v:
                        if c == "company-name":
                            for child3 in child2.descendants:
                                escapeRoom.companyName = child3
                        if c == "location-link":
                            for child3 in child2.descendants:
                                escapeRoom.locZone = child3
            
            # Search for the punctuation and horror
            spanTags = roomSoup.find_all('span')
            for spanTag in spanTags:
                spanTagTitle = spanTag.get("title")
                if spanTagTitle == "Puntuación de usuarios Escape Radar":
                    for child3 in spanTag.descendants:
                        escapeRoom.punctuation = child3.replace(',','.')
                if spanTagTitle == "Puntuación terror":
                    for child3 in spanTag.descendants:
                        escapeRoom.horror = child3
            
            iTags = roomSoup.find_all('i')
            for iTag in iTags:
                if (escapeRoom.nPlayers == " "):   escapeRoom.nPlayers   = buscarElement(iTag,"numberOfPlayers"," ","span")
                if (escapeRoom.timelapse == " "):  escapeRoom.timelapse  = buscarElement(iTag,"timeRequired"," ","span")
                if (escapeRoom.lowPrice == -1): escapeRoom.setPrice(buscarElement(iTag,"fa-euro-sign"," ","span"))
                if (escapeRoom.difLevel == " "):   escapeRoom.difLevel   = buscarElement(iTag,"fa-brain"," ","span")
                if (escapeRoom.audience == " "):   escapeRoom.audience   = buscarElement(iTag,"icon-people-white"," ","span")  
                if (escapeRoom.category == " "):   escapeRoom.category   = buscarElement(iTag,"fa-tag"," ","span")
                if (escapeRoom.address == " "):    escapeRoom.address    = buscarElement(iTag,"fa-map-marker-alt"," ","a")
                
                escapeRoom.pregnant = buscarRestriccions (iTag,"SI","NO",escapeRoom.pregnant,"fa-female")
                escapeRoom.english = buscarRestriccions (iTag,"NO","SI",escapeRoom.english,"fa-globe")
                escapeRoom.funcDiversity = buscarRestriccions (iTag,"NO","SI",escapeRoom.funcDiversity,"fa-wheelchair")
                escapeRoom.claustrofobia = buscarRestriccions (iTag,"SI","NO",escapeRoom.claustrofobia,"fa-exclamation-circle")
                           
            # Search for the coments punctuations
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
                                            escapeRoom.comentsPts[pos] = float(str(child3))
                                            pos = pos + 1
                                        if("." in str(child3)):
                                            escapeRoom.comentsPts[pos-1] = escapeRoom.comentsPts[pos-1] + float(str(child3))
                                except ValueError:
                                    pass
                
                # Search for available and unavailable time slots
                
                if(divClass is not None and divClass[0] == "table-responsive" and divId is not None and divId == "week"):
                    escapeRoom.availableTimes = 0
                    escapeRoom.unavailableTimes = 0
                    trTags = divTag.find_all('tr')
                    for trTag in trTags:
                        date_formated = datetime.datetime.now().strftime("%d/%m/%Y")
                        if(not date_formated in str(trTag)):
                            escapeRoom.availableTimes = escapeRoom.availableTimes + str(trTag).count("btn available hour-block")
                            escapeRoom.unavailableTimes = escapeRoom.unavailableTimes + str(trTag).count("btn reserved disabled hour-disabled")
                
                
                for child2 in divTag.parent.find_all("span"):
                    divItemprop = child2.get("itemprop")
                    divClass = child2.get("class")
                    if ((divItemprop is not None and divItemprop == "genre") and (divClass is not None and len(divClass) >=2 and divClass[0] == "d-flex" and divClass[1] == "tag-name")):
                        for child3 in child2.descendants:
                            escapeRoom.addGenre(str(child3).strip())
                            
                    if (divClass is not None and len(divClass) >=3 and divClass[0] == "d-flex" and divClass[1] == "tag-name" and divClass[2] == "tag-type-1"):
                        for child3 in child2.descendants:
                            escapeRoom.addSubtype(str(child3).strip())
                            
                    if (divClass is not None and len(divClass) >=3 and divClass[0] == "d-flex" and divClass[1] == "tag-name" and divClass[2] == "tag-type-2"):
                        for child3 in child2.descendants:
                            escapeRoom.addPublic(str(child3).strip())
                            
                if(divId is not None and divId == "mobile-empresa"):
                    for child2 in divTag.parent.find_all("li"):
                        for child3 in child2.parent.find_all("p"):
                            pClass = child3.get("class")
                            pText = child3.get("text")
                            
                            if (pClass is None):

                                companyInfo.append(child3.text)
                                escapeRoom.companyAddress = unique(companyInfo[0:2])
                                escapeRoom.companyPhone = unique(companyInfo[-1:])
                                
                        for child3 in child2.parent.find_all("a"):
                            
                            companyInfo2.append(child3.text)
                                                      
                            if (len(companyInfo2) >3 ): 
                                                        
                                escapeRoom.companyEmail = unique(companyInfo2[0:1])
                                escapeRoom.companyWeb = unique(companyInfo2[-1:])
                            
                            else:
                                escapeRoom.companyEmail = unique(companyInfo2[0:2])
                                escapeRoom.companyWeb = "-"
            
            # Mostra el progres a la consola
            print(" <i> "+escapeRoom.name+" data has been retrieved <i>")
            escapeRoomList.addEscape(escapeRoom)
            


            escapeRoomDf['id'] = escapeRoom.id
            escapeRoomDf['name'] = escapeRoom.name
            escapeRoomDf['punctuation'] = escapeRoom.punctuation
            escapeRoomDf['companyName'] = escapeRoom.companyName
            escapeRoomDf['locZone'] = escapeRoom.locZone
            escapeRoomDf['nPlayers'] = escapeRoom.nPlayers
            escapeRoomDf['timelapse'] = escapeRoom.timelapse
            escapeRoomDf['lowPrice'] = escapeRoom.lowPrice
            escapeRoomDf['highPrice'] = escapeRoom.highPrice
            escapeRoomDf['difLevel'] = escapeRoom.difLevel
            escapeRoomDf['audience'] = escapeRoom.audience
            escapeRoomDf['category'] = escapeRoom.category
            escapeRoomDf['horror'] = escapeRoom.horror
            escapeRoomDf['address'] = escapeRoom.address
            escapeRoomDf['genre'] = pd.Series(escapeRoom.getGenre())
            escapeRoomDf['subtype'] = pd.Series(escapeRoom.getSubType())
            escapeRoomDf['public'] = pd.Series(escapeRoom.getPublic())
            escapeRoomDf['pregnant'] = escapeRoom.pregnant
            escapeRoomDf['english'] = escapeRoom.english
            escapeRoomDf['funcDiversity'] = escapeRoom.funcDiversity
            escapeRoomDf['claustrofobia'] = escapeRoom.claustrofobia
            escapeRoomDf['ptsComenGen'] = escapeRoom.comentsPts[0]
            escapeRoomDf['ptsComenAmbi'] = escapeRoom.comentsPts[1]
            escapeRoomDf['ptsComenEnig'] = escapeRoom.comentsPts[2]
            escapeRoomDf['ptsComenInm'] = escapeRoom.comentsPts[3]
            escapeRoomDf['ptsComenHorror'] = escapeRoom.comentsPts[4]
            escapeRoomDf['availableTimes'] = escapeRoom.availableTimes
            escapeRoomDf['unavailableTimes'] = escapeRoom.unavailableTimes
            escapeRoomDf['companyAddress'] = escapeRoom.companyAddress
            escapeRoomDf['companyPhone'] = pd.Series(escapeRoom.companyPhone)
            escapeRoomDf['companyEmail'] = pd.Series(escapeRoom.companyEmail)
            escapeRoomDf['companyWeb'] = pd.Series(escapeRoom.companyWeb)
            escapeRoomDf['state'] = pd.Series(escapeRoom.state)


# Imprimir totes les dades de les escapes rooms obtingudes. Comentar a la versio final
# escapeRoomList.printAll()

# Conversió de les dades recolectades a CSV i grabació al fitxer de sortida


# Tenim les dades guardades en una estructura sencilla.
#  - Hauriem de plantejar en quin format volem formatar el CSV de sortida
#  - Convertir la estructura a format CSV
#  - Gravar el fitxer CSV final


# Millores que podriem fer
#   - Descargar imatges de la pagina web
#   - Mirar la disponibilitat de més dies, no unicament els 6 dies següents

escapeRoomDf.head()