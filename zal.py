import argparse
import pandas as pd

# Pobiera (używając argparse) z wiersza poleceń ścieżki do plików (w formacie csv)
# z danymi o GDP, populacji i emisji.

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

# if end - start < 0:
#     raise ValueError("The specified timeframe is empty, timeframe: {s} - {e}".format(s = start, e = end))

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


#print("Analiza dotyczy lat {r1} - {r2}".format(r1 = start, r2 = end))

# Czyści te dane (w tym punkcie nie ma wiele do zrobienia w odniesieniu do
# podanych źródeł danych).

df_co2=df_co2.loc[df_co2['Year']  >= start]
df_co2=df_co2.loc[df_co2['Year']  <= end]


def get_cols_to_drop(df):

    a = list(df)[4:-1]
    a = [int(i) for i in a if int(i) < start or int(i) > end]
    a = [str(i) for i in a] + [list(df)[-1]]

    return a

df_gdp.drop(get_cols_to_drop(df_gdp), axis = 1, inplace=True)
df_pop.drop(get_cols_to_drop(df_pop), axis = 1, inplace=True)

##################################################################

# Które kraje w poszczególnych latach z danymi, emitują najwięcej CO2 w
# przeliczeniu na mieszkańca. To znaczy generuje posortowaną po latach
# tabelkę pięcioma krajami o największej emisji na osobę (z podaną nazwą
# kraju, emisją na osobę i całkowitą emisją

def emissions(year1, year2):

    first = df_co2.loc[df_co2['Year'] == year1]
    first = first.drop(first.columns[[3, 4, 5, 6, 7, 9]], axis=1)
    first.sort_values(by=["Per Capita"], ascending=False, inplace=True)
    first = first.head(n=5)

    for i in range(year1+1, year2+1):

        temp = df_co2.loc[df_co2['Year']  == i]
        temp = temp.drop(temp.columns[[3, 4, 5, 6, 7, 9]], axis=1)
        temp.sort_values(by=["Per Capita"], ascending=False, inplace=True)
        first = first.append(temp.head(n=5))


    return first

#print(emissions(start,end))
emissions(start,end).to_csv('most_emissions.csv', index=False)



# Scala dane po krajach i latach.

def merge_gdp_pop(year1, year2):

    year = []
    name = []
    tot = []
    pop = []

    for i in range(year1, year2+1):
        tot += list(df_gdp[str(i)])
        name += list(df_gdp['Country Name'])
        year += [i] * len(list(df_gdp[str(i)]))
        pop += list(df_pop[str(i)])

    per = [i / j for i, j in zip(tot, pop)]
    df = {"Year": year, "Country": name, "Total GDP": tot, "Population": pop, "GDP per capita": per}

    return pd.DataFrame(df)

merged = merge_gdp_pop(start,end)

# Które kraje w poszczególnych latach z danymi mają największy przychód
# mieszkańca. To znaczy generuje posortowaną po latach tabelkę pięcioma
# krajami o największym dochodzie na mieszkańca (z podaną nazwą kraju,
# dochodem na mieszkańca i całkowitym dochodem).

def top5gdp(year1, year2, table):

    result = table.loc[table['Year'] == year1]
    result = result.sort_values(by=["GDP per capita"], ascending=False)
    result = result.head(n=5)

    for i in range(year1+1, year2+1):

        temp = table.loc[table['Year']  == i]
        temp = temp.sort_values(by=["GDP per capita"], ascending=False)
        result = result.append(temp.head(n=5))

    return result

#print(top5gdp(start,end, merged))
top5gdp(start,end, merged).to_csv('top_gdp.csv', index=False)
# Które kraje (w przeliczeniu na mieszkańca) najbardziej zmniejszyły i
# zwiększyły przez ost. 10 lat (z danych) emisję CO2.

def emission_change(year1, year2, table):
    if year2 - year1 < 10:
        period = year2 - year1
    else:
        period = 10
    then = table.loc[table['Year'] == year2-period]
    then = then.sort_values(by=["Country"])

    now = table.loc[table['Year'] == year2]
    now = now.sort_values(by=["Country"])

    countries_then = list(then['Country'])
    countries_now = list(now['Country'])
    percapita_then = list(then['Per Capita'])
    percapita_now = list(now['Per Capita'])

    t1 = {countries_then[i]: percapita_then[i] for i in range(len(countries_then))}
    t2 = {countries_now[i]: percapita_now[i] for i in range(len(countries_now))}

    to_del = []
    for k in t1:
        if k not in t2:
            to_del.append(k)

    for k in to_del:
        del t1[k]

    to_del = []
    for k in t2:
        if k not in t1:
            to_del.append(k)
    for k in to_del:
        del t2[k]

    countries_existed_then_now = []
    change = []

    for k in t1:

        countries_existed_then_now.append(k)
        change.append(t2[k] - t1[k])

    countries_then_to_print = set(countries_then) - set(countries_existed_then_now)
    countries_now_to_print = set(countries_now) - set(countries_existed_then_now)
    #print(set(countries_then).difference(set(countries_existed_then_now)))
    print("Countries that were on the list in {s} that aren't there in {e}: ". format(s = year2 - period, e = year2))
    print(countries_then_to_print)
    print("Countries that are on the list in {e}, that weren't there in {s}: ".format(s = year2 - period, e = year2))
    print(countries_now_to_print)
    print("These countries are excluded from the calculations when it comes to change in emissions")


    df = {"Country": countries_existed_then_now, "Change in emissions": change}

    return pd.DataFrame(df).sort_values(by = ["Change in emissions"])


#print(emission_change(start, end, df_co2))
emission_change(start, end, df_co2).to_csv('emission_change_10_years.csv', index=False)