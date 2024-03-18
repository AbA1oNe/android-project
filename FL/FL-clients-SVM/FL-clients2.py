import helperUnary
import numpy as np
import flwr as fl
from sklearn.svm import OneClassSVM
from sklearn.metrics import roc_curve
from sklearn.metrics import log_loss, accuracy_score, precision_score, recall_score, f1_score
import warnings
warnings.simplefilter('ignore')


# Create the flower client
class FlowerClient(fl.client.NumPyClient):

    # Get the current local model parameters
    def get_parameters(self, config):
        print(f"Client {client_id} received the parameters.")
        return helperUnary.get_params(model)

    # Train the local model, return the model parameters to the server
    def fit(self, parameters, config):
        print("Parameters before setting: ", parameters)
        helperUnary.set_params(model, parameters)
        print("Parameters after setting: ", model.get_params())

        model.fit(X_train)
        print(f"Training finished for round {config['server_round']}.")

        trained_params = helperUnary.get_params(model)
        print("Trained Parameters: ", trained_params)

        return trained_params, len(X_train), {}

    # Evaluate the local model, return the evaluation result to the server
    def evaluate(self, parameters, config):
        helperUnary.set_params(model, parameters)

        y_true = y_test.astype('int')
        y_pred = model.predict(X_test)
        loss = log_loss(y_true, y_pred, labels=[-1, 1])

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='macro')
        recall = recall_score(y_true, y_pred, average='macro')
        f1 = f1_score(y_true, y_pred, average='macro')
        fprROC, tprROC, threshold = roc_curve(y_true, y_pred, pos_label=1)
        fnrROC = 1 - tprROC #fnrROC == avgFrr
        EER = fprROC[np.nanargmin(np.absolute((fnrROC - fprROC)))]

        line = "-" * 21
        print(line)
        print(f"Accuracy : {accuracy:.8f}")
        print(f"Precision: {precision:.8f}")
        print(f"Recall   : {recall:.8f}")
        print(f"F1 Score : {f1:.8f}")
        print(f"FAR : {np.mean(fprROC):.8f}")
        print(f"FRR : {np.mean(fnrROC):.8f}")
        print(f"TPR : {np.mean(tprROC):.8f}")
        print(f"EER : {EER:.8f}")
        print(line)

        return loss, len(X_test), {"Accuracy": accuracy, "Precision": precision, "Recall": recall, "F1_Score": f1}


if __name__ == "__main__":
    client_id = 2
    print(f"Client {client_id}:\n")

    # Get the dataset for local model
    X_train, X_test, y_test = helperUnary.load_dataset(client_id)

    # Print the label distribution
    #unique, counts = np.unique(y_re, return_counts=True)
    #train_counts = dict(zip(unique, counts))
    #print("Label distribution in the training set:", train_counts)
    unique, counts = np.unique(y_test, return_counts=True)
    test_counts = dict(zip(unique, counts))
    print("Label distribution in the testing set:", test_counts, '\n')

    # Create and fit the local model
    model = OneClassSVM(
        kernel='rbf',
        gamma=1e-7,
        tol=0.001,
        nu=0.5
    )
    model.fit(X_train)

    # Start the client
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=FlowerClient())