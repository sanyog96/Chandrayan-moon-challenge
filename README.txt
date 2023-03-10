1) Create a folder 'input' with all input images and 'output' with all output images
2) Please keep aside some ratio of images to use them as validation dataset in folder with names 'input_valid' and 'output_valid'
3) Please locate 'config.py' file in the home folder and update as follows 
	4.1) training data foldername needs to be updated as 'input' and 'output'
	4.2) validation data foldername needs to be updated as 'input_valid' and 'output_valid'
4) Run below command on command line
pip install git+https://github.com/tensorlayer/tensorlayerx.git 
5) For training model, please run below command
python train.py
6) After Training for inference, please run below command
python train.py --mode=eval

You might require some other data files that contains deserts, bare lands, asteroid dataset
and train the model in the same sequence of data mentioned then train it on the cropped images the result will be better