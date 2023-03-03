import sys 
sys.path.append("src")
import warnings
warnings.filterwarnings('ignore', module='pyMRAW')
import pytest

from bounce_evaluator import bounce_eval
from data_classes import BounceData, VideoInfoPresets
from video_reader import VideoReaderMem

@pytest.mark.filterwarnings('ignore')
def test_default_bounce():

    reader = VideoReaderMem("data/ball_12bit_full.cihx")
    info = VideoInfoPresets(
        length = len(reader),
        shape = reader.frame_shape,
        pixel_scale=None,
        frame_rate=reader.frame_rate,
        bit_depth=reader.color_bit_depth,
        accel_thresh=1500.0,
        filename=reader.filename,
        ball_size=2.5e-3
    )
    data, streak = bounce_eval(reader.image_array, info)
    compare_data = BounceData.from_json_file("data/ball_12bit_full.json")

    assert data == compare_data