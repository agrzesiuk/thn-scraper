"""
Projekt: Scraper portalu The Hacker News
Autor: Aleksandra Grzesiuk
Opis: Skrypt automatycznie pobiera nagłówki, kategorie i linki do artykułów,
      generuje statystyki oraz raport HTML.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import matplotlib.pyplot as plt
import time

#uruchomienie strony w przeglądarce
options = webdriver.EdgeOptions()
options.add_argument('--headless') #przeglądarka nie będzie wyświetlona
driver = webdriver.Edge(options=options)
driver.get("https://thehackernews.com/")
time.sleep(2)

#pobieranie listy naglowków
i=1
lista_newsow = []
licznik_kategorii = {}
while i<=10:
    try:
        strona=driver.find_elements(by=By.CLASS_NAME, value='story-link')
        time.sleep(1)
        #tworzenie listy elementow - slownikow - tytul kategoria link
        for news in strona:
            tytul = news.find_element(by=By.CLASS_NAME, value='home-title').text
            kat = news.find_element(by=By.CLASS_NAME, value='h-tags').get_attribute('textContent').strip()
            link = news.get_attribute('href')

            element = {
                'Tytul: ': tytul,
                'Kategoria: ': kat,
                'Link: ': link
            }
            lista_newsow.append(element)

            #liczenie wystąpienia kategorii
            kategorie = kat.split('/')
            for k in kategorie:
                k = k.strip()
                if k in licznik_kategorii:
                    licznik_kategorii[k] += 1
                else:
                    licznik_kategorii[k] = 1

        time.sleep(1)

        #przechodzenie na kolejną stroną
        next_page=driver.find_element(by=By.CLASS_NAME, value='blog-pager-older-link-mobile').get_attribute('href')
        driver.get(next_page)
        i=i+1


    except NoSuchElementException:
        print("wystapil blad lub zebrano wszystkie artykuly ze strony")
        break

driver.close()

#wypisanie podstawowych informacji
print(f'Dane zostały pobrane z {i-1} pierwszych stron.')
liczba_artykulow=len(lista_newsow)
print(f'Znaleziono {liczba_artykulow} newsów.')


#sortowanie słownika od największej wartości
posortowane_kategorie = {kategoria: wartosc for kategoria, wartosc in sorted(licznik_kategorii.items(), key=lambda item: item[1], reverse=True)}
print('Kategorie i liczba wystąpień: ')
print(posortowane_kategorie)

#pobieranie top 10 kategorii
top_10 = dict(list(posortowane_kategorie.items())[:10])

#zbior danych, odwrocenie list zeby najpopularniejsze byly na gorze wykresu
kategorie = (list(top_10.keys()))[::-1]
wartosci = (list(top_10.values()))[::-1]

#tworzy wykres poziomy top 10
plt.barh(kategorie, wartosci, color='skyblue')
plt.grid(axis='x', linestyle='--', alpha=0.7) #siatka
plt.title('TOP10 kategorii artykulow na The Hacker News')
plt.ylabel('kategorie')
plt.xlabel('wystapienia')
plt.tight_layout() #ladne marginesy, dostosowuje rozmieszczenie aby etykiety nie byly uciete itp
#plt.show()
plt.savefig('wykres.png')
plt.close()

#zbior danych top 5
top_5 = dict(list(posortowane_kategorie.items())[:5])
kategorie2=(list(top_5.keys()))
wartosci2 = (list(top_5.values()))

#tworzenie wykresu kolowego top 5
plt.pie(wartosci2, labels=kategorie2, autopct='%1.1f%%', colors=['#ff2083','#ff509d','#ff76b4','#ff9dc7','#ffd9ea'])
plt.title('Udział procentowy TOP 5 kategorii')
#plt.show()
plt.savefig('wykres_kolowy.png')
plt.close()


#funkcja piszaca kod html
def stworz_html(lista):
    najnowsze=lista[:10]
    top_kategoria=list(posortowane_kategorie.keys())[0]

    html=f'''<!DOCTYPE html>
    <html>
    <body>
    
        <h1>Analiza artykulow z The Hacker News</h1>
        
        <h2>1. Podsumowanie:</h2>
        <p>Analiza dotyczy artykulow znajdujacych sie na pierwszych {i-1} stronach.</p>
        <p>Liczba znalezionych atrykulow: {liczba_artykulow}.</p>
        <p>Najpopularniejsza kategoria to: {top_kategoria}.</p>
        
        <h3>2. Wykresy statystyk:</h3>
        <img src='wykres.png' />
        <img src='wykres_kolowy.png' />
        
        <h3>3. 10 Najnowszych artykulow:</h3>
        
        
    '''

    k=1
    for news in najnowsze:
        html+=f"<p>{k}. {news['Tytul: ']} <br> <a href={news['Link: ']}>Otworz artykul</a></p>"
        k+=1

    html+=f'<h3>4. Artykuly z najpopularniejszej kategorii - {top_kategoria}.</h3>'

    k=1
    for news in lista_newsow:
        if top_kategoria in news['Kategoria: ']:
            html+=f"<p>{k}. {news['Tytul: ']} <br> <a href={news['Link: ']}>Otworz artykul</a></p>"
            k+=1

    html += """
        </body>
        </html>
        """

    #zapisywanie pliku html
    with open("analiza.html", "w", encoding="utf-8") as plik:
        plik.write(html)

    print("Analiza HTML została zapisana jako analiza.html")

#uruchamianie funkcji
stworz_html(lista_newsow)

#mozna uruchomic funkcje aby kod byl interaktywny do szukania tytulow z danym slowem
def szukaj():
    slowo_klucz=input('Podaj słowo klucz, żeby wyświetlić związane z nim artykuły: ')
    j=1
    for news in lista_newsow:
        if slowo_klucz.lower() in news['Tytul: '].lower():
            print(f'{j}. {news['Tytul: ']}')
            j=j+1
        else:
            continue

#szukaj()




