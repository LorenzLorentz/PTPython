from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression

data = load_breast_cancer()
X = data.data
y = data.target

X_train = X[:500, :5]
y_train = y[:500]
X_test = X[500:, :5]
y_test = y[500:]

clf = LogisticRegression(penalty='l2', solver='liblinear', random_state=0)

clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)

print(f"{accuracy:.4f}")

import chromedriver