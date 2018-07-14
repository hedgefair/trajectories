# Chasing a goal in a dangerous environment with a conditional generative model of the environment

This gif shows our MCTS agent (green) trying to catch the yellow goal while avoiding the cyan obstacles all using a learned dynamics model to imagine the future. 

![alt_text](https://github.com/johannah/trajectories/blob/master/imgs/10-step-fast.gif)

The below image shows the same episode as above with the imagined future model depicted. The first column is the observed state, the second column is the oracle rollout (for human reference only) and the third column is the model rollout that the agent used for planning. 
The fourth column describes model error where red pixels are false negatives (predicted free space where there is an obstacle) and blue pixels indicate false positives (predicted obstacle where there was free space). In the error plot, the predicted goal is plotted in orange over the true yellow goal.

![alt_text](https://github.com/johannah/trajectories/blob/master/imgs/10-step-rollout.gif)

More agent examples can be found at [https://imgur.com/a/6DJbrB1](https://imgur.com/a/6DJbrB1)

--- 
### Implementation 

Please refer to our [paper](https://github.com/johannah/trajectories/blob/master/icml18-vqvae-model-camera-ready.pdf) presented at the PGMRL Workshop at ICML 2018 for implementation details.

To train the environment model, complete the following steps: 

1) Generate a training set in pixel-space of the environment: 
[road.py](https://github.com/johannah/trajectories/blob/master/trajectories/road.py).

2) Train VQ-VAE to learn a discrete latent representation of individual frames:
[train_vqvae.py](https://github.com/johannah/trajectories/blob/master/trajectories/train_vqvae.py).

3) Train a PixelCNN on the latent space:
[train_pixel_cnn.py](https://github.com/johannah/trajectories/blob/master/trajectories/train_pixel_cnn.py).

4) Run MCTS using the learned model: 
[roadway_model.py](https://github.com/johannah/trajectories/blob/master/examples/roadway_model.py).

---
# Below we demonstrate reconstruction error 

Below is a demonstration of the reconstruction from our VQ-VAE model:

![alt_text](https://github.com/johannah/trajectories/blob/master/imgs/true_step_seed_930_vqvae.gif)

Below is a demonstration of the reconstruction from our VAE model:

![alt_text](https://github.com/johannah/trajectories/blob/master/imgs/true_step_seed_930_vae.gif)

---
# Acknowledgements

We based our VQ-VAE implementation on the excellent code from [@Ritesh Kumar](https://github.com/ritheshkumar95/vq-vae-exps). 
The implementation of discretized logistic mixture loss we use is from [@Lucas Caccia](https://github.com/pclucas14/pixel-cnn-pp/blob/master/utils.py).

Thanks to [@kastnerkyle](https://github.com/kastnerkyle) for discussions and advice on all things.

