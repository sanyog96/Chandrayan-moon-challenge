from easydict import EasyDict as edict
import json

config = edict()
config.TRAIN = edict()
config.TRAIN.batch_size = 16 # [16] use 8 if your GPU memory is small
config.TRAIN.lr_init = 1e-4
config.TRAIN.beta1 = 0.9

## initialize G
config.TRAIN.n_epoch_init = 100
    # config.TRAIN.lr_decay_init = 0.1
    # config.TRAIN.decay_every_init = int(config.TRAIN.n_epoch_init / 2)

## adversarial learning (SRGAN)
config.TRAIN.n_epoch = 200
config.TRAIN.lr_decay = 0.1
config.TRAIN.decay_every = int(config.TRAIN.n_epoch / 2)

## train set location
config.TRAIN.hr_img_path = '/home/aesicd_42/Desktop/tejas/Hyundai_project/Karthi/Inter_IIT/Demo/HR/'
config.TRAIN.lr_img_path = '/home/aesicd_42/Desktop/tejas/Hyundai_project/Karthi/Inter_IIT/Demo/LR/'

config.VALID = edict()
## test set location
config.VALID.hr_img_path = '/home/aesicd_42/Desktop/tejas/Hyundai_project/Karthi/Inter_IIT/Val_HR/'
config.VALID.lr_img_path = '/home/aesicd_42/Desktop/tejas/Hyundai_project/Karthi/Inter_IIT/Val_LR/'

def log_config(filename, cfg):
    with open(filename, 'w') as f:
        f.write("================================================\n")
        f.write(json.dumps(cfg, indent=4))
        f.write("\n================================================\n")
