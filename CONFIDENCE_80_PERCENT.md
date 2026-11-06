# 80 prosentin ennustetarkkuuden tutkimus: 6.11.2026

## Oikean aineiston testiasetelma

Tämä on **jälkikäteen tarkasteltu ennustejoukon kuvaus**, ei näyttöä tulevasta tarkkuudesta tai vedonlyöntiedusta. Koulutus ennen vuotta 2024, kalibrointi vuoden 2024 validointijoukolla, testaus 948 myöhemmällä ottelulla. Malli on sama kuin aiemman raportin kalibroitu malli.

Testitapa: valitaan ottelu vain, jos mallin arvio suosikin voittotodennäköisyydestä on vähintään ennalta nimetyn tarkastelutason 60 %, 70 % tai 80 %. Nämä tasot ovat kuvailevia vertailuja, eivät testidatasta optimoitu panostusstrategia.

| Mallin vähimmäisvarmuus | Otteluita | Osuus kaikista 948 ottelusta | Oikein | Osumatarkkuus | Noin 95 % Wilson-väli |
| --- | ---: | ---: | ---: | ---: | ---: |
| 60 % | 476 | 50,21 % | 325 | 68,28 % | 63,96–72,30 % |
| 70 % | 156 | 16,46 % | 117 | 75,00 % | 67,66–81,14 % |
| 80 % | 24 | 2,53 % | 17 | 70,83 % | 50,83–85,09 % |

Markkinan avaushinnat olivat saatavilla valittujen otteluiden osajoukosta:
- 60 % -taso: sama 467 ottelua, mallin tarkkuus 68,74 %, markkinasuosikin 65,10 %.
- 70 % -taso: sama 150 ottelua, mallin tarkkuus 76,67 %, markkinasuosikin 70,67 %.
- 80 % -taso: sama 22 ottelua, molempien tarkkuus 72,73 %.

**Tulkinta:** 70 %:n tasolla 75 % osui oikein tässä historiallisessa otoksessa. Tämä ei osoita, että algoritmi saavuttaisi 80 prosentin tarkkuuden tulevaisuudessa; lisäksi valinta kattoi vain 16 % otteluista. Tuloksen tilastollinen epävarmuus on merkittävä, ja esimerkki 80 %:n varmuustasosta on erityisen pieni. Markkinasuosikin voittaminen tarkkuudessa ei yksin osoita kannattavaa vedonlyöntiä.

## Seuraavat toimet

1. Tarkista ottelijoiden tunnistaminen ja UFC:n ulkopuolisen historian puuttuminen; tämä voi aiheuttaa virheellistä varmuutta debytanttien arvioihin.
2. Kerää ja validoi ennakkoon saatavilla olleet ottelukohtaiset kertoimet sekä dokumentoidut painonpudotus-, loukkaantumis- ja valmistautumistiedot.
3. Toteuta useita peräkkäisiä aikajaksoja käyttävä ennakointitesti ja otteluvuosiin perustuva epävarmuusarvio.
4. Kalibroi todennäköisyydet myös vahvojen suosikkien osajoukossa (esimerkiksi 70+ prosenttia).
5. Pidä **kaikkien otteluiden tarkkuus**, **valittujen otteluiden kattavuus**, **markkinavertailu** sekä **ROI** erillisinä mittareina.
6. Älä valitse uusia panostussääntöjä 2025–2026 testijoukon tuloksia optimoimalla. Kehitä seuraavat muutokset aikaisemmalla opetus-/validointiaineistolla ja arvioi lopulta koskemattomalla uudella jaksolla.

GitHub Actions -testitulos: https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42291143860

## Keskeinen varoitus

Malli ei ole osoittanut positiivista historiallista vedonlyöntituottoa. Korkea osumatarkkuus vahvojen suosikkien osajoukossa voi tarkoittaa lähinnä matalia kertoimia eikä voitollista strategiaa. Kohteiden määrän ja epävarmuuden ilmoittaminen on siksi pakollista.
