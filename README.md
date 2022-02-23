# RRD Step Changer

This bad boy takes RRD files that have been dumped to XML, installs a new step and heartbeat in there, and duplicates the records enough times to keep the timescale (mostly) accurate.

## Usage

Step 0) Back up your RRD
  `cp -a /path/to/file.rrd ./file.rrd.backup`

Step 1) Dump RRD
  `rrdtool dump /path/to/file.rrd > original.xml`
  
Step 2) Change RRD Step (example: step 60, heartbeat 120)
  `python3 rrdstep.py original.xml modified.xml 60 120`

Step 3) Restore RRD
  `rrdtool restore modified.xml modified.rrd`
  
Step 4) Copy back
    `cp modified.rrd /path/to/file.rrd`


## Limitations

It can only change the step to a numerical factor of the existing step (or the other way around if you are changing to a larger step)

300 <-> 60 :ok_hand: 

300 <-> 100 :ok_hand:

300 <-> 200 :-1:


To move between steps that are not compatible, you can find the greatest common factor, and run the tool twice. This creates larger inaccuracies the lower the GCF, but allows any conversion.

300 <-> 100 <-> 200 :ok_hand:

&nbsp;

It doesn't do any interpolations or anything smart with the records, just duplicates rows until it fills in the time properly.

&nbsp;

# Dependencies

None :)
