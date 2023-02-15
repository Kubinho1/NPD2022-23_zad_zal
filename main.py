import argparse
import pandas as pd
from extra_functions import *
#import cProfile

# Pobiera (używając argparse) z wiersza poleceń ścieżki do plików (w formacie csv)
# z danymi o GDP, populacji i emisji.
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gdp", help="file with gdp data")
    parser.add_argument("pop", help="file with population data")
    parser.add_argument("co2", help="file with co2 emission data")
    parser.add_argument("-start", help="start year", required=False, type=int)
    parser.add_argument("-koniec", help="end year", required=False, type=int)
    args = parser.parse_args()

    # Zakłada że są w formacie jaki dziś (choć w przyszłości danych może być więcej,
    # czyli nie można założyć, że program ma działać dokładnie na tych plikach, które
    # są dołączone do zadania, natomiast należy założyć, że format będzie zachowany)
    # i je wczytuje.

    df_gdp = pd.read_csv(args.gdp, skiprows=4)
    df_pop = pd.read_csv(args.pop, skiprows=4)
    df_co2 = pd.read_csv(args.co2)

    # Wybiera tylko te lata, które są we wszystkich tabelach. Uwaga: chodzi o lata
    # faktycznie występujące w tych tabelach, także w przyszłości, tzn. nie można w
    # docelowej wersji na sztywno założyć (zaszyć w kodzie), że są to dane za lata
    # 1960-2014), choć w pierwszych wersjach rozwiązania to może być wygodne.

    minyears = []
    maxyears = []

    minyears.append(min(list(df_gdp.columns)[4:-1]))
    minyears.append(min(list(df_pop.columns)[4:-1]))
    minyears.append(min(list(df_co2["Year"])))

    maxyears.append(max(list(df_gdp.columns)[4:-1]))
    maxyears.append(max(list(df_pop.columns)[4:-1]))
    maxyears.append(max(list(df_co2["Year"])))

    minyears = [int(i) for i in minyears]
    maxyears = [int(i) for i in maxyears]

    if args.start:
        if args.start > max(minyears):
            start = args.start
        else:
            start = max(minyears)
    if args.koniec:
        if args.koniec < min(maxyears):
            end = args.koniec
        else:
            end = min(maxyears)

    try:
        if end - start < 0:
            raise ValueError
        else:
            print("The specified timeframe for the analysis is: {s} - {e}\n".format(s=start, e=end))

    except ValueError:
        print("The specified timeframe is empty; specified timeframe: {s} - {e}".format(s = start, e = end))
        start = max(minyears)
        end = min(maxyears)
        print("Using the default timeframe: {s} - {e}\n".format(s = start, e = end))


    # Czyści te dane (w tym punkcie nie ma wiele do zrobienia w odniesieniu do
    # podanych źródeł danych).

    df_co2=df_co2.loc[df_co2['Year']  >= start]
    df_co2=df_co2.loc[df_co2['Year']  <= end]

    df_gdp.drop(get_cols_to_drop(df_gdp), axis = 1, inplace=True)
    df_pop.drop(get_cols_to_drop(df_pop), axis = 1, inplace=True)

    ##################################################################

    # Które kraje w poszczególnych latach z danymi, emitują najwięcej CO2 w
    # przeliczeniu na mieszkańca. To znaczy generuje posortowaną po latach
    # tabelkę pięcioma krajami o największej emisji na osobę (z podaną nazwą
    # kraju, emisją na osobę i całkowitą emisją

    emissions(start,end).to_csv('most_emissions.csv', index=False)

    # Scala dane po krajach i latach.
    merged = merge_gdp_pop(start,end)

    # Które kraje w poszczególnych latach z danymi mają największy przychód
    # mieszkańca. To znaczy generuje posortowaną po latach tabelkę pięcioma
    # krajami o największym dochodzie na mieszkańca (z podaną nazwą kraju,
    # dochodem na mieszkańca i całkowitym dochodem).

    top5gdp(start,end, merged).to_csv('top_gdp.csv', index=False)

    # Które kraje (w przeliczeniu na mieszkańca) najbardziej zmniejszyły i
    # zwiększyły przez ost. 10 lat (z danych) emisję CO2.

    emission_change(start, end, df_co2).to_csv('emission_change_10_years.csv', index=False)

main()    
#cProfile.run('main()', filename = "profile_result.txt")
