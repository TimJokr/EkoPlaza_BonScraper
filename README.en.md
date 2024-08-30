# EkoPlaza BonScraper

A Webscraper to get your receipts from EkoPlaza using your online account.

## Installation
### Installing Python if necessary
This is written in Python 3.12.5. Download the [newest version](https://www.python.org/downloads/). Click "Add to PATH" during installation.

### Installing NumPy and Selenium if necessary
This is written with NumPy 2.1.0 and Selenium 4.24.0. The newest versions can be installed by executing the following lines in the command prompt or Windows PowerShell:

```
pip install numpy
pip install selenium
```

### Download this project
Download the [latest Release](https://github.com/TimJokr/EkoPlaza_BonScraper/releases/latest/). This folder can be placed anywhere.

## Usage
Click on the adress bar in the folder with the *EkoPlaza_BonScraper.py* file. Type "cmd" and enter. Execute the following line:

```
py ./EkoPlaza_BonScraper.py
```
The first time, you will be asked for your preferences and data. Afterwhich everything will be done automatically. This can take a while the first time.
When the program is done, there will be a CSV file named "output.csv". You can do with this what you want; like opening it with a text editor ([Notepad++](https://notepad-plus-plus.org/downloads/), etc.) or spreadsheet program ([LibreOffice Calc](https://www.libreoffice.org/download/download-libreoffice/), [Microsoft Excel](https://www.microsoft.com/nl-nl/microsoft-365/excel), etc.) of your choice. Leave the rest of te files, unless you know what you are doing.

## Privacy
This program needs your EkoPlaza email and password. These will be saved locally and are *only* used during login. Nobody has access to this, except the people with access to your PC.

## Downsides
Due to the way the EkoPlaza site works, there are multiple suboptimal things:
- Discounts aren't shown, leading to the total price and the price of the products together, not always being the same.
- The loading of the transactions is slower than necessary to prevent double transactions.