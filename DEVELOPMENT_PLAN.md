# UFC Prediction Engine – kehityssuunnitelma

## Tavoite
Rakennetaan UFC-otteluiden voittotodennäköisyyksiä arvioiva ja historiallisesti testattava malli. Voittoja ei voida taata.

## Toteutusjärjestys
1. Lataa ja validoi historialliset ottelutiedot sekä kertoimet.
2. Muodosta ottelijakohtaiset ominaisuudet vain ennen ottelupäivää saatavilla olleista tiedoista; vältä tietovuoto ja ottelijoiden järjestykseen liittyvä harha.
3. Toteuta vertailutaso (markkinan marginaalista puhdistetut todennäköisyydet) ja ensimmäinen ennustemalli.
4. Testaa ajallisesti etenevällä erillisellä aineistolla ja arvioi kalibrointi, log loss sekä Brier-pisteet.
5. Lisää vain luotettavasti saatavilla olevat ennakko-ominaisuudet: KO/TKO-historia, palautumisaika, painonpudotus ja punnitusongelmat.
6. Laske historiallinen vedonlyöntituotto vain ennen ottelua saatavilla olleilla kertoimilla. Raportoi panostus, epävarmuus ja no-bet-tilanteet.
7. Tuota tulevien tapahtumien ennusteet aikaleimatuista lähtötiedoista.

## Nykytila
Tämä tiedosto vahvistaa GitHub-kirjoitusyhteyden. Varsinaista UFC-datalla koulutettua mallia tai todennettua historiallista tuottoa ei vielä ole tässä repositoriossa.
