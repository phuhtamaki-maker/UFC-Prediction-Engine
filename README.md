# UFC Prediction Engine 🥊

Paavon ja DD:n kokeellinen UFC-ennustemalli. **Tutkimusprototyyppi, ei todennettu vedonlyöntietu.**

## Projektin tiedostot

- `main.py`: ensimmäinen Python-harjoituksemme; säilytetty ennallaan.
- `engine.py`: historialliset ottelut, ennakko-ominaisuudet, kronologinen arviointi ja vedonlyönnin simulaatio.
- `predict.py`: alustavat voittotodennäköisyydet tuleviin otteluihin.
- `tests/`: automaattiset kooditestit.
- `DEVELOPMENT_PLAN.md`: kehityssuunnitelma.

## Käyttö GitHub Codespacesissa

Avaa projektin Codespace ja kirjoita terminaaliin:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

Historiallisen UFC-aineiston lataaminen ja mallin ajaminen:

```bash
python engine.py --download
```

Ohjelma hakee tiedoston `data/ufc_all_fights_wide.csv` ja tekee aikajärjestyksessä jaetun arvioinnin: opetus ennen vuotta 2024, vuoden 2024 validointi ja vuodesta 2025 alkava testijoukko. Tulokset tallentuvat `results/report.json` ja `results/out_of_sample_predictions.csv`.

Tulevan illan ottelut annetaan itse tarkistetussa CSV-tiedostossa, jonka sarakkeet ovat `event_date,f1_name,f2_name`. Esimerkiksi:

```csv
event_date,f1_name,f2_name
2026-11-07,Fighter A,Fighter B
```

Tämä on **vain formaattiesimerkki**, ei oikea ottelupari. Kun koko aineisto on ladattu, ennusteen voi muodostaa komennolla:

```bash
python predict.py --card data/upcoming.csv
```

## Tutkimuksen rajat

- Malli ei saa käyttää ennustettavan ottelun lopputulosta tai sen aikana syntyviä tilastoja.
- Koodi käsittelee saman päivän ottelut yhtenä ryhmänä, jolloin saman päivän tulokset eivät päädy toistensa ennakko-ominaisuuksiin.
- Aineiston alkuperäinen ottelijajärjestys saattaa olla voittajapainotteinen; se satunnaistetaan deterministisesti.
- KO/TKO-historia on vain aiemman lopetustavan kuvaus, **ei aivovammadiagnoosi tai todistus iskunkestävyyden muutoksesta**.
- Puuttuvia painonpudotus- tai nesteytystietoja ei arvata. Ne eivät vielä vaikuta mallin ennusteeseen.
- Todennäköisyyksiä ei ole vielä riippumattomasti kalibroitu eikä mallille ole osoitettu kannattavaa vedonlyöntietua.
- Historialliset avauskertoimet eivät välttämättä olleet käytännössä lyötävissä ilmoitettuun hintaan. ROI-simulaatio ei huomioi kaikkia käytännön rajoituksia.

## Aineisto ja lähteet

Bair, N. (2026), *UFC Data: scorecards, round statistics, and betting odds, 2013 to 2026*, versio 0.1.1, CC BY 4.0: https://github.com/nlbair/ufc-data ja https://doi.org/10.5281/zenodo.23458636.

Työkalu ei ole UFC:n hyväksymä tai siihen sidoksissa.
