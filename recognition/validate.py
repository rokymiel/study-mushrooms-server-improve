import torch
import torchvision

from common.constants import classnames

mushrooms_recognition_model = torchvision.models.resnet50()
mushrooms_recognition_model.fc = torch.nn.Linear(mushrooms_recognition_model.fc.in_features, len(classnames))
device = torch.device('cpu')
mushrooms_recognition_model.load_state_dict(torch.load('nn', map_location=device))
mushrooms_recognition_model.eval()