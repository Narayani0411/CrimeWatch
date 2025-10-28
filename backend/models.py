import torch
import torch.nn as nn
import torchvision.models as models

class CNN_LSTM(nn.Module):
    def __init__(self, embed_dim=512, hidden_dim=256, num_layers=1):
        super(CNN_LSTM, self).__init__()
        base_model = models.resnet18(pretrained=True)
        self.cnn = nn.Sequential(*list(base_model.children())[:-1])
        self.cnn_fc = nn.Linear(base_model.fc.in_features, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (batch, seq_len, C, H, W)
        B, T, C, H, W = x.size()
        x = x.view(B*T, C, H, W)
        with torch.no_grad():  # freeze CNN backbone
            feats = self.cnn(x).view(B*T, -1)
        feats = self.cnn_fc(feats)
        feats = feats.view(B, T, -1)
        lstm_out, _ = self.lstm(feats)
        out = self.fc(lstm_out[:, -1, :])
        return self.sigmoid(out).squeeze()
