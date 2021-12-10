#### Attack using Rogue Wi-Fi Access Point

WLANs are the most dominant wireless connectivity infrastructure for short-range and high-throughput 
Internet services and have been widely deployed in populationdense scenarios such as homes, offices, 
campuses, shopping malls, and airports. Wi-Fi networks have been designed based on the 
IEEE 802.11 standards, and 802.11a/g/n/ac standards are widely used in various commercial Wi-Fi devices 
such as smartphones, laptops, printers, cameras, and smart televisions.

Most of Wi-Fi networks operate in unlicensed industrial, scientific, and medical (ISM) frequency bands, 
which have 14 overlapping 20 MHz channels on 2.4 GHz and 28 nonoverlapping 20 MHz channels bandwidth in 5 GHz. 
Most Wi-Fi devices are limited to a maximum transmit power of 100 mW, with a typical indoor coverage range of 35 m.
A Wi-Fi network can cover up to 1 km range in outdoor environments in an extended coverage setting.

When deploying a rogue Wi-Fi AP, hackers usually imitating a legitimate AP with the same SSID, which will help 
them confuse mobile users and attract more users to select the rogue one. To avoid being detected, hackers may 
also go a step further and spoof the MAC address of the true access point so that will be seen as a base 
station clone, which strengthens the illusion. In addition, when multiple Wi-Fi APs are associated with 
the same SSID, the majority of today’s devices are configured to connect to the one that provides higher 
signal strength. When mobile devices are closer to the rogue Wi-Fi AP than the genuine one, 
the rogue one is like to have higher signal strength and hence is selected for connection.
 
As the example, hackers can deploy a rogue Wi-Fi AP near to Starbucks Coffee store and change the SSID to 
“Starbucks Free Wi-Fi”. For users who do not check it carefully, there is a high probability for them 
to choose this rogue Wi-Fi AP.
 
For attacks launched by deploying rogue Wi-Fi APs, there are four major parties involved: 
1. a genuine AP
2. a regular Wi-Fi service user
3. a rogue AP
4. an attacker. 

To launch the attack, the rogue Wi-Fi AP just simply sniffs the first three steps of the four-way 
handshake protocol between the user and the genuine AP. As the authentication process is in an 
open Wi-Fi network that does not involve any key exchange, the attacker is able to obtain 
the parameters sent by the genuine AP to the user. 

Then, by injecting an association response to the user right after its request is sent out in step 3 of the 
four-way handshake protocol, the rogue Wi-Fi AP will be associated with the user. This is because the user 
associated with the AP whose association response arrives first.
