# Markkinan ja UFC-mallin yhdistäminen – 6.11.2026

## Tavoite
Testata, voiko oma ennen ottelun alkua tuotettu ennuste parantaa vedonlyöntikertoimista johdettua markkinaennustetta. Tämä on tutkimusta eikä vedonlyöntisuositus.

## Menetelmä
- Opetusdata: UFC:n ratkaistut ottelut ennen vuotta 2024 (5 157 kpl).
- Vuoden 2024 validointijoukko: markkinakertoimet saatavilla **512 ottelusta**.
- Vuoden 2025–2026 ajallinen testijoukko: 948 ottelua, joista markkinakertoimet saatavilla **937 ottelusta**.
- Omat todennäköisyydet kalibroitiin aikaisemman validoinnin perusteella.
- Lineaarisen yhdistelmän oman mallin paino valittiin **vain vuoden 2024 validointijoukossa** kiinteistä vaihtoehdoista 0 %, 25 %, 50 %, 75 %, 100 %, minimoiden log loss.
- Vuoden 2025–2026 testijaksoa ei käytetty yhdistämispainon valintaan.

## Tulos

**Validoinnissa valittu oman mallin paino oli 0 %**: käytännössä pelkkä vedonvälittäjien kertoimista laskettu marginaalista puhdistettu markkinatodennäköisyys. Valittu validoinnin log loss oli 0,60511.

Vertailu samoissa 937 testijoukon ottelussa:

| Mittari | Alkuperäinen oma malli | Markkina = valittu yhdistelmä |
| --- | ---: | ---: |
| Voittajan oikein | 62,86 % | **66,81 %** |
| Brier (pienempi parempi) | 0,2297 | **0,2094** |
| Log loss (pienempi parempi) | 0,6514 | **0,6071** |

Kaikilla 948 testijoukon ottelulla yhdistelmäjärjestelmä (markkina, ellei kerrointa ole; silloin oma malli) saavutti 66,46 % tarkkuuden. Tämän vertailun lukua **ei** saa kutsua oman mallin ennustetarkkuudeksi.

Yhdistelmämallin +5 % laskennallisen odotusarvosäännön vedonlyöntisimulaatiossa tehtiin **0 vetoa**, joten ROI:ta ei voida laskea. Markkinatodennäköisyyksistä ei syntynyt tällä säännöllä näennäistä etua samoilla kertoimilla.

GitHub Actions: https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42291814506

## Johtopäätös
Mallimme ei ole vielä osoittanut tuovansa markkinalle uutta ennustearvoa. Numeron nousu 62,9 % -> 66,8 % ei ole itsenäinen algoritminen läpimurto, koska valittu menetelmä käyttää yksinomaan markkinan arviota.

80 %:n tarkkuutta ei ole saavutettu. Tavoite vaatii raportoinnin kaikkien ottelujen osalta, valikoidun osajoukon osalta erikseen sekä kattavuuden, epävarmuusvälit ja arvioidun ROI:n.

## Seuraava varsinainen tutkimus
1. Rakennetaan uusia ajallisesti turvallisia, todistetusti ennen ottelua saatavilla olleita muuttujia.
2. Mitataan, tuovatko ne lisäarvoa markkinakertoimiin verrattuna uusilla ajanjaksoilla.
3. Parannetaan ottelijahistorian kattavuutta ja uutis-/loukkaantumis-/lyhyen varoitusajan lähteiden aikaleimoja.
4. Markkinan avaushintojen saatavuutta ja ajankohtaa ei ole todennettu käytännön panostuksen kannalta; siksi tulokset ovat teoreettisia.
