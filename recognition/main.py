import os

import hydra
import numpy as np
import torch.optim.optimizer
from omegaconf import DictConfig
from torch.optim import lr_scheduler
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
from torchvision.datasets import ImageFolder

from train import train_model


def get_train_val_loaders(cfg: DictConfig) -> (DataLoader, DataLoader):
    train_ds = ImageFolder(cfg.data.train.dir, transform=hydra.utils.instantiate(cfg.data.train.transforms))
    val_ds = ImageFolder(cfg.data.val.dir, transform=hydra.utils.instantiate(cfg.data.val.transforms))

    train_loader = DataLoader(train_ds, batch_size=cfg.general.train_batch_size,
                              shuffle=True, num_workers=cfg.general.num_workers, drop_last=True,
                              worker_init_fn=lambda wid: np.random.seed(wid + 10))
    val_loader = DataLoader(val_ds, batch_size=cfg.general.val_batch_size,
                            num_workers=cfg.general.num_workers,
                            worker_init_fn=lambda wid: np.random.seed(wid + 10))

    return train_loader, val_loader


@hydra.main(config_path="configs", config_name="default")
def main(cfg: DictConfig) -> None:
    os.makedirs("checkpoints/", exist_ok=True)
    if cfg.general.seed is not None:
        torch.manual_seed(cfg.general.seed)

    DEVICE = cfg.general.device
    # Datasets and loaders
    train_loader, val_loader = get_train_val_loaders(cfg)

    # Model
    model = hydra.utils.instantiate(cfg.model.net)
    model.to(DEVICE)
    print(f"Model #parameters: {sum([p.numel() for p in model.parameters()]) / 1e6:.3f} M")

    # Criterion
    criterion = hydra.utils.instantiate(cfg.loss)

    # Optimizer
    OptimizerClass = hydra.utils.get_class(cfg.optimizer.type)
    optimizer = OptimizerClass(model.parameters(), **cfg.optimizer.params)

    # Scheduler
    scheduler = None
    if cfg.scheduler is not None:
        SchedulerClass = hydra.utils.get_class(cfg.scheduler.type)
        if issubclass(SchedulerClass, lr_scheduler.LambdaLR):
            lambda_rule = hydra.utils.instantiate(cfg.scheduler.lambda_fn)

            scheduler = SchedulerClass(optimizer, lambda_rule)
        elif issubclass(SchedulerClass, lr_scheduler.ExponentialLR):
            gamma = cfg.scheduler.gamma

            scheduler = SchedulerClass(optimizer, gamma)
        elif issubclass(SchedulerClass, lr_scheduler.StepLR):
            step_size = cfg.scheduler.step_size
            gamma = cfg.scheduler.gamma

            scheduler = SchedulerClass(optimizer, step_size, gamma)
        else:
            raise ValueError(f"Unknown or unsupported scheduler type: {SchedulerClass}")

    writer = None
    if cfg.logging.log:
        writer = SummaryWriter(cfg.general.exp_name + "_log", flush_secs=5)

    train_model(epochs=cfg.general.epochs,
                model=model,
                criterion=criterion,
                optimizer=optimizer,
                train_loader=train_loader,
                val_loader=val_loader,
                scheduler=scheduler,
                writer=writer,
                device=DEVICE,
                save_frequency=cfg.logging.save_frequency,
                save_last=cfg.logging.save_last,
                save_best=cfg.logging.save_best,
                save_jit=cfg.logging.save_jit,
                num_classes=cfg.model.net.num_classes)


if __name__ == "__main__":
    main()
