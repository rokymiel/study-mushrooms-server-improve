import common.constants
from common.constants import classnames

mushrooms_recognition_model = torchvision.models.resnet50()
mushrooms_recognition_model.fc = torch.nn.Linear(mushrooms_recognition_model.fc.in_features, len(classnames))
current_device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
mushrooms_recognition_model.load_state_dict(torch.load('../nn', map_location=current_device))
mushrooms_recognition_model.eval()


def predict_probs(image):
    preprocess = torchvision.transforms.Compose([
        torchvision.transforms.Resize(256),
        torchvision.transforms.CenterCrop(224),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    tensor = preprocess(image)
    batch = tensor.unsqueeze(0)

    batch = batch.to(current_device)
    mushrooms_recognition_model.to(current_device)
    with torch.no_grad():
        output = mushrooms_recognition_model(batch)

    return torch.nn.functional.softmax(output[0], dim=0)


def recognize(image, model_creator, threshold=0.01):
    probs = predict_probs(image)
    res = []

    for prob, classname in zip(probs, classnames):
        probability = prob.item().__float__()
        if probability > threshold:
            r_model = model_creator(probability, classname)
            res.append(r_model)

    return res
