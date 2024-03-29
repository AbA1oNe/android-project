import RFhelper
import numpy as np
import flwr as fl
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from imblearn.over_sampling import SMOTE
from sklearn.metrics import roc_curve
from sklearn.metrics import log_loss, accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.simplefilter('ignore')


# Create the flower client
class FlowerClient(fl.client.NumPyClient):

    # Get the current local model parameters
    def get_parameters(self, config):
        print(f"Client {client_id} received the parameters.")
        return RFhelper.get_params(model)

    # Train the local model, return the model parameters to the server
    def fit(self, parameters, config):
        print("Parameters before setting: ", parameters)
        RFhelper.set_params(model, parameters)
        print("Parameters after setting: ", model.get_params())

        model.fit(X_re, y_re)
        print(f"Training finished for round {config['server_round']}.")

        trained_params = RFhelper.get_params(model)
        print("Trained Parameters: ", trained_params)

        return trained_params, len(X_re), {}

    # Evaluate the local model, return the evaluation result to the server
    def evaluate(self, parameters, config):
        RFhelper.set_params(model, parameters)

        y_true = y_test.astype('int')
        y_pred = model.predict(X_test)
        loss = log_loss(y_true, y_pred, labels=[0, 1])

        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()

        accuracyCalc = (tp+tn)/(tp+tn+fp+fn)
        precisionCalc = tp/(tp+fp)
        tpr = tp/(tp+fn)
        far = fp/(fp+tn)
        frr = fn/(fn+tp)

        accuracy = accuracy_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred, average='binary', pos_label=1)
        f1 = f1_score(y_true, y_pred, average='binary', pos_label=1)
        fprROC, tprROC, threshold = roc_curve(y_test.astype('int'), y_pred, pos_label=1)
        fnrROC = 1 - tprROC #fnrROC == avgFrr
        EER = fprROC[np.nanargmin(np.absolute((fnrROC - fprROC)))]

        line = "-" * 21
        print(line)
        print(f"Accuracy : {accuracy:.8f}")
        print(f"accuracyCalc : {accuracyCalc:.8f}")
        print(f"precisionCalc: {precisionCalc:.8f}")
        print(f"Recall   : {recall:.8f}")
        print(f"F1 Score : {f1:.8f}")
        print(f"FAR : {far:.8f}")
        print(f"FRR : {frr:.8f}")
        print(f"TPR : {tpr:.8f}")
        print(f"EER : {EER:.8f}")
        print(line)

        return loss, len(X_test), {"Accuracy": accuracy, "Precision": precisionCalc, "Recall": recall, "F1_Score": f1}


if __name__ == "__main__":
    client_id = 7
    print(f"Client {client_id}:\n")

    # Get the dataset for local model
    X_train, y_train, X_test, y_test = RFhelper.load_dataset(client_id)
    #X_re, y_re = RandomUnderSampler(random_state=42).fit_resample(X_train, y_train.astype('int'))
    X_re, y_re = SMOTE(random_state=42, k_neighbors=2).fit_resample(X_train, y_train.astype('int'))

    # Print the label distribution
    unique, counts = np.unique(y_re, return_counts=True)
    train_counts = dict(zip(unique, counts))
    print("Label distribution in the training set:", train_counts)
    unique, counts = np.unique(y_test, return_counts=True)
    test_counts = dict(zip(unique, counts))
    print("Label distribution in the testing set:", test_counts, '\n')

    # Create and fit the local model
    model = RandomForestClassifier(
        class_weight='balanced',
        criterion='entropy',
        n_estimators=100,
        max_depth=40,
        min_samples_split=2,
        min_samples_leaf=2,
    )
    model.fit(X_re.astype(np.float32), y_re.astype('int'))

    # Start the client
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=FlowerClient())