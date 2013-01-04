# donationprint

Prints a donation reciept with prefilled forms to support your local
hackerspace.

This is a fork of the original RaumZeitLabor repository at
<https://raumzeitlabor.de/wiki/Spendenterminal> with the following features:

* Connected to a Raspberry Pi
* Prints a pre-filled donation form when swiping a valid EC card
* Prints a blank donation form when pushing a button (via GPIO)
* Status LED to indicate processing (via GPIO)
* Counts the number of printed receipts, in case you want statistics

## setup

* Clone this repository to `/root/donationprint` (or alter some paths)
* Connect a button to ground and GPIO15 (we'll use the internal pull-up)
* Connect GPIO23 to the base of an NPN transistor driving the status LED
  (6k8 seems to be an acceptable base resistance)
* Start `blankprint` and `donationprint` via systemd, daemontools or similar
