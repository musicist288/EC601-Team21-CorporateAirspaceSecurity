from rtlsdr import RtlSdr
import math
from datetime import datetime
from threading import Timer 
# Commented this out since the code that uses it is
# docstring-ed out.
# from pylab import *

NUM_SAMPLES = 32768
BARGRAPH = "################################################################################" \
            + "                                                                                "
            

READINGS = 10

def main(): 
    baseline = 0
    state = 'capturing'
    sdr = RtlSdr()

    '''
    # configure device
    sdr.sample_rate = 1.024e6  # Hz
    sdr.center_freq = 433.9e6     # Hz
    sdr.freq_correction = 20   # PPM
    sdr.gain = 'auto'
    '''
    
    while True:
        a = float(input("Sample rate(MHz): "))
        if 0 < a <= 3.2:
            sdr.sample_rate = a*1e6
            break
        else:
            print("Invalid sample rate. Must be between 1Hz and 10MHz")

    b = float(input("Center Frequency(MHz): "))
    sdr.center_freq = b*1e6
    sdr.freq_correction = 20   # PPM
    sdr.gain = 'auto'
    

    #tones = AudioTones()
    #tones.init()
    #for i in range(0,10):
        #rssi = MeasureRSSI(sdr)

    i=1
    measures = 0
    while i>0:
        # Measure minimum RSSI over a few readings, auto-adjust for dongle gain
        min_rssi = 1000
        avg_rssi = 0
        for i in range(0, 10):
            rssi = MeasureRSSI(sdr)
            #print("i: ",i, "rssi: ",rssi,"\n")
            min_rssi = min(min_rssi, rssi)
            avg_rssi += rssi
        avg_rssi /= 10
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if state == "capturing":
            measures += 1
            baseline += avg_rssi
            if measures == READINGS:
                baseline  /= READINGS
                state = 'running'
                print("Running")
                print("Baseline; %f" % baseline)
        else:
            if avg_rssi > baseline + 8:
                print("Detected issue - Time: ", current_time, " Avg_RSSI: ",avg_rssi)

    #ampl_offset = avg_rssi
    #max_rssi = MeasureRSSI(sdr) - ampl_offset
    #avg_rssi = max_rssi + 20;
    #counter = 0

    '''
    # use matplotlib to estimate and plot the PSD
    samples = sdr.read_samples(256*1024)
    psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
    xlabel('Frequency (MHz)')
    ylabel('Relative power (dB)')
    show()
    '''

# First attempt: using floating-point complex samples
def MeasureRSSI(sdr):
    samples = sdr.read_samples(NUM_SAMPLES)
    power = 0.0
    for sample in samples:
        power += (sample.real * sample.real) + (sample.imag * sample.imag)
    return 10 * (math.log(power) - math.log(NUM_SAMPLES))


if __name__ == "__main__":
    import os, sys
    main()

