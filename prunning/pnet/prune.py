import sys
sys.path.append('.')
import os
import argparse

import torch
from torchvision import transforms

from tools.dataset import FaceDataset
from nets.prune_mtcnn import PNet
from prunning.pnet.pruner import PNetPruner
from checkpoint import CheckPoint
import config

# Set device
use_cuda = config.USE_CUDA and torch.cuda.is_available()
# torch.cuda.manual_seed(train_config.manualSeed)
device = torch.device("cuda:1" if use_cuda else "cpu")
torch.backends.cudnn.benchmark = True

# Set dataloader
kwargs = {'num_workers': 8, 'pin_memory': False} if use_cuda else {}
train_data = FaceDataset(os.path.join(config.ANNO_PATH, config.PNET_TRAIN_IMGLIST_FILENAME))
val_data = FaceDataset(os.path.join(config.ANNO_PATH, config.PNET_VAL_IMGLIST_FILENAME))
dataloaders = {'train': torch.utils.data.DataLoader(train_data, 
                        batch_size=config.BATCH_SIZE, shuffle=True, **kwargs),
               'val': torch.utils.data.DataLoader(val_data,
                        batch_size=config.BATCH_SIZE, shuffle=True, **kwargs)
              }

# Set model
model = PNet(is_train=True)
model = model.to(device)
model.load_state_dict(torch.load('pretrained_weights/mtcnn/best_pnet.pth'), strict=True)

# Set checkpoint
# checkpoint = CheckPoint(train_config.save_path)

# Set optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=config.STEPS, gamma=0.1)

# Set trainer
trainer = PNetPruner(config.EPOCHS, dataloaders, model, optimizer, scheduler, device, 0.5, 2)

trainer.prune()
    
# checkpoint.save_model(model, index=epoch, tag=config.SAVE_PREFIX)
            
