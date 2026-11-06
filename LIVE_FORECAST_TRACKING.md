# Etukäteen lukittujen UFC-ennusteiden todellinen seuranta

Päiväys: 6.11.2026

## Miksi tämä on tärkeää?

Aiemmissa tutkimuksissa samaa historiallista aineistoa on jo käytetty lukuisia kertoja. Jotta pystymme luotettavasti mittaamaan tulevan mallin suorituskykyä, tallennamme ennusteet **ennen otteluita** ja tarkistamme jälkikäteen vain näitä alkuperäisiä ennusteita.

## 7.11.2026 otteluillan lukittu arkisto

- [Lukitus valmistui GitHubissa](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions/runs/42296300043)
- Arkisto: `frozen-ufc-nov7-42296300043`, GitHub Actions -ajon Artifacts-osio.
- Mukana `frozen_predictions.csv` ja `manifest.json`.
- Manifest sisältää SHA-256-tunnisteen ennustetiedostolle, alkuperäisen ottelukortin ja historiatiedoston tiivisteet, ajon tunnisteen ja aikaleiman.
- Lukitusaikaraja: **7.11.2026 klo 12.00 UTC**. Ajon pitää valmistua ennen sitä.
- Arkisto on GitHub Actionsin artefakti, jonka säilytysaika on tässä ajossa 90 päivää. Se ei ole pysyvä arkisto.

## Jälkitarkistus

Kun ottelut ovat päättyneet ja historiadataan on merkitty tulokset:

1. Avaa [GitHub Actions -näkymä](https://github.com/phuhtamaki-maker/UFC-Prediction-Engine/actions).
2. Valitse `Score frozen UFC Nov 7 picks`.
3. Valitse `Run workflow`. Tämä käyttää alkuperäistä lukittua artefaktia, ei uutta ennusteajoa.
4. Ajo tarkistaa tiivisteen, hakee uusimmat historiatulokset ja julkaisee `frozen_score.json`-raportin omana artefaktinaan.

Jos ottelutuloksia ei vielä löydy historiadatasta, ajo ilmoittaa ettei arviointia ole mahdollista tehdä, eikä se keksi osumia.

`score_frozen.py` osaa myös ajaa tarkistuksen paikallisesti:

```bash
python score_frozen.py \
  --frozen results/original_snapshot/frozen_predictions.csv \
  --manifest results/original_snapshot/manifest.json \
  --results data/ufc_all_fights_wide.csv \
  --out results/frozen_score.json
```

## Arviointisäännöt

- Vain sama päivämäärä ja täsmälleen sama ottelupari ovat arvioitavia.
- Perutut ottelut, muuttuneet vastustajat, tasapelit, NC-tulokset ja puuttuvat tulokset jäävät arvioinnin ulkopuolelle ja näkyvät lukumäärissä.
- Jos sama ottelu esiintyy tuloksissa kahdesti, tulos merkitään epäselväksi eikä sitä lasketa.
- Muutettu ennustetiedosto hylätään SHA-256-tarkistuksessa.
- Tuloksissa raportoidaan myös arvioitujen otteluiden osuus kaikista lukituista ennusteista.
- Tulos ei ole sama kuin vedonlyönnin ROI, eikä korkea osumatarkkuus todista voitollisuutta.
- **Tietojen ennakollisuus** on osoitettu vain arkistoon kirjatuilla ajoajoilla ja syötteiden tiivisteillä. Ulkoisen aineiston historiallista saatavuushetkeä ei voida aukottomasti todistaa tästä arkistosta yksin.

## Jatkokehitys

Tuleville UFC-korteille tehdään vastaava ennusteiden lukitus ennen otteluita. Versionvaihdoksia verrataan vain uusiin etukäteen lukittuihin tuloksiin, jotta aiemman testihistorian perusteella tehty valikointi ei vääristä mittausta. Tavoite 80 % pysyy kokeellisena tutkimustavoitteena, ei lupauksena.
