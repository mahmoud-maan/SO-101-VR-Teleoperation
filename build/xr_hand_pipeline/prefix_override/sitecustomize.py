import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/maan/SO-101-VR-Teleoperation/install/xr_hand_pipeline'
