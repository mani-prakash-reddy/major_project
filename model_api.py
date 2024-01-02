from flask import Flask, request, jsonify
import torch
import torch.nn as nn

app = Flask(__name__)


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2, hidden_size3, output_size):
        super(LSTMModel, self).__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_size1, batch_first=True)
        self.dropout1 = nn.Dropout(0.2)
        self.lstm2 = nn.LSTM(hidden_size1, hidden_size2, batch_first=True)
        self.dropout2 = nn.Dropout(0.2)
        self.lstm3 = nn.LSTM(hidden_size2, hidden_size3, batch_first=True)
        self.dropout3 = nn.Dropout(0.2)
        self.fc1 = nn.Linear(hidden_size3, 50)
        self.dropout4 = nn.Dropout(0.2)
        self.fc2 = nn.Linear(50, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        out, _ = self.lstm1(x)
        out = self.dropout1(out)
        out, _ = self.lstm2(out)
        out = self.dropout2(out)
        out, _ = self.lstm3(out)
        out = self.dropout3(out)
        out = out[:, -1, :]
        out = torch.relu(self.fc1(out))
        out = self.dropout4(out)
        out = self.sigmoid(self.fc2(out))
        return out


# Load the saved model
input_size = 7
hidden_size1 = 100
hidden_size2 = 50
hidden_size3 = 25
output_size = 1
model = LSTMModel(input_size, hidden_size1, hidden_size2,
                  hidden_size3, output_size)
model.load_state_dict(torch.load('model.pth'))
model.eval()


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    inputs = torch.tensor(data['inputs']).unsqueeze(0).unsqueeze(2)
    outputs = model(inputs)
    prediction = outputs.item()
    return jsonify({'prediction': prediction})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
