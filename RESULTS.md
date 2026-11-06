# Ensimmäinen historiallinen UFC-mallin vertailu – 6.11.2026

## Lähde ja testiasetelma

- Lähde: [nlbair/ufc-data](https://github.com/nlbair/ufc-data) (CC BY 4.0), UFC-ottelut 2013–10.10.2026.
- Koulutus: ennen 1.1.2024, **5 157** ratkaistua ottelua.
- Validointi: 1.1.–31.12.2024, **513** ottelua.
- Koskematon ajallinen testi: 1.1.2025 alkaen, **948** ottelua.
- Tulokset vahvistettu GitHub Actionsissa: [historiallinen testiajo](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42289043939).
- Koodi: `engine.py`. Ottelijoiden järjestystä vaihdellaan deterministisesti ja saman päivän ottelut käsitellään ilman saman päivän tulosvuotoa.

## Testitulos

| Mittari | Malli (948 ottelua) | Elo-verrokki (948 ottelua) |
| --- | ---: | ---: |
| Voittajaennusteen osumatarkkuus | 62,55 % | 56,22 % |
| Brier-pisteet (pienempi parempi) | 0,2305 | 0,2455 |
| Log loss (pienempi parempi) | 0,6532 | 0,6842 |

## Reilu markkinavertailu samoilla otteluilla

Avauskertoimet oli saatavilla **937 ottelusta**:

| Mittari | Oma malli | Markkinan marginaalista puhdistettu avauskerroinarvio |
| --- | ---: | ---: |
| Osumatarkkuus | 62,86 % | **66,81 %** |
| Brier | 0,2297 | **0,2094** |
| Log loss | 0,6514 | **0,6071** |

**Markkinan arviot olivat näissä testeissä parempia kuin oma mallimme.** Tämä ei vielä osoita markkinan tai mallin tulevaa suorituskykyä.

## Vedonlyöntikokeilu

Kokeellinen sääntö: lyö korkeintaan yksi 1 yksikön veto per ottelu, jos laskennallinen odotusarvo avauskertoimella ylittää +5 %. Kun molemmat puolet täyttävät säännön, valitse suurempi laskennallinen etu.

- Vetoja: **762**
- Kokonaispanos: **762 yksikköä**
- Historiallinen voitto/tappio: **−24,777 yksikköä**
- ROI: **−3,25 %**

Sääntö ei ole tuottava tällä testijaksolla. Historialliset avauskertoimet eivät välttämättä olleet aidosti tarjolla, eikä testi huomioi hintaliukumaa tai kaikkia rajoituksia. Yksi ajallinen testijakso ei todista yleistä kannattavuutta tai kannattamattomuutta.

## Päätökset ja seuraavat työvaiheet

1. **Ei oikean rahan panoksia tämän mallin perusteella.** Nykyinen strategia on testissä tappiollinen.
2. Otetaan vedonlyöntimarkkina vertailupisteeksi; mittaamme lisäarvoa samoilla otteluilla.
3. Tarkistetaan aineiston ottelijajärjestyksen, historiallisten poissaolotietojen, ranking-tietojen ja päivämäärien mahdolliset vuotokohdat.
4. Koulutetaan todennäköisyydet vain aikaisemmilla otteluilla ja kalibroidaan ne erillisellä validointijoukolla.
5. Lisätään tarkistettuja KO/TKO-palautumisen, painonpudotuksen ja muiden ennakkotietojen muuttujia vain silloin, kun niistä on luotettavat lähteet.
6. Käytetään seuraavia aikajaksoja uusina testeina eikä valita parametreja vuoden 2025–2026 testijakson perusteella.
7. Vertaillaan eri riskirajoja ja vetoihin vaadittavaa etua **vain kehitys-/validointiaineistolla**, ei jälkikäteen parhaan tuloksen metsästämiseksi testijoukosta.

*Tämä dokumentti kuvaa todennettuja historiallisen ohjelma-ajon tuloksia, ei sijoituslupausta tai lääketieteellistä diagnoosia.*


## 6.11.2026 – Aikajärjestyksessä erillisellä validoinnilla tehty kalibrointi

- Menetelmä: symmetrinen temperature scaling; lämpötilaksi valikoitui **0,8** käyttämällä ainoastaan vuoden 2024 validointia.
- Vuoden 2025–2026 erillinen testijoukko: **948 ottelua**.
- Brier ennen **0,2305**, kalibroinnin jälkeen **0,2298** (pienempi parempi).
- Log loss ennen **0,6532**, kalibroinnin jälkeen **0,6517** (pienempi parempi).
- Kalibroidun mallin simuloitu vetostrategia: **745 vetoa**, tuotto **−21,56 yksikköä**, ROI **−2,89 %**.
- Markkinavertailu samoilla **937 ottelulla**: kalibroitu malli Brier **0,2287**, marginaalista puhdistettu avauskerroin Brier **0,2094**. Markkina edelleen parempi.
- Tulos vahvistettu GitHub Actions -lokista: https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42289945148

**Johtopäätös:** Kalibrointi paransi mitattua todennäköisyyslaatua, mutta vedonlyönti oli edelleen tappiollista. Myös lisäoptimointi juuri näiden 2025–2026 testitulosten mukaan vääristäisi tuloksia: uudet muutokset on testattava erillisillä tulevilla otteluilla tai huolellisesti rakennetuilla ajallisilla vertailuilla.

## Julkiset valmistautumistiedot

- `fighter_context.py` varmistaa, että dokumentti on julkaistu ennen ottelua, lähde on yksilöity ja tapahtumatyyppi kuuluu rajattuun, objektiiviseen luetteloon.
- `data/public_context_2026-11-07.csv` sisältää UFC:n omiin ennakkoilmoituksiin perustuvia muutoksia 7.11.2026 ottelukorttiin. Tiedot ovat **kontekstia**, eivät automaattisia terveys- tai voittotodennäköisyysarvioita.
- Lähteet: https://www.ufc.com/news/updates-ufc-fight-night-cortes-acosta-vs-walker ja https://www.ufc.com/news/ufc-fight-night-bonfim-vs-brady-updates
- Yksityisiä terveystietoja, diagnosoimattomia ongelmia, väitteitä henkilökohtaisista kriiseistä tai huhuja **ei kerätä**.
