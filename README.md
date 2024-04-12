# Vectorvision
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/vectorvision/badge/?version=latest)](https://vectorvision.readthedocs.io/en/latest/?badge=latest)

## Overview
Projekt polega na zaimplementowaniu narzędzia pozwalającego na konwersję obrazka z formatu rastrowego (np. .png lub .jpg) do wersji wektorowej (np. .svg).

Aplikacja powinna wspierać przynajmniej formaty wejściowe PNG i JPG oraz format wyjściowy SVG. Utworzony plik SVG powinien zostać w miarę możliwości zoptymalizowany pod kątem rozmiaru. Aplikacja powinna działać z poziomu konsoli (CLI).


## Features

Program powinien umożliwiać przetwarzanie obrazów z formatów rastrowych PNG i JPG do formatu wektorowego SVG. W pierwszej kolejności obsługiwana będzie konwersja prostych obrazów binarnych, docelowo również bardziej skomplikowanych obrazów monochromatycznych i kolorowych. Obsługa programu odbywać się będzie z poziomu linii komend. Użytkownik przed uruchomieniem będzie miał możliwość określenia parametrów konwersji związanych z używanym algorytmem oraz (potencjalnie) wyboru algorytmu konwersji za pomocą flag wywołania. Ostateczna decyzja dotycząca implementowanych wariantów algorytmów konwersji zostanie podjęta po dogłębniejszym zapoznaniu się z tematem w  najbliższych tygodniach.

- Wsparcie dla formatów wejściowych: PNG, JPG.
- Format wyjściowy: SVG.
- Optymalizacja pliku wyjściowego SVG pod kątem rozmiaru.
- Uruchomienie programu z poziomu konsoli komendą:
	program <sciezka do pliku wejscia> <nazwa pliku wyjscia> <parametry konwersji>

## Tech Stack
Projekt zrealizowany zostanie w języku Python. Na chwilę obecną zakładamy wykorzystanie następujących bibliotek:
- Sphinx
- PIL
- numpy 
- argparse
- OpenCV
- pytest



## Docs
See the documentation for detailed information:
https://vectorvision.readthedocs.io/en/latest/?badge=latest

## Installation:

## Usage:


## Authors
- [@Karol Ziarek](https://github.com/ziarekk)
- [@Wojciech Lapacz](https://github.com/WojciechL02)
- [@Kajan Rożej](https://github.com/Kajotello)

## License
Please check the MIT license that is listed in this repository.
