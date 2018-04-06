import shutil
import torch
from IPython import embed
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import datasets, transforms
from vq_vae import AutoEncoder, to_scalar
from torch.autograd import Variable
import numpy as np
from torchvision.utils import save_image
import time
from glob import glob
import os
from imageio import imread, imwrite
from PIL import Image


class FroggerDataset(Dataset):
    def __init__(self, root_dir, transform=None, limit=None):
        self.root_dir = root_dir
        self.transform = transform
        search_path = os.path.join(self.root_dir, '*.png')
        self.indexes = glob(search_path)
        if not len(self.indexes):
            print("Error no files found at {}".format(search_path))
            raise
        if limit is not None:
            self.indexes = self.indexes[:min(len(self.indexes), limit)]

    def __len__(self):
        return len(self.indexes)

    def __getitem__(self, idx):
        img_name = self.indexes[idx]
        image = imread(img_name)
        image = image[:,:,None].astype(np.float32)
        reward = int(img_name.split('_')[-1].split('.png')[0])
        if self.transform is not None:
            image = self.transform(image)

        return image,reward


def train(epoch,model,optimizer,train_loader,do_checkpoint,do_use_cuda,model_savepath):
    train_loss = []
    for batch_idx, (data, _) in enumerate(train_loader):
        start_time = time.time()
        if do_use_cuda:
            x = Variable(data, requires_grad=False).cuda()
        else:
            x = Variable(data, requires_grad=False)

        optimizer.zero_grad()

        x_tilde, z_e_x, z_q_x = model(x)
        z_q_x.retain_grad()

        loss_1 = F.binary_cross_entropy(x_tilde, x)
        loss_1.backward(retain_graph=True)
        model.embedding.zero_grad()
        z_e_x.backward(z_q_x.grad, retain_graph=True)

        loss_2 = 0 * F.mse_loss(z_q_x, z_e_x.detach())
        # loss_2.backward(retain_graph=True)
        loss_3 = 0 * F.mse_loss(z_e_x, z_q_x.detach())
        # loss_3.backward()
        optimizer.step()
        train_loss.append(to_scalar([loss_1, loss_2]))
        if not batch_idx%10:
            print 'Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {} Time: {}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / float(len(train_loader)),
                np.asarray(train_loss).mean(0),
                time.time() - start_time
            )

    if do_checkpoint:
        state = {'epoch':epoch,
                 'state_dict':model.state_dict(),
                 'loss':np.asarray(train_loss).mean(0),
                 'optimizer':optimizer.state_dict(),
                 }
        save_checkpoint(state, filename=model_savepath)
    return model, optimizer

def test(x,model,save_img_path=None):
    x_tilde, _, _ = model(x)
    x_cat = torch.cat([x, x_tilde], 0)
    images = x_cat.cpu().data
    if save_img_path is not None:
        save_image(images, save_img_path, nrow=1)

def save_checkpoint(state, is_best=False, filename='model.pkl'):
    torch.save(state, filename)
    if is_best:
        bestpath = os.path.join(os.path.split(filename)[0], 'model_best.pkl')
        shutil.copyfile(filename, bestpath)

if __name__ == '__main__':
    import argparse
    default_base_datadir = 'saved/'
    default_model_savepath = os.path.join(default_base_datadir, 'frogger_model.pkl')

    parser = argparse.ArgumentParser(description='train vq-vae for frogger images')
    parser.add_argument('-c', '--cuda', action='store_true', default=False)
    parser.add_argument('-d', '--datadir', default=default_base_datadir)
    parser.add_argument('-s', '--model_savepath', default=default_model_savepath)
    parser.add_argument('-l', '--model_loadpath', default=None)

    args = parser.parse_args()
    train_data_dir = os.path.join(args.datadir, 'imgs_train')
    test_data_dir =  os.path.join(args.datadir, 'imgs_test')
    use_cuda = args.cuda

    if args.model_loadpath is not None:
        if os.path.exists(args.model_loadpath):
            vmodel = torch.load(args.model_loadpath)
            opt = torch.optim.Adam(vmodel.parameters(), lr=1e-3)
            opt.load_state_dict(checkpoint['optimizer'])
            print('loaded checkpoint at epoch: {} from {}'.format(epoch, args.model_loadpath))
        else:
            print('could not find checkpoint at {}'.format(args.model_loadpath))
    else:
        if use_cuda:
            vmodel = AutoEncoder().cuda()
        else:
            vmodel = AutoEncoder()
        opt = torch.optim.Adam(model.parameters(), lr=1e-3)

    data_train_loader = DataLoader(FroggerDataset(train_data_dir, 
                                   transform=transforms.ToTensor()), 
                                   batch_size=64, shuffle=True)
    data_test_loader = DataLoader(FroggerDataset(test_data_dir, 
                                  transform=transforms.ToTensor()), 
                                  batch_size=32, shuffle=True)
    test_data = list(test_loader)
    for i in xrange(100):
        vmodel, opt = train(i,vmodel,opt,data_train_loader,
                            do_checkpoint=True,use_cuda=use_cuda,
                            args.model_savepath)
        if use_cuda:
            x_test = Variable(test_data[0][0]).cuda()
        else:
            x_test = Variable(test_data[0][0])
        test(vmodel,x_test)




