import pandas as pd
def get_cols_to_drop(df,start,end):

    a = list(df)[4:-1]
    a = [int(i) for i in a if int(i) < start or int(i) > end]
    a = [str(i) for i in a] + [list(df)[-1]]

    return a

def emissions(year1, year2, df_co2):
    
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

def merge_gdp_pop(year1, year2, df_gdp, df_pop):

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


def top5gdp(year1, year2, table):

    result = table.loc[table['Year'] == year1]
    result = result.sort_values(by=["GDP per capita"], ascending=False)
    result = result.head(n=5)

    for i in range(year1+1, year2+1):

        temp = table.loc[table['Year']  == i]
        temp = temp.sort_values(by=["GDP per capita"], ascending=False)
        result = result.append(temp.head(n=5))

    return result

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
    print("Countries that were on the list in {s} that aren't there in {e}: ". format(s = year2 - period, e = year2))
    print(countries_then_to_print)
    print("Countries that are on the list in {e}, that weren't there in {s}: ".format(s = year2 - period, e = year2))
    print(countries_now_to_print)
    print("These countries are excluded from the calculations when it comes to change in emissions")


    df = {"Country": countries_existed_then_now, "Change in emissions": change}

    return pd.DataFrame(df).sort_values(by = ["Change in emissions"])
