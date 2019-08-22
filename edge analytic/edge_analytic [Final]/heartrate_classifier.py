from sklearn import tree
from mongodb import connections


# Main process for heart rate classifier
# Generate classifier
def main_process():
    global classifier

    # Reconstruct dataset (divide dataset feature and status)
    dataset = {
        "feature": [],
        "status": []
    }

    for document in connections["dataset"].find({}):
        dataset["feature"].append([document["activity"], document["age"], document["heart_rate"]])
        dataset["status"].append(document["status"])

    # Create classifier
    classifier = tree.DecisionTreeClassifier().fit(dataset["feature"], dataset["status"])


# Classify new data
def classify(activity, age, heart_rate):
    global classifier

    new_data = [activity, age, heart_rate]
    result = classifier.predict([new_data])[0]
    print("[Classifier] Status: " + result)
    return result
