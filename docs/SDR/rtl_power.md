# RTL Power tool 

(open-source) Command line only tool that generates .csv files with the power levels of each fft bin over time. 
This allows a large swatch of spectrum to be monitored. With a python script, a waterfall image can be generated. 

---

### Feature:
1. Unlimited frequency range. You can do the whole 1.7GHz of a dongle.
2. Unlimited time. At least until you run out of disk for logging.
3. Unlimited FFT bins. But in practice I don't think I've taken it above 100k bins.
4. Quantitative rendering. Exact power levels are logged.
5. Runs on anything. A slower computer will use less samples to keep up

---

### Install rtl_power
It comes with the rtl-sdr driver, the rtl-sdr code can be checked out with: 
```
git clone git://git.osmocom.org/rtl-sdr.git
```
Building with cmake:
``` 
    cd rtl-sdr/
    mkdir build
    cd build
    cmake ../
    make
    sudo make install
    sudo ldconfig
```
In order to be able to use the dongle as a non-root user, 
you may install the appropriate udev rules file by calling cmake with -DINSTALL_UDEV_RULES=ON argument in the above build steps.
``` 
cmake ../ -DINSTALL_UDEV_RULES=ON 
```
To check if it's correctly installed and working, call: rtl_test -t

---

### Example Command

```
rtl_power -f 144M:146M:100 -g 50 -i 1s -e 30m two_meter_data.csv
```
Captures from 144MHz to 146Mhz in 100Hz intervals with a gain of 50, taking samples every 1 sec, for 30 minutes, 
and saving into the file "two_meter_data.csv"

---

### Parameters
```
-f lower:upper:bin  (Hz)
```
Frequency range and the size of the bin
```
-i <integration interval>
```
Amount of time to integrate for each sample
```
-g <gain value>
```
Gain for the sdr
```
-e <exit timer>
```
Amount of time to collect for

---

### Output Format
Rtl_power produces a compact CSV file with minimal redundancy. The columns are:
```
    date, time, Hz low, Hz high, Hz step, samples, dB, dB, dB, ...
```
---

### Usage

```
rtl_power -f 420M:440M:8k -g 50 -i 10 -e 1h  433_minute.csv
```

**Note:** On some platforms this may hit a 2GB file limit. 
Use output redirection **(rtl_power ... > log.csv)** for unlimited file size.

---

#### Why rtl_power instead of spectrum analyzer?

The above command represents one hour of the entire 20MHz air-band. Chatter and active frequencies are quite visible. 
But you could never see this in a normal waterfall. A normal waterfall restricts the view to a narrow slit. 
Compared with the survey, a waterfall displays a chunk that is 300 pixels wide and one pixel tall. 
No wonder for very wide band we cannot find any traffic.

When you are considering getting into a new branch of radio, performing surveys is a smart idea. 
A survey is basically a summary of an entire band. If anything happens, it will appear in the survey.
First check if your location has good reception.

Using rtl_power is much lower-stress than monitoring a waterfall. 
Timing does not really matter and you don't have to stay glued to the screen. 
Go eat dinner and check the plot afterwards.

---

#### Scripting for getting average RSSI values over a fixed interval for a band

With a small amount of Awk/Perl/Python/whatever you can quickly put together custom tools. 
For example, if you wanted to make a 150MHz power meter:

```
rtl_power -f 300M:450M:3.2M -g 30 -i 1 | awk 'BEGIN {t=0} {if (t==0) {t=$2; n=0; s=0};
if (t==$2) {s+=$7; n++} else {print s/n; t=0}}'
```

Every couple of seconds it will output the average dB of the entire range. 
Here post-processing is a little simpler because it is operating in wide-bin mode and each line only has a single dB value.

---
