#!/usr/bin/bash
# orig_300.xml  README.md  reference_300_600_1200.xml  reference_300_60_120.xml  rrdstep.py  test.sh
rm -f test_*.xml
python3 ../rrdstep.py orig_300.xml test_600_1200.xml 600 1200
python3 ../rrdstep.py orig_300.xml test_60_120.xml 60 120
sha256sum reference_300_60_120.xml test_60_120.xml
sha256sum reference_300_600_1200.xml test_600_1200.xml
