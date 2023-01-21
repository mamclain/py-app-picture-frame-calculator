from painting.dataclasses.painting_information import PaintingInformation
from painting.enums.text_unit_mode import TextUnitMode
from painting.frame_builder import FrameBuilder


def main():
    pictures = {
        "ruby": PaintingInformation(
            name="Ruby",
            width_min_cm=23.7,
            width_max_cm=24.3,
            height_min_cm=34.7,
            height_max_cm=35.3,
            left_offset_cm=0.5,
            top_offset_cm=0.5,
            right_offset_cm=0.5,
            bottom_offset_cm=3
        ),
        "dark_angel": PaintingInformation(
            name="Dark Angel",
            width_min_cm=33.8,
            width_max_cm=34,
            height_min_cm=69.5,
            height_max_cm=69.8,
            left_offset_cm=1,
            top_offset_cm=1,
            right_offset_cm=1,
            bottom_offset_cm=1
        ),
        "puffins": PaintingInformation(
            name="Puffins",
            width_min_cm=16.3,
            width_max_cm=16.7,
            height_min_cm=21.4,
            height_max_cm=22,
            left_offset_cm=.5,
            top_offset_cm=.5,
            right_offset_cm=.5,
            bottom_offset_cm=.5
        ),
    }

    painting = pictures["ruby"]
    frame = FrameBuilder(painting=painting)
    frame.draw_schematic(text_unit_mode=TextUnitMode.CM)
    # frame.draw_schematic(text_unit_mode=TextUnitMode.TAPE)
    # frame.calculate_build_dimensions()
    #
    # frame.plot()


if __name__ == '__main__':
    main()
