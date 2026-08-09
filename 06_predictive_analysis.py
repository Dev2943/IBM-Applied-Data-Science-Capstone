"""
Capstone step 6 — Predictive analysis (classification).
Builds, tunes and evaluates four models, then saves the two charts
needed for slides 43 and 44.

Output: slide43_model_accuracy.png, slide44_confusion_matrix.png
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn import preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, classification_report

DATA1 = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
         "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")
DATA2 = ("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
         "IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_3.csv")

data = pd.read_csv(DATA1)
X = pd.read_csv(DATA2)

# ---------------------------------------------------------------- prepare
Y = data['Class'].to_numpy()

transform = preprocessing.StandardScaler()
X = transform.fit_transform(X)

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=2)
print("Train size:", X_train.shape[0], " Test size:", X_test.shape[0])

results = {}

# ---------------------------------------------------------------- logistic
parameters_lr = {'C': [0.01, 0.1, 1], 'penalty': ['l2'], 'solver': ['lbfgs']}
logreg_cv = GridSearchCV(LogisticRegression(), parameters_lr, cv=10)
logreg_cv.fit(X_train, Y_train)
print("\nLogistic Regression")
print("  best params:", logreg_cv.best_params_)
print("  best CV accuracy:", round(logreg_cv.best_score_, 4))
results['Logistic Regression'] = logreg_cv.score(X_test, Y_test)

# ---------------------------------------------------------------- SVM
parameters_svm = {
    'kernel': ('linear', 'rbf', 'poly', 'sigmoid'),
    'C': np.logspace(-3, 3, 5),
    'gamma': np.logspace(-3, 3, 5)
}
svm_cv = GridSearchCV(SVC(), parameters_svm, cv=10)
svm_cv.fit(X_train, Y_train)
print("\nSupport Vector Machine")
print("  best params:", svm_cv.best_params_)
print("  best CV accuracy:", round(svm_cv.best_score_, 4))
results['SVM'] = svm_cv.score(X_test, Y_test)

# ---------------------------------------------------------------- tree
parameters_tree = {
    'criterion': ['gini', 'entropy'],
    'splitter': ['best', 'random'],
    'max_depth': [2 * n for n in range(1, 10)],
    'max_features': ['sqrt', 'log2'],
    'min_samples_leaf': [1, 2, 4],
    'min_samples_split': [2, 5, 10]
}
tree_cv = GridSearchCV(DecisionTreeClassifier(random_state=2),
                       parameters_tree, cv=10)
tree_cv.fit(X_train, Y_train)
print("\nDecision Tree")
print("  best params:", tree_cv.best_params_)
print("  best CV accuracy:", round(tree_cv.best_score_, 4))
results['Decision Tree'] = tree_cv.score(X_test, Y_test)

# ---------------------------------------------------------------- KNN
parameters_knn = {
    'n_neighbors': list(range(1, 11)),
    'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
    'p': [1, 2]
}
knn_cv = GridSearchCV(KNeighborsClassifier(), parameters_knn, cv=10)
knn_cv.fit(X_train, Y_train)
print("\nK-Nearest Neighbours")
print("  best params:", knn_cv.best_params_)
print("  best CV accuracy:", round(knn_cv.best_score_, 4))
results['KNN'] = knn_cv.score(X_test, Y_test)

# ---------------------------------------------------------------- slide 43
print("\n--- Test set accuracy ---")
for name, score in results.items():
    print(f"  {name:22s} {score:.4f}")

best_name = max(results, key=results.get)
print("\nBest model:", best_name)

plt.figure(figsize=(9, 5))
bars = plt.bar(list(results.keys()), list(results.values()), color="#1f77b4")
for b, v in zip(bars, results.values()):
    plt.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.3f}",
             ha='center', fontsize=11)
plt.ylabel("Test Accuracy")
plt.title("Classification Accuracy by Model")
plt.ylim(0, 1.05)
plt.tight_layout()
plt.savefig("slide43_model_accuracy.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------- slide 44
best_model = {'Logistic Regression': logreg_cv, 'SVM': svm_cv,
              'Decision Tree': tree_cv, 'KNN': knn_cv}[best_name]
yhat = best_model.predict(X_test)

cm = confusion_matrix(Y_test, yhat)
print("\nConfusion matrix:\n", cm)
print("\n", classification_report(Y_test, yhat,
                                  target_names=['did not land', 'landed']))

plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title(f'Confusion Matrix — {best_name}')
plt.xticks([0.5, 1.5], ['did not land', 'landed'])
plt.yticks([0.5, 1.5], ['did not land', 'landed'], rotation=0)
plt.tight_layout()
plt.savefig("slide44_confusion_matrix.png", dpi=150, bbox_inches="tight")
plt.close()

print("\nSaved slide43_model_accuracy.png and slide44_confusion_matrix.png")
