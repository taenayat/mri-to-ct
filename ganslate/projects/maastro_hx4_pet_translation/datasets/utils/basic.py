import numpy as np
import torch
import SimpleITK as sitk

from ganslate.utils import sitk_utils
from ganslate.data.utils.body_mask import get_body_mask
from ganslate.data.utils.normalization import min_max_normalize


# Body mask settings
OUT_OF_BODY_HU = -1024
OUT_OF_BODY_SUV = 0
HU_THRESHOLD = -300 



def apply_body_mask(image_dict, generate_body_mask=False):

    # If body mask doesn't exist, then create one from the available CT using morph. ops
    if generate_body_mask: 
        assert image_dict['body-mask'] is None
        assert any(['CT' in k for k in image_dict.keys()])  # There should be a CT in the dict to be able to generate a mask
        ct_image_name = [k for k in image_dict.keys() if 'CT' in k][0]
        image_dict['body-mask'] = get_body_mask(image_dict[ct_image_name], HU_THRESHOLD)

    # Apply masking to any CT or PET image present in image_dict
    assert image_dict['body-mask'] is not None
    body_mask = image_dict['body-mask']
    for k in image_dict.keys():
        if 'PET' in k:
            image_dict[k] = np.where(body_mask, image_dict[k], OUT_OF_BODY_SUV)
        elif 'CT' in k:
            image_dict[k] = np.where(body_mask, image_dict[k], OUT_OF_BODY_HU)

    return image_dict


def clip_and_min_max_normalize(tensor, min_value, max_value):
    tensor = torch.clamp(tensor, min_value, max_value)
    tensor = min_max_normalize(tensor, min_value, max_value)
    return tensor


def sitk2np(image_dict):
    # WHD to DHW
    for k in image_dict.keys():
        if isinstance(image_dict[k], sitk.SimpleITK.Image):
            image_dict[k] = sitk_utils.get_npy(image_dict[k])
    return image_dict

def np2tensor(image_dict):
    for k in image_dict.keys():
        image_dict[k] = torch.tensor(image_dict[k])
    return image_dict
