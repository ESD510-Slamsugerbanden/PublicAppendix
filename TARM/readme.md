# The tarm codebase
In here you'll find all the code for making a reciever with a raspberry pi on your own.

 **Main.py**: Containing the continous tracking algortihm for the azimuth plane
 **angle_corr.py**: Simulation of the expected correlation for a given angle
 **init_search.py**: Algorihm for inital search
 **beacon_serde_vs.py**: The background server for recieving the gnuradio UDP packages
 **Rotax.py**: Interface for the platform controller
 **permutation.py**: Controller using extremum seeking control
 **switch.py**: For controlling the switches on the RPI
 **filters.py**: IIR lowpass and highpass filters
 