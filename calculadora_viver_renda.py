from dateutil.relativedelta import relativedelta
import numpy_financial as npf
import datetime
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description='Calculadora de renda passiva')


parser.add_argument(
    '-r', '--renda', dest='passive_income', type=float, required=True,
    help='Quanto deseja de renda passiva mensal?')


parser.add_argument(
    '-a', '--aporte', dest='monthly_contribution', type=float, required=True,
    help='Quanto vai poupar por mês?')


parser.add_argument(
    '-p', '--patrimonio', dest='current_patrimony', type=float, required=True,
    help='Quanto você tem hoje?')


args = parser.parse_args()


def find_bc(cod_bcb):
    url = 'http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json'.format(cod_bcb)
    df = pd.read_json(url)
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df.set_index('data', inplace=True)
    return df


def main():
    cdi_cum = find_bc(4391)
    ipca_cum = find_bc(433)
    years_ago = datetime.datetime.now() - relativedelta(years=8)

    cdi_mean_8y = cdi_cum[(cdi_cum.index >= years_ago)]\
        .groupby(pd.Grouper(freq='Y'))\
        .sum()\
        .mean()

    ipca_mean_8y = ipca_cum[(ipca_cum.index >= years_ago)]\
        .groupby(pd.Grouper(freq='Y'))\
        .sum()\
        .mean()

    year_profitability = (cdi_mean_8y*1.30-ipca_mean_8y) / 100
    future_patrimony = ((args.passive_income * 12) / year_profitability)
    years_investing = npf.nper(year_profitability.valor/12, -args.monthly_contribution, -args.current_patrimony, future_patrimony.valor) / 12

    print('130% do CDI com a média do CDI e IPCA dos últimos 8 anos equivale a {:.2f}% a.a'.format(year_profitability.valor*100))
    print('Patrimônio necessário para viver de renda R$ {:,.2f}'.format(future_patrimony.valor))
    print('É necessário poupar por {:.1f} anos para ter esse patrimônio'.format(years_investing))


if __name__ == "__main__":
    main()