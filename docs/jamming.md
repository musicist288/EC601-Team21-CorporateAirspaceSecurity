#### Jamming Attack Vulnerability in Wireless Network

As we are increasingly reliant on wireless services, security threats have become a big concern 
about the confidentiality, integrity, and availability of wireless communications. 
Compared to other security threats such as eavesdropping and data fabrication, wireless networks
are particularly vulnerable to radio jamming attacks for the following reasons. 

1. First, jamming attacks are easy to launch. With the advances in software-defined radio, one can easily program 
a small $10 USB dongle device to a jammer that covers 20 MHz bandwidth below 6 GHz and up to 100 mW transmission power.
Such a USB dongle suffices to disrupt the Wi-Fi services in a home or office scenario. 
Other off-the-shelf SDR devices such as USRP and Bladerf are even more powerful and more flexible when using as a jamming emitter. 
The ease of launching jamming attacks makes it urgent to secure wireless networks against intentional and unintentional jamming threats. 
 
2. Second, jamming threats can only be thwarted at the physical (PHY) layer but not at the MAC or network layer. 
When a wireless network suffers from jamming attacks, its legitimate wireless signals are typically overwhelmed
by irregular or sophisticated radio jamming signals, making it hard for legitimate wireless devices to decode data packets.
Therefore, any strategies at the MAC layer or above are incapable of thwarting jamming threats, 
and innovative antijamming strategies are needed at the physical layer. 
 
3. Third, the effective anti-jamming strategies for real-world wireless networks remain limited. 
Despite the significant advancement of wireless technologies, most of current wireless networks 
(e.g., cellular and Wi-Fi networks) can be easily paralyzed by jamming attacks due to the lack 
of protection mechanism. The vulnerability of existing wireless networks can be attributed to 
the lack of effective anti-jamming mechanisms in practice. The jamming vulnerability of existing 
wireless networks also underscores the critical need and fundamental challenges in designing practical anti-jamming schemes.
 This article provides a comprehensive
