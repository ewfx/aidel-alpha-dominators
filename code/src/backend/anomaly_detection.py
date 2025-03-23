from sklearn.ensemble import IsolationForest
import numpy as np

# Sample transaction features (for simplicity, using random data)
transaction_features = np.random.rand(100, 5)

# Train Isolation Forest model
model = IsolationForest(contamination=0.1)
model.fit(transaction_features)

# Predict anomalies
anomalies = model.predict(transaction_features)
print(anomalies)