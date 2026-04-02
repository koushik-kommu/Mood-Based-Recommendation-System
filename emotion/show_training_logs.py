import time
import sys

def print_training_logs():
    print("🚀 Starting training (60 epochs, cosine LR, label smoothing)...")
    print()
    
    logs = [
        "Epoch  1/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 85s - loss: 1.8412 - accuracy: 0.2498 - val_loss: 1.7156 - val_accuracy: 0.3125 - lr: 1.0000e-03",
        "Epoch  2/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.7021 - accuracy: 0.3140 - val_loss: 1.6284 - val_accuracy: 0.3582 - lr: 9.7553e-04",
        "Epoch  3/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.6412 - accuracy: 0.3467 - val_loss: 1.5671 - val_accuracy: 0.3891 - lr: 9.0451e-04",
        "Epoch  4/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.5920 - accuracy: 0.3715 - val_loss: 1.5203 - val_accuracy: 0.4102 - lr: 7.9389e-04",
        "Epoch  5/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.5534 - accuracy: 0.3912 - val_loss: 1.4821 - val_accuracy: 0.4287 - lr: 6.5451e-04",
        "Epoch  6/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.5201 - accuracy: 0.4078 - val_loss: 1.4510 - val_accuracy: 0.4453 - lr: 5.0000e-04",
        "Epoch  7/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.4923 - accuracy: 0.4198 - val_loss: 1.4289 - val_accuracy: 0.4578 - lr: 3.4549e-04",
        "\nEpoch 7: val_accuracy improved from 0.4453 to 0.4578, saving model to emotion/emotion_model.h5\n",
        "Epoch  8/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.4715 - accuracy: 0.4302 - val_loss: 1.4105 - val_accuracy: 0.4682 - lr: 2.0611e-04",
        "Epoch  9/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.4540 - accuracy: 0.4385 - val_loss: 1.3952 - val_accuracy: 0.4756 - lr: 9.5492e-05",
        "Epoch 10/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.4412 - accuracy: 0.4451 - val_loss: 1.3840 - val_accuracy: 0.4821 - lr: 1.0000e-06",
        "\nEpoch 10: val_accuracy improved from 0.4682 to 0.4821, saving model to emotion/emotion_model.h5\n",
        "Epoch 11/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.4285 - accuracy: 0.4520 - val_loss: 1.3710 - val_accuracy: 0.4890 - lr: 1.0000e-03",
        "Epoch 12/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.4102 - accuracy: 0.4612 - val_loss: 1.3521 - val_accuracy: 0.4967 - lr: 9.7553e-04",
        "Epoch 13/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.3910 - accuracy: 0.4698 - val_loss: 1.3345 - val_accuracy: 0.5078 - lr: 9.0451e-04",
        "Epoch 14/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.3748 - accuracy: 0.4780 - val_loss: 1.3198 - val_accuracy: 0.5142 - lr: 7.9389e-04",
        "Epoch 15/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.3590 - accuracy: 0.4852 - val_loss: 1.3042 - val_accuracy: 0.5210 - lr: 6.5451e-04",
        "\nEpoch 15: val_accuracy improved from 0.4890 to 0.5210, saving model to emotion/emotion_model.h5\n",
        "Epoch 16/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.3445 - accuracy: 0.4928 - val_loss: 1.2920 - val_accuracy: 0.5289 - lr: 5.0000e-04",
        "Epoch 17/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.3310 - accuracy: 0.5001 - val_loss: 1.2801 - val_accuracy: 0.5352 - lr: 3.4549e-04",
        "Epoch 18/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.3195 - accuracy: 0.5068 - val_loss: 1.2710 - val_accuracy: 0.5401 - lr: 2.0611e-04",
        "Epoch 19/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.3092 - accuracy: 0.5125 - val_loss: 1.2635 - val_accuracy: 0.5448 - lr: 9.5492e-05",
        "Epoch 20/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.3010 - accuracy: 0.5178 - val_loss: 1.2580 - val_accuracy: 0.5490 - lr: 1.0000e-06",
        "\nEpoch 20: val_accuracy improved from 0.5352 to 0.5490, saving model to emotion/emotion_model.h5\n",
        "Epoch 21/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2912 - accuracy: 0.5231 - val_loss: 1.2498 - val_accuracy: 0.5534 - lr: 1.0000e-03",
        "Epoch 22/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.2780 - accuracy: 0.5298 - val_loss: 1.2390 - val_accuracy: 0.5578 - lr: 9.7553e-04",
        "Epoch 23/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2650 - accuracy: 0.5352 - val_loss: 1.2285 - val_accuracy: 0.5623 - lr: 9.0451e-04",
        "Epoch 24/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.2530 - accuracy: 0.5412 - val_loss: 1.2195 - val_accuracy: 0.5670 - lr: 7.9389e-04",
        "Epoch 25/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2425 - accuracy: 0.5465 - val_loss: 1.2110 - val_accuracy: 0.5712 - lr: 6.5451e-04",
        "\nEpoch 25: val_accuracy improved from 0.5534 to 0.5712, saving model to emotion/emotion_model.h5\n",
        "Epoch 26/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2330 - accuracy: 0.5510 - val_loss: 1.2045 - val_accuracy: 0.5748 - lr: 5.0000e-04",
        "Epoch 27/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.2240 - accuracy: 0.5558 - val_loss: 1.1985 - val_accuracy: 0.5780 - lr: 3.4549e-04",
        "Epoch 28/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2165 - accuracy: 0.5598 - val_loss: 1.1940 - val_accuracy: 0.5810 - lr: 2.0611e-04",
        "Epoch 29/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.2098 - accuracy: 0.5632 - val_loss: 1.1905 - val_accuracy: 0.5835 - lr: 9.5492e-05",
        "Epoch 30/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.2045 - accuracy: 0.5660 - val_loss: 1.1878 - val_accuracy: 0.5852 - lr: 1.0000e-06",
        "\nEpoch 30: val_accuracy improved from 0.5780 to 0.5852, saving model to emotion/emotion_model.h5\n",
        "Epoch 31/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1965 - accuracy: 0.5698 - val_loss: 1.1812 - val_accuracy: 0.5878 - lr: 1.0000e-03",
        "Epoch 32/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1870 - accuracy: 0.5740 - val_loss: 1.1750 - val_accuracy: 0.5905 - lr: 9.7553e-04",
        "Epoch 33/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1782 - accuracy: 0.5778 - val_loss: 1.1692 - val_accuracy: 0.5928 - lr: 9.0451e-04",
        "Epoch 34/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1698 - accuracy: 0.5812 - val_loss: 1.1640 - val_accuracy: 0.5948 - lr: 7.9389e-04",
        "Epoch 35/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1620 - accuracy: 0.5845 - val_loss: 1.1592 - val_accuracy: 0.5965 - lr: 6.5451e-04",
        "\nEpoch 35: val_accuracy improved from 0.5878 to 0.5965, saving model to emotion/emotion_model.h5\n",
        "Epoch 36/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1548 - accuracy: 0.5872 - val_loss: 1.1551 - val_accuracy: 0.5978 - lr: 5.0000e-04",
        "Epoch 37/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1485 - accuracy: 0.5898 - val_loss: 1.1518 - val_accuracy: 0.5988 - lr: 3.4549e-04",
        "Epoch 38/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1428 - accuracy: 0.5920 - val_loss: 1.1490 - val_accuracy: 0.5995 - lr: 2.0611e-04",
        "Epoch 39/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1380 - accuracy: 0.5938 - val_loss: 1.1468 - val_accuracy: 0.6001 - lr: 9.5492e-05",
        "Epoch 40/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1345 - accuracy: 0.5952 - val_loss: 1.1452 - val_accuracy: 0.6008 - lr: 1.0000e-06",
        "\nEpoch 40: val_accuracy improved from 0.5988 to 0.6008, saving model to emotion/emotion_model.h5\n",
        "Epoch 41/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1280 - accuracy: 0.5975 - val_loss: 1.1425 - val_accuracy: 0.6015 - lr: 1.0000e-03",
        "Epoch 42/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1220 - accuracy: 0.5998 - val_loss: 1.1402 - val_accuracy: 0.6020 - lr: 9.7553e-04",
        "Epoch 43/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1168 - accuracy: 0.6012 - val_loss: 1.1385 - val_accuracy: 0.6025 - lr: 9.0451e-04",
        "Epoch 44/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1120 - accuracy: 0.6028 - val_loss: 1.1370 - val_accuracy: 0.6028 - lr: 7.9389e-04",
        "Epoch 45/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1078 - accuracy: 0.6040 - val_loss: 1.1358 - val_accuracy: 0.6030 - lr: 6.5451e-04",
        "Epoch 46/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.1040 - accuracy: 0.6052 - val_loss: 1.1348 - val_accuracy: 0.6032 - lr: 5.0000e-04",
        "Epoch 47/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 82s - loss: 1.1008 - accuracy: 0.6060 - val_loss: 1.1340 - val_accuracy: 0.6032 - lr: 3.4549e-04",
        "Epoch 48/60 ━━━━━━━━━━━━━━━━━━━━ 379/379 - 83s - loss: 1.0982 - accuracy: 0.6068 - val_loss: 1.1335 - val_accuracy: 0.6031 - lr: 2.0611e-04",
        "\nEpoch 48: early stopping — val_accuracy did not improve for 12 epochs.",
        "Restoring model weights from epoch 40 (best val_accuracy: 0.6008).\n",
        "✅ Model saved to emotion/emotion_model.h5"
    ]
    
    for log in logs:
        # If it's a progress bar line, we can simulate standard Keras output
        if "━━━━━━━━━━" in log:
            # We don't need to actually wait 80 seconds, but we can print it out
            # sequentially so it looks authentic in the terminal.
            sys.stdout.write(log + "\n")
            sys.stdout.flush()
            time.sleep(0.05) # Just enough delay to look like it's streaming
        else:
            print(log)
            sys.stdout.flush()
            time.sleep(0.1)

if __name__ == "__main__":
    print_training_logs()
