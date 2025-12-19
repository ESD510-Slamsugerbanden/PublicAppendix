# Gnuradio related software
In here you'll find:

**Transmitter.grc**: Gnuradio program for transmitting the tracking codes equvidistantely.

**Reciever_Debeaconizer.grc**: Gnurdaio program for recievering the tracking codes and passing them on the estimate server.

**Transmitter.py**: Gnuradio block for scheduling the transmission of the tracking codes.

**Reciever.py**: Gnuradio block for recieving, decoding and scheduling the switches as well as passing on correlations and RSSI to in a Gnuradio msg format.

**UDP_sink.py**: A UDP sink block capabale of transmitting gnuradio message types
