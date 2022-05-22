import numpy as np
import torch
from sklearn.metrics import top_k_accuracy_score, f1_score
from torch import nn, optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

from validate import validate_model


def train_model(epochs: int,
                model: nn.Module,
                criterion: nn.Module,
                optimizer: optim.Optimizer,
                train_loader: DataLoader,
                val_loader: DataLoader,
                scheduler,
                writer: SummaryWriter,
                device: str,
                save_frequency: int = 5,
                save_best: bool = True,
                save_last: bool = True,
                save_jit: bool = False,
                num_classes: int = None
                ) -> None:
    assert epochs > 0, "epochs must be positive integer."

    train_step = 0
    best_loss = float("inf")
    for epoch in range(epochs):
        running_train_loss = 0
        running_val_loss = 0
        running_train_preds = []
        running_train_y = []
        running_train_raw = []

        model.train()
        for imgs, y in tqdm(train_loader, desc=f"Epoch {epoch:04}: Training"):
            imgs, y = imgs.to(device), y.to(device)

            optimizer.zero_grad()
            preds = model(imgs)
            loss = criterion(preds, y)

            loss.backward()
            optimizer.step()
            class_preds = preds.argmax(dim=1).tolist()
            running_train_preds.extend(class_preds)
            running_train_raw.extend(preds.tolist())
            running_train_y.extend(y.tolist())
            running_train_loss += imgs.shape[0] * loss.item()

            if writer is not None:
                writer.add_scalar("Train/Step Wise Loss", loss, train_step)
                writer.add_scalar("Train/Step Wise Accuracy",
                                  (np.array(class_preds) == np.array(y.tolist())).mean(), train_step)
            if scheduler is not None:
                scheduler.step()
            train_step += 1

        if writer is not None:
            # Train stats
            writer.add_scalar("Train/Epoch Wise Loss", running_train_loss / len(train_loader.dataset), epoch)
            for k in [1, 3, 5]:
                writer.add_scalar(f"Train/Epoch Wise Top {k} Accuracy",
                                  top_k_accuracy_score(running_train_y, running_train_raw, k=k,
                                                       labels=np.arange(num_classes)), epoch)
            writer.add_scalar("Train/Epoch Wise F1-Score", f1_score(running_train_y, running_train_preds,
                                                                    average="macro"), epoch)

        best_loss = validate_model(best_loss, epoch, model, criterion, val_loader, writer, device, save_frequency,
                                   save_best, save_jit, num_classes)

    if save_last:
        val_loss = running_val_loss / len(val_loader.dataset)
        torch.save(model.state_dict(), f"checkpoints/model_ep{epoch:04}_valloss{val_loss:.03f}.pth")
        if save_jit:
            scripted_model = torch.jit.script(model.cuda())
            scripted_model.save(f"checkpoints/gpu-model_ep{epoch:04}_valloss{val_loss:.03f}.jit")
            scripted_model = torch.jit.script(model.cpu())
            scripted_model.save(f"checkpoints/cpu-model_ep{epoch:04}_valloss{val_loss:.03f}.jit")
            model.to(device)
