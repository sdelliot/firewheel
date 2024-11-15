.. _image-creation-tutorial:

#######################
Image Creation Tutorial
#######################
This tutorial will cover building a new image for use within FIREWHEEL.
This requires two steps.
First, building a new virtual machine disk from an `ISO <https://en.wikipedia.org/wiki/Optical_disc_image>`_ file.
Second, creating a new model component so that the image can be included in a topology file.
Lastly, there is an optional step to optimize the image size.
This step speeds the process of transferring images around the :ref:`FIREWHEEL-cluster` and saves disk size by ensuring that the VM disk size is as small as possible.


.. toctree::
   :maxdepth: 2

   image/building_from_iso.rst
   image/creating_model_component.rst
   image/optimizing_image_size.rst
   image/troubleshooting_images.rst
