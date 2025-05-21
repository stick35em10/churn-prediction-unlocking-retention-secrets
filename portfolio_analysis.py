# portfolio_analysis.py

import pandas as pd
import numpy as np

import matplotlib.pyplot     as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble        import RandomForestClassifier
from sklearn.metrics         import classification_report
import joblib
import os

class CreditPortfolioMonitor:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        #print(f"try see self.data[Deposit].tail: {self.data.Deposit.tail}")
        print(f"try see self.data[Deposit].tail: {self.data.tail}")
        self.preprocess_data()
        
    def preprocess_data(self):

        # Converter tipos de dados
        self.data['Transaction_Date']      = pd.to_datetime(self.data['Transaction_Date'])
        self.data['Account_Open_Date']     = pd.to_datetime(self.data['Account_Open_Date'])
        self.data['Last_Transaction_Date'] = pd.to_datetime(self.data['Last_Transaction_Date'])
        
        # Codificar variáveis categóricas
        self.data = pd.get_dummies(self.data, columns=['Gender', 'Account_Type', 'Loan_Type', 'Region', 'Marital_Status'])
        
        # Verificar valores nulos
        null_counts = self.data.isnull().sum()
        print("Contagem de valores nulos por coluna:\n", null_counts)

        # Tratar valores ausentes
        filds_to_null = ["Age","Account_Balance","Transaction_Amount","Loan_Amount","Credit_Score","Annual_Income","Customer_Service_Interactions","Recent_Complaints","Customer_Satisfaction_Score","Churn_Label","Churn_Timeframe"] 
        self.data = self.data[filds_to_null].copy()
        self.data = self.data.fillna(0, inplace=True)

        #print(self.data.dtypes)
        #AttributeError: 'NoneType' object has no attribute 'dtypes'
        print(" pass self.data.fillna(0, inplace=True)")
    
    def analyze_portfolio(self):
        print("star def analyze_portfolio(self):")
        # Análise básica, 
        # TypeError: object of type 'NoneType' has no len()
        analysis = {
            'total_customers' : len(self.data),
            'churn_rate'      : self.data['Churn_Label'].mean(),
            'avg_credit_score': self.data['Credit_Score'].mean(),
            'avg_loan_amount' : self.data['Loan_Amount'].mean(),
            'default_rate'    : (self.data['Loan_Amount'] > self.data['Account_Balance']).mean()
        }
        print(" pass analysis in analyze_portfolio ")

        print("analyze_portfolio(self):# Análise básica analysis = {")

        # Segmentação por características
        segments = {
            'by_age': self.data.groupby(pd.cut(self.data['Age'], bins=[0, 30, 50, 70, 100]))['Churn_Label'].mean(),
            'by_income': self.data.groupby(pd.cut(self.data['Annual_Income'], bins=5))['Churn_Label'].mean(),
            'by_credit_score': self.data.groupby(pd.cut(self.data['Credit_Score'], bins=[0, 300, 600, 850]))['Churn_Label'].mean()
        }
        
        print("\n def analyze_portfolio(self): \n")

        return {'basic_analysis': analysis, 'segmented_analysis': segments}
    
    def build_churn_model(self):
        # Preparar dados para modelagem
        X = self.data.drop(['Customer_ID', 'Churn_Label', 'Churn_Timeframe', 
                           'Transaction_Date', 'Account_Open_Date', 
                           'Last_Transaction_Date'], axis=1, errors='ignore')
        y = self.data['Churn_Label']
        
        # Dividir dados
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Treinar modelo
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Avaliar modelo
        y_pred = model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        # Salvar modelo
        model_path = '/app/models/churn_model.pkl'
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        
        return {'model_performance': report, 'feature_importance': dict(zip(X.columns, model.feature_importances_))}
    
    def generate_reports(self):
        analysis = self.analyze_portfolio()
        model_results = self.build_churn_model()
        
        # Gerar visualizações
        self.plot_analysis(analysis)
        
        return {**analysis, **model_results}
    
    def plot_analysis(self, analysis):
        plt.figure(figsize=(15, 10))
        
        # Gráfico de taxa de churn por idade
        plt.subplot(2, 2, 1)
        analysis['segmented_analysis']['by_age'].plot(kind='bar')
        plt.title('Churn Rate by Age Group')
        plt.ylabel('Churn Rate')
        
        # Gráfico de taxa de churn por renda
        plt.subplot(2, 2, 2)
        analysis['segmented_analysis']['by_income'].plot(kind='bar')
        plt.title('Churn Rate by Income Group')
        plt.ylabel('Churn Rate')
        
        # Gráfico de taxa de churn por score de crédito
        plt.subplot(2, 2, 3)
        analysis['segmented_analysis']['by_credit_score'].plot(kind='bar')
        plt.title('Churn Rate by Credit Score')
        plt.ylabel('Churn Rate')
        
        # Salvar gráficos
        plots_path = '/app/reports/analysis_plots.png'
        os.makedirs(os.path.dirname(plots_path), exist_ok=True)
        plt.tight_layout()
        plt.savefig(plots_path)
        plt.close()

if __name__ == "__main__":
    #datasets/customer_churn_dataset.csv
    #monitor = CreditPortfolioMonitor('/app/data/customer_churn_dataset.csv')
    
    monitor = CreditPortfolioMonitor('datasets/customer_churn_dataset.csv')
    
    results = monitor.generate_reports()
    
    # Salvar resultados em JSON
    import json
    report_path = '/app/reports/portfolio_analysis.json'
    print("report_path")

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Análise do portfólio concluída e relatórios gerados.")