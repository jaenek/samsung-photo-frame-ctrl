import os

from frame_ctrl import FrameController

frame_ctrl = FrameController()
geometry = frame_ctrl.get_display_geometry()
os.system(f'./scripts/window-in-frame.sh GEOMETRY="{geometry}"')
