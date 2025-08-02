from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import StockPredictionSerializer
from rest_framework import status
from rest_framework.response import Response

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from .utils import save_plot
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from keras.models import load_model

class StockPredictionAPIView(APIView):
  def post(self, request):
    serializer = StockPredictionSerializer(data=request.data)
    if serializer.is_valid():
      ticker = serializer.validated_data['ticker']
      
      # Fetch the data from yfinance
      now = datetime.now()
      start = datetime(now.year - 10, now.month, now.day)
      end = now
      df = yf.download(ticker, start=start, end=end)
      if df.empty:
        return Response({"error": "No data found for the ticker", 'status': status.HTTP_404_NOT_FOUND})
      
      df = df.reset_index()

      # Generate basic plot
      plt.switch_backend('AGG')
      plt.figure(figsize=(12, 5));
      plt.plot(df['Close'], label='Closing Price');
      plt.title(f'Closing price of {ticker}');
      plt.xlabel('Days');
      plt.ylabel('Close Price')
      plt.legend()
      
      # Save the plot to a file
      plot_img_path = f'{ticker}_plot.png'
      plot_img = save_plot(plot_img_path)

      # 100 Days Moving Average
      ma100 = df['Close'].rolling(100).mean()
      plt.switch_backend('AGG')
      plt.figure(figsize=(12, 5));
      plt.plot(df['Close'], label='Closing Price');
      plt.plot(ma100, 'r', label='100 Days Moving Average');
      plt.title(f'100 Days Moving Average of {ticker}');
      plt.xlabel('Days');
      plt.ylabel('Price')
      plt.legend()
      
      # Save the moving average plot to a file
      plot_img_path = f'{ticker}_ma100_plot.png'
      plot_100_dma = save_plot(plot_img_path)
      
      # 200 Days Moving Average
      ma200 = df['Close'].rolling(200).mean()
      plt.switch_backend('AGG')
      plt.figure(figsize=(12, 5));
      plt.plot(df['Close'], label='Closing Price');
      plt.plot(ma100, 'r', label='100 DMA');
      plt.plot(ma200, 'g', label='200 DMA');
      plt.title(f'200 Days of Moving Average {ticker}');
      plt.xlabel('Days');
      plt.ylabel('Price')
      plt.legend()
      
      # Save the moving average plot to a file
      plot_img_path = f'{ticker}_ma200_plot.png'
      plot_200_dma = save_plot(plot_img_path)
      
      # Splitting data into training and testing datasets.
      training_df = pd.DataFrame(df['Close'][0:int(len(df)*0.7)])
      testing_df = pd.DataFrame(df['Close'][int(len(df)*0.7):len(df)])
      
      # Scaling down the data between 0 and 1
      scaler = MinMaxScaler(feature_range=(0, 1))
      
      # Load ML model
      model = load_model('stock_prediction_model.keras')
      
      # Preparing testing data
      past_100_days = training_df.tail(100)
      final_df = pd.concat([past_100_days, testing_df], ignore_index=True)
      input_data = scaler.fit_transform(final_df)
      
      x_test = []
      y_test = []
      for i in range(100, input_data.shape[0]):
          x_test.append(input_data[i-100:i])
          y_test.append(input_data[i, 0])
      x_test, y_test = np.array(x_test), np.array(y_test)
      
      # Making predictions
      y_predicted = model.predict(x_test)
      
      # Revert the scaled prices to original prices
      y_predicted = scaler.inverse_transform(y_predicted)
      y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
      
      # Ploting the final predictions
      plt.switch_backend('AGG')
      plt.figure(figsize=(12, 5))
      plt.plot(y_test, 'r', label='Original Price')
      plt.plot(y_predicted, 'g', label='Predicted Price')
      plt.title(ticker)
      plt.xlabel('Days')
      plt.ylabel('Price')
      plt.legend()
      
      # Save the final plot to a file
      plot_img_path = f'{ticker}_final_prediction.png'
      plot_final = save_plot(plot_img_path)
      
      # Model Evaluation
      # Mean Squared Error
      mse = mean_squared_error(y_test, y_predicted)
      
      # Root Mean Squared Error
      rmse = np.sqrt(mse)
      
      # R-squared
      r2 = r2_score(y_test, y_predicted)
      
      return Response({
        "status": "success", 
        'plot_img': plot_img,
        'plot_100_dma': plot_100_dma,
        'plot_200_dma': plot_200_dma,
        'plot_final': plot_final,
        'mse': mse,
        'rmse': rmse,
        'r2': r2
      })
