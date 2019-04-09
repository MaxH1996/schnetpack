import os

import numpy as np
import schnetpack as spk


def evaluate(args, model, train_loader, val_loader, test_loader, device,
             metrics):

    header = []
    results = []
    if "train" in args.split:
        header += ["Train MAE", "Train RMSE"]
        results += evaluate_dataset(metrics, model, train_loader, device)
    if "val" in args.split:
        header += ["Val MAE", "Val RMSE"]
        results += evaluate_dataset(metrics, model, val_loader, device)

    if "test" in args.split:
        header += ["Test MAE", "Test RMSE"]
        results += evaluate_dataset(metrics, model, test_loader, device)
    header = " ".join(header)
    results = np.array(results)

    np.savetxt(
        os.path.join(args.modelpath, "evaluation.txt"),
        results,
        header=header,
        fmt="%.5f",
    )


def evaluate_dataset(metrics, model, loader, device):
    for metric in metrics:
        metric.reset()

    for batch in loader:
        batch = {k: v.to(device) for k, v in batch.items()}
        result = model(batch)

        for metric in metrics:
            metric.add_batch(batch, result)

    results = [metric.aggregate() for metric in metrics]
    return results
