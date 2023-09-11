
import numpy as np
import tensorflow as tf
from skimage.color import rgb2lab, lab2rgb, rgb2gray, gray2rgb
from skimage.transform import resize
from tensorflow.keras.utils import img_to_array, load_img, array_to_img
from tensorflow.keras.models import load_model
from keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input

#inception = load_model('inception_model.h5')
inception = InceptionResNetV2(weights=None, include_top=True)
inception.graph = tf.compat.v1.get_default_graph()

model=load_model('colorizer.model')

def get_inception_embedding(grey_rgb):
    grey_rgb_resized = resize(grey_rgb ,(1, 299, 299, 3))
    grey_rgb_resized = preprocess_input(grey_rgb_resized)
    embedding = inception.predict(grey_rgb_resized)
    return embedding[0]

def pipeline(path):
    img= img_to_array(load_img(path))/255   # Standardize RGB image array for the RGB-LAB transformation
    img = resize(img ,(256,256))    # (256, 256, 3) standard shape for all images

    # extract l layer from lab
    lab_img= rgb2lab(img)
    l_img = lab_img[:,:,:1]
    assert l_img.shape == (256,256,1) , "L channel matrix shape is wrong"
    
    input0= l_img.reshape((1,)+ l_img.shape)

    # generate gray image 
    gray_img= rgb2gray(img)
    gray_rgb_img= gray2rgb(gray_img)

    input1= get_inception_embedding(gray_rgb_img)
    input1= input1.reshape((1,)+ input1.shape)
    assert input1.shape == (1, 1000) , "input 2 shape is wrong"

    input= [input0, input1]
    ab_predict= model.predict(input)[0]*128
    assert ab_predict.shape == (256,256,2) , "AB channels matrices shape is wrong"

    result_lab= np.zeros(img.shape)
    result_lab[:,:,:1], result_lab[:,:,1:]= l_img, ab_predict    # Give backthe original values range for AB
    result_rgb= lab2rgb(result_lab)

    return array_to_img(result_rgb)