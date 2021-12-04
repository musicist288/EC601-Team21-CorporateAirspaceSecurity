import argparse
from rtlsdr import RtlSdr
import math
from datetime import datetime
from threading import Timer 
from audio_tones import AudioTones

NUM_SAMPLES = 32768
BARGRAPH = "################################################################################" \
            + "                                                                                "
            

READINGS = 10

def main(): 
    baseline = 0
    state = 'capturing'
    sdr = RtlSdr()
    
    parser = argparse.ArgumentParser(description="To detect rogue signal based on RSSI; check README.md for options and usage")

    parser.add_argument("-s", "--samplerate", action="store", type=float, default="2000000", help="Default=2mhz | Set how quickly bits are read")
    parser.add_argument("-f", "--frequency", action="store", type=float, default="433000000", help="Default=433mhz | Set the frequency to listen on")
    parser.add_argument("-g", "--gain", action="store", type=str, default="auto", help="Default=auto |  RX Gain")
    parser.add_argument("-p", "--ppm", action="store", type=int, default="20", help="Default=20 | Frequency correction")
    args = parser.parse_args()

    
    # configure device
    sdr.sample_rate = args.samplerate  # Hz
    sdr.center_freq = args.frequency     # Hz
    sdr.freq_correction = args.ppm   # PPM
    sdr.gain = args.gain #gain


    tones = AudioTones()
    tones.init()
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
                tones.play(35)



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
