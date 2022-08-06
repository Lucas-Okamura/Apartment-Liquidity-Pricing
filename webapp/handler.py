import pickle
from flask import Flask, request, Response
import pandas as pd
from portfolio.Portfolio import Portfolio
import os

with open('./model/portfolio_2.pkl', 'rb') as file:
    model = pickle.load( file )

# initialize API
app = Flask( __name__ )

@app.route( '/portfolio/predict', methods=['POST'] )
def sugest_apartments():
    test_json = request.get_json()
   
    if test_json: # there is data
        test_raw = pd.DataFrame(test_json[:-1], columns=test_json[0].keys())

        # define budget
        budget = test_json[-1]['budget']

        # Instantiate Portfolio class
        pipeline = Portfolio()

        # change Portfolio budget
        pipeline.budget = budget
              
        # feature engineering
        df2 = pipeline.feature_engineering(test_raw)
        
        # data preparation
        df3 = pipeline.data_preparation(df2, model)
        
        # prediction
        df_response = pipeline.get_prediction( model, test_raw, df3 )
        
        return df_response

    else:
        return Response( '{}', status=200, mimetype='application/json' )

if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run( host = "0.0.0.0", port = port)