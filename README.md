# changeMAC

changeMAC is a small program that changes your MAC address (on restart or manually). This prevents your device from being tracked in wifi networks, enabling you to use the same free-but-for-a-limited-time network multiple times and also circumventing per-device online-time limits. It's settings are accessible via an user interface.

## How to use

After opening the program, choose the network adapter you want to set the settings for from the dropdown list. In the lower part of the window, you'll see all actions:

Name | Type | Description
--- | --- | ---
```change on restart``` | Checkbox | Check it if you want your MAC to be different after every restart.
```OUI``` | Entry | These are the first three octets of the MAC. Set if you are experiencing issues or feel fancy.
```change mac``` | Button | Click to change MAC manually.
```reset settings``` | Button | Click to reset settings for this adapter.

This program only works when you're on windows and have admin rights.

If you have issues with a specific network adapter, select it from the dropdown list and click ```reset settings```. Now open a cmd window by pressing ```Win + R``` and type ```getmac /v /fo list```. Look at the network adapter and note the first three (of six) octets of the mac. Write these down in the ```OUI``` field. 

_Note: after pressing ```reset settings```, you'll  need to again choose the right adapter from the dropdown list._