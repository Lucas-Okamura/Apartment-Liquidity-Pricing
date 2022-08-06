import os
import pandas as pd
import numpy as np
import math

class Portfolio:
    def __init__(self):
        self.home_path=os.path.abspath('')

        # ler arquivos de bins de lat e long
        self.latitude_bins = pd.IntervalIndex(np.load('./parameters/lat_bins.npy', allow_pickle=True))
        self.longitude_bins = pd.IntervalIndex(np.load('./parameters/long_bins.npy', allow_pickle=True))

        # budget
        self.budget = 150000000

    def feature_engineering(self, apartments):

        # transformando latitude e longitude em bins
        apartments['latitude_bins'] = pd.cut(apartments['latitude'], bins = self.latitude_bins).astype(str)
        apartments['longitude_bins'] = pd.cut(apartments['longitude'], bins = self.longitude_bins).astype(str)

        # map de latitude e longitude em labels
        map_lat = {}
        map_long = {}

        for index, item in enumerate(self.latitude_bins.sort_values().astype(str)):
            map_lat[item] = str(index)
            
        for index, item in enumerate(self.longitude_bins.sort_values().astype(str)):
            map_long[item] = str(index)
            
        apartments['latitude_bins'] = apartments['latitude_bins'].map(map_lat)
        apartments['longitude_bins'] = apartments['longitude_bins'].map(map_long)

        # criando features lat_long_bins e rooms garages
        apartments['lat_long_bins'] = apartments['latitude_bins'] + apartments['longitude_bins']
        apartments['rooms_garages'] = apartments['rooms'] + apartments['garages']

        return apartments

    def data_preparation(self, apartments, model):
        # seleção de colunas
        apartments = apartments[['useful_area', 'value', 'interior_quality', 'rooms_garages', 'lat_long_bins']]

        # one hot encoding em lat_long_bins
        apartments = pd.get_dummies(apartments, columns = ['lat_long_bins'], drop_first = True)

        # preencher colunas faltantes com 0
        for column in model.feature_names:
            if column not in apartments.columns:
                apartments[column] = 0

        return apartments

    def predict_scenario(self, apartments, model, multiply_values, renovate = False):
        # verificando se argumentos fornecidos são listas
        if not isinstance(multiply_values, list):
            multiply_values = [multiply_values]
        
        for multiply_value in multiply_values:
            # ----------- aplicando cenário -------------- #
            multiply_name = str(int(round((multiply_value - 1) * 100))) + '%' # nome a ser exibido na coluna para identificação
            apartments_copy = apartments[['useful_area', 'value', 'interior_quality', 'rooms_garages',
                                        'lat_long_bins_01', 'lat_long_bins_02', 'lat_long_bins_10',
                                        'lat_long_bins_11', 'lat_long_bins_12', 'lat_long_bins_20',
                                        'lat_long_bins_21', 'lat_long_bins_22']].copy() # seleção apenas de colunas pertinentes para o modelo
            # aumento de preço
            apartments_copy['value'] = apartments_copy['value'] * multiply_value # alterando valor no dataframe a ter predito
            apartments['value_' + multiply_name] = apartments['value'] * multiply_value # trazendo novo valor de venda para o dataframe original

            # reforma
            if renovate:
                apartments_copy['interior_quality'] = 3
                column_name = f'mais_{multiply_name}_com_reforma'
                print(f"{multiply_name} com reforma")
            else:
                column_name = f'mais_{multiply_name}_sem_reforma'
                print(f"{multiply_name} sem reforma")

            # -------- prevendo probabilidades de venda ----------- #
            predict =  1 - model.predict(apartments_copy)

            # -------- obtendo em quantos dias um apartamento chega em 55% de probabilidade de venda ----------- #
            s = np.where(predict.gt(0.55, axis = 0), predict.columns, '')
            s2 = pd.Series([', '.join(x).strip(', ') for x in s])
            s3 = s2.str.split(', ').apply(lambda x: pd.to_numeric(x[0], errors = 'coerce')) # pd.Series com o dia em que foi atingido prob > 55%

            # -------- trazendo informações de dias, probabilidade e lucro / dia escolhidos para o dataframe original ----------- #
            predict['DIAS_' + column_name] = s3
            apartments['DIAS_' + column_name] = s3
            predict_prob_selected = predict.apply(lambda x: x[x['DIAS_' + column_name]] if not math.isnan(x['DIAS_' + column_name]) else np.nan, axis = 1) # obtendo probabilidade neste dia
            apartments['PROB_' + column_name] = predict_prob_selected
            apartments['LUCRO_DIA_INVEST_' + column_name] = (apartments['value_' + multiply_name] - apartments['value']) / (apartments['DIAS_' + column_name] * apartments['value'])
        
        return apartments

    def get_prediction(self, model, apartments_raw, apartments):
        # predict 10%, 20%, 30%, 40% sem reforma
        apartments = self.predict_scenario(apartments, 
                                    model, 
                                    [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2],
                                    renovate = False)

        # predict 10%, 20%, 30%, 40% com reforma
        apartments = self.predict_scenario(apartments, 
                                    model, 
                                    [1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2],
                                    renovate = True)

        # --------- obtendo maior taxa de lucro / (dia * investimento) ---------------#
        columns_lucro = [column for column in apartments.columns if column.startswith('LUCRO_DIA_INVEST')]

        # coeficiente de lucro / dia, investimento para o melhor cenario 
        apartments['better_scenario_coeff'] = apartments[columns_lucro].max(axis = 1)

        # melhor cenário de aumento de preço + reforma ou não
        apartments['better_scenario'] = apartments[columns_lucro].idxmax(axis = 1)

        # observacao da sugestao (com ou sem reforma)
        apartments['obs'] = apartments['better_scenario'].str[-11:]

        # colunas de melhor aumento de preço
        apartments['better_raise'] = 'value_' + apartments['better_scenario'].str.findall('\d+%').apply(pd.Series)

        # melhor aumento de preço
        apartments['sale_price'] = apartments.loc[~apartments['better_raise'].isna()].apply(lambda x : x[x['better_raise']], axis = 1)

        # selecionando colunas pertinentes para sugestao de compra
        apartments = apartments[['better_scenario', 'better_raise', 'sale_price', 'better_scenario_coeff', 'obs', 'value']]

        # ordenacao por melhor coeficiente de lucro
        sorted_apartments = apartments.sort_values(by = 'better_scenario_coeff', ascending = False).reset_index()
        invested = 0
        buy_apartments = pd.DataFrame(columns = sorted_apartments.columns)

        for idx, row in sorted_apartments.iterrows():
            if invested + row.value < self.budget:
                buy_apartments = buy_apartments.append(row)
                invested += row.value

        # merge para trazer informações finais
        final_apartments_list = buy_apartments[['index', 'sale_price', 'obs']].merge(apartments_raw, left_on = 'index', right_index = True)

        return final_apartments_list.to_json( orient='records', date_format='iso' )