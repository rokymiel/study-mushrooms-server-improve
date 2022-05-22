import numpy as np
import torch
from sklearn.metrics import top_k_accuracy_score, f1_score
from torch import nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


def validate_model(best_loss: float,
                   epoch: int,
                   model: nn.Module,
                   criterion: nn.Module,
                   val_loader: DataLoader,
                   writer: SummaryWriter,
                   device: str,
                   save_frequency: int = 5,
                   save_best: bool = True,
                   save_jit: bool = False,
                   num_classes: int = None
                   ) -> float:
    running_val_loss = 0
    running_val_preds = []
    running_val_y = []
    running_val_raw = []
    val_step = epoch * len(val_loader)

    model.eval()
    with torch.inference_mode():
        for imgs, y in tqdm(val_loader, desc=f"Epoch {epoch:04}: Validation"):
            imgs, y = imgs.to(device), y.to(device)

            preds = model(imgs)
            loss = criterion(preds, y)

            class_preds = preds.argmax(dim=1).tolist()
            running_val_preds.extend(class_preds)
            running_val_raw.extend(preds.tolist())
            running_val_y.extend(y.tolist())
            running_val_loss += imgs.shape[0] * loss.item()

            if writer is not None:
                writer.add_scalar("Validation/Step Wise Loss", loss, val_step)
                writer.add_scalar("Validation/Step Wise Accuracy",
                                  (np.array(class_preds) == np.array(y.tolist())).mean(), val_step)
            val_step += 1

    val_loss = running_val_loss / len(val_loader.dataset)
    if writer is not None:
        writer.add_scalar("Validation/Epoch Wise Loss", val_loss, epoch)
        for k in [1, 3, 5]:
            writer.add_scalar(f"Validation/Epoch Wise Top {k} Accuracy",
                              top_k_accuracy_score(running_val_y, running_val_raw, k=k,
                                                   labels=np.arange(num_classes)), epoch)
        writer.add_scalar("Validation/Epoch Wise F1-Score", f1_score(running_val_y, running_val_preds,
                                                                     average="macro"), epoch)

    if save_frequency is not None and (epoch + 1) % save_frequency == 0 or \
            save_best and val_loss < best_loss:
        best_loss = val_loss
        torch.save(model.state_dict(), f"checkpoints/model_ep{epoch:04}_valloss{val_loss:.03f}.pth")
        if save_jit:
            scripted_model = torch.jit.script(model.cuda())
            scripted_model.save(f"checkpoints/gpu-model_ep{epoch:04}_valloss{val_loss:.03f}.jit")
            scripted_model = torch.jit.script(model.cpu())
            scripted_model.save(f"checkpoints/cpu-model_ep{epoch:04}_valloss{val_loss:.03f}.jit")
            model.to(device)
    return best_loss
