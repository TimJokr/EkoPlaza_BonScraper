# EkoPlaza BonScraper
[English README](./README.en.md)

Een Webscaper om EkoPlaza bonnen te krijgen via ja online account.

## Installatie
### Instaleer Python indien nodig
Dit is geschreven in Python 3.12.5. Download de [nieuwste versie](https://www.python.org/downloads/). Klik "Add to PATH" tijdens installatie.

### Instaleer NumPy en Selenium indien nodig
Dit is geschreven met NumPy 2.1.0 en Selenium 4.24.0. De nieuwste versies kunnen geïnstaleerd worden door de volgende regels uit te voeren in de opdrachtprompt of Windows PowerShell:

```
pip install numpy
pip install selenium
```

### Download dit project
Download de [laatste Release](https://github.com/TimJokr/EkoPlaza_BonScraper/releases/latest/). Deze folder kan overal geplaats worden.

## Gebruik
Klik op de adresbalk in de folder met het *EkoPlaza_BonScraper.py* bestand. Type "cmd" en enter. Voer de volgende regel uit:

```
py ./EkoPlaza_BonScraper.py
```
De eerste keer word om voorkeuren en gegevens gevraagd. Daarna wordt alles automatisch geregeld. Dit kan eventjes duren de eerste keer.
Als het programma klaar is, staat in de folder een CSV bestand genaamd "output.csv". Hiermee kan gedaan worden wat u wil; zoals openen met een textbewerker ([Notepad++](https://notepad-plus-plus.org/downloads/), etc.) of spreadsheet-programma ([LibreOffice Calc](https://www.libreoffice.org/download/download-libreoffice/), [Microsoft Excel](https://www.microsoft.com/nl-nl/microsoft-365/excel), etc.) naar keuze. De rest van de bestanden moeten met rust gelaten worden, behalve als u weet wat u doet.

## Privacy
Dit programma heeft uw EkoPlaza mail en wachtwoord nodig. Deze worden lokaal opgeslagen en worden *alleen* gebruikt tijdens het inloggen. Niemand heeft hier toegang tot, behalve de mensen met toegang tot uw PC.

## Nadelen
Door de manier dat de EkoPlaza site werkt, zijn er meerdere dingen die suboptimaal werken:
- Kortingen worden niet weergegeven, waardoor het totaal bedrag en de prijs van de producten samen, niet altijd overeenkomt.
- Het laden van de transacties is langzamer dan nodig om dubbele transacties te verkomen.