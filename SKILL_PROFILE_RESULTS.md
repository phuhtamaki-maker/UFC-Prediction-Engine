# UFC taitoprofiilikoe – 6.11.2026

## Tutkimuskysymys

Parantaako ennen ottelua saatavilla olleiden lyönti- ja painitilastojen historiallinen kooste ennusteita verrattuna aiempaan kymmenen muuttujan malliin?

**Tutkimuskoodi:** `skill_features.py` (profiilit), `skill_profile_experiment.py` (erillinen vertailu). Tuotantopolku `predict.py` käyttää yhä **kymmenen muuttujan perustasoa**.

## Mitä lisättiin?

Kunkin ottelijan jo päättyneistä UFC-otteluista laskettu:
- Merkittävien osumien määrä / minuutti.
- Vastustajan merkittävien lyöntien torjunnan osuus.
- Onnistuneet alasviennit / 15 minuuttia.
- Vastustajan alasvientiyritysten torjunnan osuus.

Pienillä näytemäärillä käytetään ennalta määriteltyjä tasoittavia lähtöarvoja. Puuttuvia ottelutilastoja ei tulkita automaattisesti nollasuorituksiksi. Saman päivän ottelut eivät saa toistensa tulostietoja.

## Rehellinen, kronologinen testiasetelma

2018–2026, **9 erillistä vuosikohtaista testijaksoa**, yhteensä **4 387** ratkaistua ottelua. Kunkin testivuoden oppiminen päättyy ennen edellistä vuotta; edellinen vuosi käytetään vain kalibrointiin. Molempia malleja arvioitiin täsmälleen samoilla otteluilla.

| Mittari | Perusmalli (10 muuttujaa) | Taitoprofiilimalli (14 muuttujaa) |
| --- | ---: | ---: |
| Voittajat oikein | 2 622 / 4 387 = **59,77 %** | 2 653 / 4 387 = **60,47 %** |
| Brier, pienempi parempi | 0,23692 | **0,23385** |
| Vähintään 70 % arviot: osumat | **337 / 446 = 75,56 %** | 455 / 609 = **74,71 %** |
| Vähintään 70 % arvioiden osuus kaikista otteluista | 10,17 % | 13,88 % |
| Simuloituja tasapanosvetoja | 3 318 | 3 262 |
| Historiallinen voittotappio yksiköissä | −169,604 | −110,407 |
| Historiallinen ROI | −5,11 % | −3,38 % |

### Vuosittaista vaihtelua

| Vuosi | Perusmalli | Taitoprofiilimalli |
| --- | ---: | ---: |
| 2018 | 59,91 % | 62,69 % |
| 2019 | 56,13 % | 56,13 % |
| 2020 | 61,94 % | 60,81 % |
| 2021 | 58,75 % | 60,16 % |
| 2022 | 60,47 % | 61,26 % |
| 2023 | 57,74 % | 57,34 % |
| 2024 | 57,70 % | 60,23 % |
| 2025 | 61,60 % | 63,74 % |
| 2026 | 64,60 % | 62,30 % |

## Päätös

**Säilytetään kymmenen muuttujan perusmalli ensisijaisena.** Taitoprofiilimalli paransi kaikkien otteluiden osumatarkkuutta ja Brier-arvoa tässä historiatestissä, mutta vahvojen suosikkien osumatarkkuus oli hieman heikompi ja simuloitu vedonlyönti pysyi tappiollisena. Lisäämme tilastot siis vain tutkimusmalliin. Emme väitä, että 80 % tavoite olisi saavutettu.

## Erittäin olennaiset varaukset

1. Historian 2018–2026 tuloksia on jo tarkasteltu kehitystyössä monta kertaa. Vaikka jokainen vuositesti on kronologinen, tämän toistuvan mallivalinnan takia **aineisto ei ole enää täysin koskematon riippumaton testi**. Tarvitaan uusia ajassa eteenpäin kerättäviä ennusteita.
2. Ottelutilastot voivat sisältää jälkikäteen korjattuja kirjauksia; nykyinen laskenta käyttää niitä vain jo päättyneiden otteluiden osalta.
3. Takautuvat avauskertoimet eivät välttämättä olleet lyötävissä, ja simulaatio ei huomioi kaikkia käytännön rajoitteita. Negatiivinen ROI ei todista tulevaa tappiota, mutta ei myöskään anna näyttöä tuotosta.
4. Ennusteiden osumatarkkuus, kattavuus, todennäköisyyksien kalibrointi ja ROI ovat eri mittareita. Yksi onnistunut vuosi tai korkea suosikkien prosentti ei osoita pysyvää 80 %:n tasoa.

### Toistettavat lähteet ja ajot

- [GitHub Actions: onnistunut taitoprofiilitesti](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42295663338)
- Aineisto: [nlbair/ufc-data](https://github.com/nlbair/ufc-data), CC BY 4.0
- GitHub Actions -ajon ladattava `ufc-skill-profile-research` -artefakti, `skill_profile_experiment.json`.

## Seuraava järkevä tutkimusaskel

Lukitaan mallien versiot, arkistoidaan tulevien tapahtumien ennusteet **ennen otteluiden alkua**, lisätään aineistoon lähteen julkaisuajankohdat ja mitataan oikeat lopputulokset viikoittain. Näin vältetään vuodesta toiseen saman testihistorian optimointi.
