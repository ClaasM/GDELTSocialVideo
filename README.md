./darknet detector test cfg/coco.data cfg/yolov3.cfg yolov3.weights data/dog.jpg


Make sure the following environment variables are set:

export DYLD_LIBRARY_PATH="/usr/local/cuda/lib"

If using PyCharm, they can be added to the default Python run configuration s.t. they're set for every new python script.
There is no run configuration for Jupyter, though, so the notebook server has to be run from a Terminal (which can be a PyCharm-Terminal, though).

Consists of 2225 documents from the BBC news website corresponding to stories in five topical areas from 2004-2005.
Natural Classes: 5 (business, entertainment, politics, sport, tech)

If you make use of the dataset, please consider citing the publication:
- D. Greene and P. Cunningham. "Practical Solutions to the Problem of Diagonal Dominance in Kernel Document Clustering", Proc. ICML 2006.

All rights, including copyright, in the content of the original articles are owned by the BBC.

Contact Derek Greene <derek.greene@ucd.ie> for further information.
http://mlg.ucd.ie/datasets/bbc.html

