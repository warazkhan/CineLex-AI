from kaggle.api.kaggle_api_extended import KaggleApi

# Initialize API
api = KaggleApi()
api.authenticate()

print("Kaggle API Authenticated!")