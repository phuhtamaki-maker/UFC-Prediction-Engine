# UFC Prediction Engine – kävelevä vuositestaus 2018–2026

Päiväys: 6.11.2026. [GitHub Actionsin onnistunut testi](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42292462540)

## Menetelmä

Jokaisena testivuonna malli koulutetaan vain sitä edellistä vuotta vanhemmilla otteluilla, ja todennäköisyyksien lämpötilakalibrointi tehdään vain edellisen vuoden otteluista. Testivuoden tuloksia ei käytetä saman vuoden ennusteen opettamiseen. Alkuperäinen historiallinen aineisto on [nlbair/ufc-data](https://github.com/nlbair/ufc-data), CC BY 4.0.

## Testin yksityiskohdat

| Testivuosi | Otteluita | Mallin osumatarkkuus | Markkinasuosikin osumatarkkuus* | Mallin väh. 70 % varmat: osumia / määrä | Simuloitu ROI |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2018 | 469 | 59,91 % | 64,96 % | 26/34 (76,47 %) | −8,03 % |
| 2019 | 506 | 56,13 % | 59,20 % | 25/40 (62,50 %) | +1,55 % |
| 2020 | 444 | 61,94 % | 64,71 % | 1/1 (100 %; **ei merkityksellinen yhden ottelun otos**) | −7,15 % |
| 2021 | 497 | 58,75 % | 61,34 % | 46/67 (68,66 %) | +2,06 % |
| 2022 | 506 | 60,47 % | 66,33 % | 29/38 (76,32 %) | −13,52 % |
| 2023 | 504 | 57,74 % | 65,79 % | 32/37 (86,49 %) | −1,29 % |
| 2024 | 513 | 57,70 % | 67,77 % | 47/59 (79,66 %) | −14,93 % |
| 2025 | 513 | 61,60 % | 66,73 % | 64/83 (77,11 %) | −5,48 % |
| 2026 (aineiston loppuun) | 435 | 64,60 % | 66,90 % | 67/87 (77,01 %) | +1,08 % |

*Markkinaluvuissa on vain ne ottelut, joista avauskertoimet olivat saatavilla, joten eri rivien malliprosentti ei ole täydellisen saman joukon vertailu. Tarkat paritetut vertailut ovat automaattisesti tallennetussa JSON-raportissa.*

## Yhteenveto kaikista vuosista

- **4 387** testattua ottelua.
- **2 622** oikein, eli yhteensä **59,77 %** mallin suosikkiarvioista.
- Vähintään **70 %** voittotodennäköisyyksiksi arvioiduista: **337/446 = 75,56 %**.
- Vahvojen arvioiden osuus kaikista otteluista oli noin **10,2 %**.
- Kuvaileva tasapanosten, +5 % oletetun laskennallisen edun vedonlyöntisimulaatio: **3 318 vetoa**, yhteensä noin **−169,604 yksikköä**, yhdistetty ROI noin **−5,11 %**.
- **80 prosentin luotettavaa yleistä tarkkuutta ei ole osoitettu.**
- Yksittäinen 2023 vuoden 86,49 %:n vahvojen suosikkien osumaosuus 37 ottelulla **ei** osoita 80 % suorituskykyä tulevaisuudessa.

## Rajoitukset

- Aiempien vuosien koulutusjaksot ovat päällekkäisiä: vuodet eivät ole toisistaan riippumattomia toistoja.
- Aineistossa olevat jälkikäteen korjatut tiedot eivät välttämättä vastaa täsmälleen ottelupäivänä tarjolla ollutta sisältöä.
- Avauskertoimet eivät välttämättä olleet historiallisesti lyötävissä ilmoitettuun hintaan.
- Malli ei vielä käytä luotettavasti kerättyä UFC:n ulkopuolista historiaa eikä vahvistettuja painonpudotus-/sairaus-/harjoitusleiriominaisuuksia numeerisesti.
- **Markkinavertailut ja ROI eivät osoita positiivista vedonlyöntietua.** Valikoitujen suosikkien osumatarkkuus ja kertoimiin suhteutettu etu ovat eri asioita.

## Päätös

Pidetään 80 %:n tavoite tutkimustavoitteena **vain, jos otteluiden kattavuus, epävarmuus ja aito ennakollisuus raportoidaan aina**. Seuraavaksi korjataan tunnistetut datan laatuongelmat, parannetaan historiallisten ennakkotietojen saatavuutta ja verrataan uusiin jaksoihin muuttamatta tavoitteita jälkikäteen.

Raaka raportti: GitHub Actions -ajon `ufc-walk-forward-research` -artifact, tiedosto `walk_forward.json`.
