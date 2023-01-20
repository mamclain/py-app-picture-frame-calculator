from painting.dataclasses.painting_information import PaintingInformation
from painting.frame_builder import (
    build_frame,
    plot_frame
)


def main():
    pictures = {
        "ruby": PaintingInformation(
            width_min_cm=23.7,
            width_max_cm=24.3,
            height_min_cm=34.7,
            height_max_cm=35.3,
            hide_left_offset_cm=0.5,
            hide_top_offset_cm=0.5,
            hide_right_offset_cm=0.5,
            hide_bottom_offset_cm=3
        ),
        "dark_angel": PaintingInformation(
            width_min_cm=33.8,
            width_max_cm=34,
            height_min_cm=69.5,
            height_max_cm=69.8,
            hide_left_offset_cm=1,
            hide_top_offset_cm=1,
            hide_right_offset_cm=1,
            hide_bottom_offset_cm=1
        ),
        "puffins": PaintingInformation(
            width_min_cm=16.3,
            width_max_cm=16.7,
            height_min_cm=21.4,
            height_max_cm=22,
            hide_left_offset_cm=.5,
            hide_top_offset_cm=.5,
            hide_right_offset_cm=.5,
            hide_bottom_offset_cm=.5
        ),
    }

    painting = pictures["ruby"]

    frame_layout = build_frame(painting)

    plot_frame(frame_layout)


if __name__ == '__main__':
    main()
