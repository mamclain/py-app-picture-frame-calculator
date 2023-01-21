"""
a class to build a frame for a painting
"""
import io
from typing import Tuple

import cairosvg
import svgwrite
from matplotlib import pyplot as plt

from painting.dataclasses.coordinate import Coordinate
from painting.dataclasses.coordinate_list import CoordinateList
from painting.dataclasses.frame_layout import FrameLayout
from painting.dataclasses.frame_part import FramePart
from painting.dataclasses.frame_part_list import FramePartList
from painting.dataclasses.frame_size import FrameSize
from painting.dataclasses.painting_information import PaintingInformation
from painting.dataclasses.paper_dimensions import PaperDimensions
from painting.dataclasses.unit_cm_value import UnitCm
from painting.enums.frame_coordinate import FrameCoordinate
from painting.enums.frame_index import FrameIndex
from painting.enums.text_unit_mode import TextUnitMode
from painting.mathematics.units import cm_to_in


class FrameBuilder(object):
    def __init__(
            self,
            painting: PaintingInformation,
            frame: FrameSize = FrameSize(width_in=2, height_in=1)
    ):
        self.painting = painting
        self.frame = frame

    def calculate_frame_layout(
            self,
            at: Coordinate = Coordinate(x=0, y=0),
    ) -> FrameLayout:
        """ calculate the frame layout for a painting
        :param at: the location of the painting
        :return: the frame layout
        """

        # find the delta between the min and max painting size
        od_width_delta = self.painting.width_max_cm - self.painting.width_min_cm
        od_height_delta = self.painting.height_max_cm - self.painting.height_min_cm

        # find the center offset between the min and max painting size
        minimum_edge_at = Coordinate(
            x=at.x + od_width_delta / 2,
            y=at.y + od_height_delta / 2
        )

        # find the interior edge that covers the painting
        interior_edge_at = Coordinate(
            x=at.x + self.painting.left_offset_cm,
            y=at.y + self.painting.bottom_offset_cm
        )

        # build a vertex list of the maximum painting boundary
        painting_maximum_boundary = CoordinateList(
            [
                Coordinate(
                    x=at.x,
                    y=at.y
                ),
                Coordinate(
                    x=at.x + self.painting.width_max_cm,
                    y=at.y
                ),
                Coordinate(
                    x=at.x + self.painting.width_max_cm,
                    y=at.y + self.painting.height_max_cm
                ),
                Coordinate(
                    x=at.x,
                    y=at.y + self.painting.height_max_cm
                ),
                Coordinate(
                    x=at.x,
                    y=at.y
                )
            ]
        )

        # build a vertex list of the minimum painting boundary
        painting_minimum_boundary = CoordinateList(
            [
                Coordinate(
                    x=minimum_edge_at.x,
                    y=minimum_edge_at.y
                ),
                Coordinate(
                    x=minimum_edge_at.x + self.painting.width_min_cm,
                    y=minimum_edge_at.y
                ),
                Coordinate(
                    x=minimum_edge_at.x + self.painting.width_min_cm,
                    y=minimum_edge_at.y + self.painting.height_min_cm
                ),
                Coordinate(
                    x=minimum_edge_at.x,
                    y=minimum_edge_at.y + self.painting.height_min_cm
                ),
                Coordinate(
                    x=minimum_edge_at.x,
                    y=minimum_edge_at.y
                )
            ]
        )

        # build a vertex list of the interior edge of the frame overlapping the painting
        interior_edge = CoordinateList(
            [
                Coordinate(
                    x=interior_edge_at.x,
                    y=interior_edge_at.y
                ),
                Coordinate(
                    x=interior_edge_at.x + (
                            self.painting.width_max_cm - self.painting.right_offset_cm - self.painting.left_offset_cm
                    ),
                    y=interior_edge_at.y
                ),
                Coordinate(
                    x=interior_edge_at.x + (
                            self.painting.width_max_cm - self.painting.right_offset_cm - self.painting.left_offset_cm
                    ),
                    y=interior_edge_at.y + (
                            self.painting.height_max_cm - self.painting.top_offset_cm - self.painting.bottom_offset_cm
                    )
                ),
                Coordinate(
                    x=interior_edge_at.x,
                    y=interior_edge_at.y + (
                            self.painting.height_max_cm - self.painting.top_offset_cm - self.painting.bottom_offset_cm
                    )
                ),
                Coordinate(
                    x=interior_edge_at.x,
                    y=interior_edge_at.y
                )
            ]
        )

        # build a vertex list of the exterior edge of the frame
        exterior_edge = CoordinateList(
            [
                interior_edge[FrameCoordinate.BOTTOM_LEFT] + Coordinate(
                    x=-self.frame.width_cm,
                    y=-self.frame.width_cm
                ),
                interior_edge[FrameCoordinate.BOTTOM_RIGHT] + Coordinate(
                    x=self.frame.width_cm,
                    y=-self.frame.width_cm
                ),
                interior_edge[FrameCoordinate.TOP_RIGHT] + Coordinate(
                    x=self.frame.width_cm,
                    y=self.frame.width_cm
                ),
                interior_edge[FrameCoordinate.TOP_LEFT] + Coordinate(
                    x=-self.frame.width_cm,
                    y=self.frame.width_cm
                ),
                interior_edge[FrameCoordinate.BOTTOM_LEFT_OVERLAY] + Coordinate(
                    x=-self.frame.width_cm,
                    y=-self.frame.width_cm
                )
            ]
        )

        # cleanup the vertex lists to get all vertexes into quadrant 1
        # find min x and y
        min_x = at.x - exterior_edge.x_min
        min_y = at.y - exterior_edge.y_min

        # create an offset coordinate
        min_offset = Coordinate(x=min_x, y=min_y)

        # apply the offset to all vertexes lists
        painting_maximum_boundary += min_offset
        painting_minimum_boundary += min_offset
        interior_edge += min_offset
        exterior_edge += min_offset

        return FrameLayout(
            painting_max_boundary=painting_maximum_boundary,
            painting_min_boundary=painting_minimum_boundary,
            painting_overlap_boundary=interior_edge,
            frame_exterior_boundary=exterior_edge
        )

    def calculate_build_dimensions(self) -> FramePartList:
        """ calculate the build dimensions for the frame

        :return: a list of frame parts
        """

        # calculate the frame layout
        base_frame = self.calculate_frame_layout()

        # pull out the needed edges
        inner_frame = base_frame.painting_overlap_boundary
        outer_frame = base_frame.frame_exterior_boundary
        inlay_frame = base_frame.painting_max_boundary
        delta_inlay = base_frame.painting_min_boundary

        # calculate the inner build dimensions
        bottom_id_cm = inner_frame[FrameCoordinate.BOTTOM_LEFT].distance(inner_frame[FrameCoordinate.BOTTOM_RIGHT])
        right_id_cm = inner_frame[FrameCoordinate.BOTTOM_RIGHT].distance(inner_frame[FrameCoordinate.TOP_RIGHT])
        top_id_cm = inner_frame[FrameCoordinate.TOP_RIGHT].distance(inner_frame[FrameCoordinate.TOP_LEFT])
        left_id_cm = inner_frame[FrameCoordinate.TOP_LEFT].distance(inner_frame[FrameCoordinate.BOTTOM_LEFT])

        # calculate the outer build dimensions
        bottom_od_cm = outer_frame[FrameCoordinate.BOTTOM_LEFT].distance(outer_frame[FrameCoordinate.BOTTOM_RIGHT])
        right_od_cm = outer_frame[FrameCoordinate.BOTTOM_RIGHT].distance(outer_frame[FrameCoordinate.TOP_RIGHT])
        top_od_cm = outer_frame[FrameCoordinate.TOP_RIGHT].distance(outer_frame[FrameCoordinate.TOP_LEFT])
        left_od_cm = outer_frame[FrameCoordinate.TOP_LEFT].distance(outer_frame[FrameCoordinate.BOTTOM_LEFT])

        # calculate the inlay build dimensions
        bottom_inlay_cm = inner_frame[FrameCoordinate.BOTTOM_LEFT].y_delta(inlay_frame[FrameCoordinate.BOTTOM_RIGHT])
        right_inlay_cm = inner_frame[FrameCoordinate.BOTTOM_RIGHT].x_delta(inlay_frame[FrameCoordinate.TOP_RIGHT])
        top_inlay_cm = inner_frame[FrameCoordinate.TOP_RIGHT].y_delta(inlay_frame[FrameCoordinate.TOP_LEFT])
        left_inlay_cm = inner_frame[FrameCoordinate.TOP_LEFT].x_delta(inlay_frame[FrameCoordinate.BOTTOM_LEFT])

        # calculate the delta inlay build dimensions
        bottom_coverage_cm = inner_frame[FrameCoordinate.BOTTOM_LEFT].y_delta(delta_inlay[FrameCoordinate.BOTTOM_RIGHT])
        right_coverage_cm = inner_frame[FrameCoordinate.BOTTOM_RIGHT].x_delta(delta_inlay[FrameCoordinate.TOP_RIGHT])
        top_coverage_cm = inner_frame[FrameCoordinate.TOP_RIGHT].y_delta(delta_inlay[FrameCoordinate.TOP_LEFT])
        left_coverage_cm = inner_frame[FrameCoordinate.TOP_LEFT].x_delta(delta_inlay[FrameCoordinate.BOTTOM_LEFT])

        # build the frame part list
        parts_list = FramePartList(
            [
                FramePart(
                    inner_length=UnitCm(bottom_id_cm),
                    outer_length=UnitCm(bottom_od_cm),
                    inlay_width=UnitCm(bottom_inlay_cm),
                    coverage_width=UnitCm(bottom_coverage_cm)
                ),
                FramePart(
                    inner_length=UnitCm(right_id_cm),
                    outer_length=UnitCm(right_od_cm),
                    inlay_width=UnitCm(right_inlay_cm),
                    coverage_width=UnitCm(right_coverage_cm)
                ),
                FramePart(
                    inner_length=UnitCm(top_id_cm),
                    outer_length=UnitCm(top_od_cm),
                    inlay_width=UnitCm(top_inlay_cm),
                    coverage_width=UnitCm(top_coverage_cm)
                ),
                FramePart(
                    inner_length=UnitCm(left_id_cm),
                    outer_length=UnitCm(left_od_cm),
                    inlay_width=UnitCm(left_inlay_cm),
                    coverage_width=UnitCm(left_coverage_cm)
                )
            ]
        )
        return parts_list

    @staticmethod
    def _draw_od_bottom_dimension(
            dwg: svgwrite.Drawing,
            x1_xy: Tuple[float, float],
            x2_xy: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode

    ):
        """ draw the od bottom dimension
        :param dwg: the drawing to draw on
        :param x1_xy: the left x,y coordinate
        :param x2_xy: the right x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        # left end cap line
        dwg.add(
            dwg.line(
                (x1_xy[0], x1_xy[1] - ruler_offset),
                (x1_xy[0], x1_xy[1] - ruler_offset * 2),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )
        # right end cap line
        dwg.add(
            dwg.line(
                (x2_xy[0], x2_xy[1] - ruler_offset),
                (x2_xy[0], x2_xy[1] - ruler_offset * 2),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )
        # the line
        dwg.add(
            dwg.line(
                (x1_xy[0], x1_xy[1] - ruler_offset - ruler_offset / 2),
                (x2_xy[0], x2_xy[1] - ruler_offset - ruler_offset / 2),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.outer_length.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.outer_length.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.outer_length.value_tape
        else:
            output_text = frame_part.outer_length.value_cm_round

        # draw the bottom text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        bottom_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="middle",
            font_size=font_size,
        )
        # the text is drawn in normal rotation space so we need to flip it back right side up
        bottom_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        bottom_text.translate(
            (x1_xy[0] + x2_xy[0]) / 2,
            x1_xy[1] + ruler_offset * 3 + ruler_offset / 2
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(bottom_text)

    @staticmethod
    def _draw_od_side_dimension(
            dwg: svgwrite.Drawing,
            x1_xy: Tuple[float, float],
            x2_xy: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the od side dimension
        :param dwg: the drawing to draw on
        :param x1_xy: the top x,y coordinate
        :param x2_xy: the bottom x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        # top end cap line
        dwg.add(
            dwg.line(
                (x1_xy[0] + ruler_offset, x1_xy[1]),
                (x1_xy[0] + ruler_offset * 2, x1_xy[1]),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )
        # bottom end cap line
        dwg.add(
            dwg.line(
                (x2_xy[0] + ruler_offset, x2_xy[1]),
                (x2_xy[0] + ruler_offset * 2, x2_xy[1]),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )
        # the line
        dwg.add(
            dwg.line(
                (x1_xy[0] + ruler_offset + ruler_offset / 2, x1_xy[1]),
                (x2_xy[0] + ruler_offset + ruler_offset / 2, x2_xy[1]),
                stroke="black",
                stroke_width=svg_dim_stroke_width
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.outer_length.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.outer_length.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.outer_length.value_tape
        else:
            output_text = frame_part.outer_length.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="start",
            font_size=font_size,
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            (x1_xy[0] + ruler_offset * 2 + ruler_offset / 2),
            -(x2_xy[1] - x1_xy[1]) / 2
        )
        side_text.rotate(90)
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_id_side_dimension(
            dwg: svgwrite.Drawing,
            x1_xy: Tuple[float, float],
            x2_xy: Tuple[float, float],
            side_length: UnitCm,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the max painting dimension
        :param dwg: the drawing to draw on
        :param x1_xy: the top x,y coordinate
        :param x2_xy: the bottom x,y coordinate
        :param side_length: the length of the side
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        # top end cap line
        dwg.add(
            dwg.line(
                (x1_xy[0] - ruler_offset / 4, x1_xy[1]),
                (x1_xy[0] - ruler_offset / 4 - ruler_offset, x1_xy[1]),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )
        # bottom end cap line
        dwg.add(
            dwg.line(
                (x2_xy[0] - ruler_offset / 4, x2_xy[1]),
                (x2_xy[0] - ruler_offset / 4 - ruler_offset, x2_xy[1]),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )
        # the line
        dwg.add(
            dwg.line(
                (x1_xy[0] - ruler_offset / 4 - ruler_offset / 2, x1_xy[1]),
                (x2_xy[0] - ruler_offset / 4 - ruler_offset / 2, x2_xy[1]),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = side_length.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = side_length.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = side_length.value_tape
        else:
            output_text = side_length.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="start",
            font_size=font_size,
            fill="blue"
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            (x1_xy[0] - ruler_offset - ruler_offset / 2),
            -(x2_xy[1] - x1_xy[1]) / 2
        )
        side_text.rotate(-90)
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_id_top_dimension(
            dwg: svgwrite.Drawing,
            x1_xy: Tuple[float, float],
            x2_xy: Tuple[float, float],
            side_length: UnitCm,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode

    ):
        """ draw the id top dimension
        :param dwg: the drawing to draw on
        :param x1_xy: the left x,y coordinate
        :param x2_xy: the right x,y coordinate
        :param side_length: the side length to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        # left end cap line
        dwg.add(
            dwg.line(
                (x1_xy[0], x1_xy[1] + ruler_offset / 4),
                (x1_xy[0], x1_xy[1] + ruler_offset / 4 + ruler_offset),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )
        # right end cap line
        dwg.add(
            dwg.line(
                (x2_xy[0], x2_xy[1] + ruler_offset / 4),
                (x2_xy[0], x2_xy[1] + ruler_offset / 4 + ruler_offset),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )
        # the line
        dwg.add(
            dwg.line(
                (x1_xy[0], x1_xy[1] + ruler_offset / 4 + ruler_offset / 2),
                (x2_xy[0], x2_xy[1] + ruler_offset / 4 + ruler_offset / 2),
                stroke="blue",
                stroke_width=svg_dim_stroke_width
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = side_length.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = side_length.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = side_length.value_tape
        else:
            output_text = side_length.value_cm_round

        # draw the bottom text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        bottom_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="middle",
            font_size=font_size,
            fill="blue"
        )
        # the text is drawn in normal rotation space so we need to flip it back right side up
        bottom_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        bottom_text.translate(
            (x1_xy[0] + x2_xy[0]) / 2,
            -(x1_xy[1] + ruler_offset / 2 + ruler_offset / 2)
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(bottom_text)

    @staticmethod
    def _draw_bottom_inlay_dimension(
            dwg: svgwrite.Drawing,
            xy1: Tuple[float, float],
            xy2: Tuple[float, float],
            xy3: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the bottom dimension
        :param dwg: the drawing to draw on
        :param xy1: the xy 1 x,y coordinate
        :param xy2: the xy 2 x,y coordinate
        :param xy3: the xy 3 x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        x_mid_point = (xy1[0] + xy2[0]) / 2

        # draw arrow left side
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point - ruler_offset / 2, xy1[1] + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )
        # draw arrow right side
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point + ruler_offset / 2, xy1[1] + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw outbound line
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point, xy3[1]),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw hash edge
        dwg.add(
            dwg.line(
                (x_mid_point - ruler_offset / 2, xy3[1]),
                (x_mid_point + ruler_offset / 2, xy3[1]),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.inlay_width.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.inlay_width.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.inlay_width.value_tape
        else:
            output_text = frame_part.inlay_width.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="middle",
            font_size=font_size,
            fill="red"
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            x_mid_point,
            -xy3[1] - ruler_offset / 2
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_top_inlay_dimension(
            dwg: svgwrite.Drawing,
            xy1: Tuple[float, float],
            xy2: Tuple[float, float],
            xy3: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the bottom dimension
        :param dwg: the drawing to draw on
        :param xy1: the xy 1 x,y coordinate
        :param xy2: the xy 2 x,y coordinate
        :param xy3: the xy 3 x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        x_mid_point = (xy1[0] + xy2[0]) / 2

        # draw arrow left side
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point - ruler_offset / 2, xy1[1] - ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )
        # draw arrow right side
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point + ruler_offset / 2, xy1[1] - ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw outbound line
        dwg.add(
            dwg.line(
                (x_mid_point, xy1[1]),
                (x_mid_point, xy3[1]),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw hash edge
        dwg.add(
            dwg.line(
                (x_mid_point - ruler_offset / 2, xy3[1]),
                (x_mid_point + ruler_offset / 2, xy3[1]),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.inlay_width.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.inlay_width.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.inlay_width.value_tape
        else:
            output_text = frame_part.inlay_width.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="middle",
            font_size=font_size,
            fill="red"
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            x_mid_point,
            -xy3[1] + ruler_offset
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_right_inlay_dimension(
            dwg: svgwrite.Drawing,
            xy1: Tuple[float, float],
            xy2: Tuple[float, float],
            xy3: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the right dimension
        :param dwg: the drawing to draw on
        :param xy1: the xy 1 x,y coordinate
        :param xy2: the xy 2 x,y coordinate
        :param xy3: the xy 3 x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        y_mid_point = (xy1[1] + xy2[1]) / 2

        # draw arrow top side
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy1[0] - ruler_offset / 2, y_mid_point - ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )
        # draw arrow bottom side
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy1[0] - ruler_offset / 2, y_mid_point + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw outbound line
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy3[0], y_mid_point),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw hash edge
        dwg.add(
            dwg.line(
                (xy3[0], y_mid_point - ruler_offset / 2),
                (xy3[0], y_mid_point + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.inlay_width.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.inlay_width.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.inlay_width.value_tape
        else:
            output_text = frame_part.inlay_width.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="end",
            font_size=font_size,
            fill="red"
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            xy3[0] - ruler_offset / 4,
            -y_mid_point + ruler_offset / 3
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_left_inlay_dimension(
            dwg: svgwrite.Drawing,
            xy1: Tuple[float, float],
            xy2: Tuple[float, float],
            xy3: Tuple[float, float],
            frame_part: FramePart,
            ruler_offset: float,
            svg_dim_stroke_width: float,
            font_size: str,
            text_unit_mode: TextUnitMode
    ):
        """ draw the left dimension
        :param dwg: the drawing to draw on
        :param xy1: the xy 1 x,y coordinate
        :param xy2: the xy 2 x,y coordinate
        :param xy3: the xy 3 x,y coordinate
        :param frame_part: the frame part to draw
        :param ruler_offset: the ruler offset
        :param svg_dim_stroke_width: the stroke width
        """

        y_mid_point = (xy1[1] + xy2[1]) / 2

        # draw arrow top side
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy1[0] + ruler_offset / 2, y_mid_point - ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )
        # draw arrow bottom side
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy1[0] + ruler_offset / 2, y_mid_point + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw outbound line
        dwg.add(
            dwg.line(
                (xy1[0], y_mid_point),
                (xy3[0], y_mid_point),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        # draw hash edge
        dwg.add(
            dwg.line(
                (xy3[0], y_mid_point - ruler_offset / 2),
                (xy3[0], y_mid_point + ruler_offset / 2),
                stroke="red",
                stroke_width=svg_dim_stroke_width / 2
            )
        )

        if text_unit_mode == TextUnitMode.CM:
            output_text = frame_part.inlay_width.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            output_text = frame_part.inlay_width.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            output_text = frame_part.inlay_width.value_tape
        else:
            output_text = frame_part.inlay_width.value_cm_round

        # draw the side text in inches
        # note the font_size is not directly related to the viewbox. best result so far is in percent
        side_text = dwg.text(
            output_text,
            insert=(0, 0),
            text_anchor="start",
            font_size=font_size,
            fill="red"
        )
        # the text is drawn in normal rotation space, so we need to flip it back right side up
        side_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        side_text.translate(
            xy3[0] + ruler_offset / 4,
            -y_mid_point + ruler_offset / 3
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(side_text)

    @staticmethod
    def _draw_text(
            dwg: svgwrite.Drawing,
            x: float,
            y: float,
            text: str,
            font_size: str,
            color: str,
            text_anchor: str,
    ):
        draw_text = dwg.text(
            text,
            insert=(0, 0),
            text_anchor=text_anchor,
            font_size=font_size,
            fill=color
        )
        # the text is drawn in normal rotation space so we need to flip it back right side up
        draw_text.scale(1, -1)
        # we also need to translate it to the correct location which is adding rather than subtracting
        draw_text.translate(
            x,
            -y
        )
        # we cant chain transforms so i had to do a dedicated object here
        dwg.add(draw_text)

    def draw_schematic(
            self,
            paper_size: PaperDimensions = PaperDimensions(8, 10),
            text_unit_mode: TextUnitMode = TextUnitMode.CM,
            at: Coordinate = Coordinate(x=0, y=0),
    ):
        """
        Draw a schematic of the frame layout
        :param paper_size: the size of the paper to draw on
        :param text_unit_mode: the unit mode to use for text
        :param at: the coordinate to draw the schematic at
        :return: 
        """

        frame_to_plot = self.calculate_frame_layout(at=at)
        parts = self.calculate_build_dimensions()

        exterior_coordinates = list(zip(
            [cm_to_in(v) for v in frame_to_plot.frame_exterior_boundary.xs],
            [cm_to_in(v) for v in frame_to_plot.frame_exterior_boundary.ys]
        ))

        interior_coordinates = list(zip(
            [cm_to_in(v) for v in frame_to_plot.painting_overlap_boundary.xs],
            [cm_to_in(v) for v in frame_to_plot.painting_overlap_boundary.ys]
        ))

        inlay_coordinates = list(zip(
            [cm_to_in(v) for v in frame_to_plot.painting_max_boundary.xs],
            [cm_to_in(v) for v in frame_to_plot.painting_max_boundary.ys]
        ))

        bottom_vertex = [
            exterior_coordinates[FrameCoordinate.BOTTOM_LEFT],
            exterior_coordinates[FrameCoordinate.BOTTOM_RIGHT],
            interior_coordinates[FrameCoordinate.BOTTOM_RIGHT],
            interior_coordinates[FrameCoordinate.BOTTOM_LEFT]
        ]

        right_vertex = [
            exterior_coordinates[FrameCoordinate.BOTTOM_RIGHT],
            exterior_coordinates[FrameCoordinate.TOP_RIGHT],
            interior_coordinates[FrameCoordinate.TOP_RIGHT],
            interior_coordinates[FrameCoordinate.BOTTOM_RIGHT]
        ]

        top_vertex = [
            exterior_coordinates[FrameCoordinate.TOP_RIGHT],
            exterior_coordinates[FrameCoordinate.TOP_LEFT],
            interior_coordinates[FrameCoordinate.TOP_LEFT],
            interior_coordinates[FrameCoordinate.TOP_RIGHT]
        ]

        left_vertex = [
            exterior_coordinates[FrameCoordinate.TOP_LEFT],
            exterior_coordinates[FrameCoordinate.BOTTOM_LEFT],
            interior_coordinates[FrameCoordinate.BOTTOM_LEFT],
            interior_coordinates[FrameCoordinate.TOP_LEFT]
        ]

        inlay_vertex = [
            inlay_coordinates[FrameCoordinate.BOTTOM_LEFT],
            inlay_coordinates[FrameCoordinate.BOTTOM_RIGHT],
            inlay_coordinates[FrameCoordinate.TOP_RIGHT],
            inlay_coordinates[FrameCoordinate.TOP_LEFT]
        ]

        interior_width = UnitCm(
            frame_to_plot.painting_overlap_boundary[FrameCoordinate.BOTTOM_RIGHT].distance(
                frame_to_plot.painting_overlap_boundary[FrameCoordinate.BOTTOM_LEFT]
            )
        )

        interior_height = UnitCm(
            frame_to_plot.painting_overlap_boundary[FrameCoordinate.BOTTOM_RIGHT].distance(
                frame_to_plot.painting_overlap_boundary[FrameCoordinate.TOP_RIGHT]
            )
        )

        painting_max_height = UnitCm(
            frame_to_plot.painting_max_boundary[FrameCoordinate.TOP_LEFT].distance(
                frame_to_plot.painting_max_boundary[FrameCoordinate.BOTTOM_LEFT]
            )
        )

        painting_max_width = UnitCm(
            frame_to_plot.painting_max_boundary[FrameCoordinate.TOP_LEFT].distance(
                frame_to_plot.painting_max_boundary[FrameCoordinate.TOP_RIGHT]
            )
        )

        exterior_x_min_in = cm_to_in(frame_to_plot.frame_exterior_boundary.x_min)
        exterior_y_min_in = cm_to_in(frame_to_plot.frame_exterior_boundary.y_min)
        exterior_x_max_in = cm_to_in(frame_to_plot.frame_exterior_boundary.x_max)
        exterior_y_max_in = cm_to_in(frame_to_plot.frame_exterior_boundary.y_max)

        svg_offset = 5
        ruler_offset = .5
        svg_stroke_width = .01
        svg_dim_stroke_width = .05
        font_size = "2%"

        svg_view_x_min_pad_in = exterior_x_min_in - svg_offset
        svg_view_y_min_pad_in = exterior_y_min_in - svg_offset
        svg_view_x_max_pad_in = exterior_x_max_in + svg_offset * 2
        svg_view_y_max_pad_in = exterior_y_max_in + svg_offset * 2

        svg_width_in = svg_view_x_max_pad_in - svg_view_x_min_pad_in
        svg_height_in = svg_view_y_max_pad_in - svg_view_y_min_pad_in

        # create the svg object
        dwg = svgwrite.Drawing(
            profile='tiny',
            size=(f"{paper_size.width}in", f"{paper_size.height}in")

        )

        # set up our view box
        dwg.attribs['viewBox'] = f"{svg_view_x_min_pad_in} " \
                                 f"{svg_view_y_min_pad_in} " \
                                 f"{svg_view_x_max_pad_in} " \
                                 f"{svg_view_y_max_pad_in}"

        # our coordinate space is upside down vs svg standard, so do a y-axis flip and transform
        dwg.attribs['transform'] = f"scale(1, -1) translate(0, -{svg_view_y_max_pad_in - svg_offset * 2})"

        # draw our bottom frame
        dwg.add(dwg.polygon(bottom_vertex, fill='lightblue', stroke='black', stroke_width=svg_stroke_width))

        self._draw_od_bottom_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.BOTTOM],
            x1_xy=bottom_vertex[0],
            x2_xy=bottom_vertex[1],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw our right frame
        dwg.add(dwg.polygon(right_vertex, fill='green', stroke='black', stroke_width=svg_stroke_width))

        # draw right side dimensions
        self._draw_od_side_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.RIGHT],
            x1_xy=right_vertex[0],
            x2_xy=right_vertex[1],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw top
        dwg.add(dwg.polygon(top_vertex, fill='lightblue', stroke='black', stroke_width=svg_stroke_width))

        # draw left
        dwg.add(dwg.polygon(left_vertex, fill='green', stroke='black', stroke_width=svg_stroke_width))

        # draw the inlay
        dwg.add(dwg.polygon(inlay_vertex, fill='none', stroke='black', stroke_width=svg_stroke_width * 2))

        # draw the bottom inlay dimension
        self._draw_bottom_inlay_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.BOTTOM],
            xy1=inlay_vertex[0],
            xy2=inlay_vertex[1],
            xy3=bottom_vertex[2],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw the top inlay dimension
        self._draw_top_inlay_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.TOP],
            xy1=inlay_vertex[3],
            xy2=inlay_vertex[2],
            xy3=top_vertex[2],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw the right side inlay dimension
        self._draw_right_inlay_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.RIGHT],
            xy1=inlay_vertex[2],
            xy2=inlay_vertex[1],
            xy3=right_vertex[2],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw the left side inlay dimension
        self._draw_left_inlay_dimension(
            dwg=dwg,
            frame_part=parts.parts[FrameIndex.LEFT],
            xy1=inlay_vertex[3],
            xy2=inlay_vertex[0],
            xy3=left_vertex[2],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw painting max side dimensions
        self._draw_id_side_dimension(
            dwg=dwg,
            side_length=painting_max_height,
            x1_xy=inlay_vertex[0],
            x2_xy=inlay_vertex[3],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw the painting max top dimension
        self._draw_id_top_dimension(
            dwg=dwg,
            side_length=painting_max_width,
            x1_xy=inlay_vertex[3],
            x2_xy=inlay_vertex[2],
            ruler_offset=ruler_offset,
            svg_dim_stroke_width=svg_dim_stroke_width,
            font_size=font_size,
            text_unit_mode=text_unit_mode
        )

        # draw the painting name
        self._draw_text(
            dwg=dwg,
            x=0,
            y=svg_height_in - svg_offset * 3 + .5,
            text=f"Name: {self.painting.name}",
            font_size=font_size,
            color='orange',
            text_anchor='start',
        )

        if text_unit_mode == TextUnitMode.CM:
            id_width_text = interior_width.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            id_width_text = interior_width.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            id_width_text = interior_width.value_tape
        else:
            id_width_text = interior_width.value_cm_round

        if text_unit_mode == TextUnitMode.CM:
            id_height_text = interior_height.value_cm_round
        elif text_unit_mode == TextUnitMode.INCH:
            id_height_text = interior_height.value_in_round
        elif text_unit_mode == TextUnitMode.TAPE:
            id_height_text = interior_height.value_tape
        else:
            id_height_text = interior_height.value_cm_round

        self._draw_text(
            dwg=dwg,
            x=(svg_width_in - svg_offset * 3) / 2,
            y=(svg_height_in - svg_offset * 3) / 2 - .5,
            text=f"ID Width: {id_width_text}",
            font_size=font_size,
            color='orange',
            text_anchor='middle',
        )

        self._draw_text(
            dwg=dwg,
            x=(svg_width_in - svg_offset * 3) / 2,
            y=(svg_height_in - svg_offset * 3) / 2 + .5,
            text=f"ID Height: {id_height_text}",
            font_size=font_size,
            color='orange',
            text_anchor='middle',
        )

        svg_file = io.StringIO()
        dwg.write(svg_file)
        svg_file.seek(0)

        cairosvg.svg2png(file_obj=svg_file, write_to="testd.png", dpi=300)

    def plot(
            self,
            at: Coordinate = Coordinate(x=0, y=0),
            axis_offset: float = 1
    ) -> None:
        """ plot a frame layout
        :param at: the bottom left location of the painting on the plot
        :param axis_offset: the offset to apply to the axis
        """

        frame_to_plot = self.calculate_frame_layout(at=at)

        # find the min and max axis ranges from the outside boundary
        min_x = frame_to_plot.frame_exterior_boundary.x_min
        max_x = frame_to_plot.frame_exterior_boundary.x_max
        min_y = frame_to_plot.frame_exterior_boundary.y_min
        max_y = frame_to_plot.frame_exterior_boundary.y_max

        # to make the axis equal, find the common min and max between x and y and add small offset
        eq_min = min(min_x, min_y) - axis_offset
        eq_max = max(max_x, max_y) + axis_offset

        plt.xlim(eq_min, eq_max)
        plt.ylim(eq_min, eq_max)
        ax = plt.gca()
        ax.set_aspect('equal', adjustable='box')

        plt.plot(frame_to_plot.painting_max_boundary.xs, frame_to_plot.painting_max_boundary.ys, 'k')
        plt.plot(frame_to_plot.painting_min_boundary.xs, frame_to_plot.painting_min_boundary.ys, 'b')
        plt.plot(frame_to_plot.painting_overlap_boundary.xs, frame_to_plot.painting_overlap_boundary.ys, 'r')
        plt.plot(frame_to_plot.frame_exterior_boundary.xs, frame_to_plot.frame_exterior_boundary.ys, 'g')
        plt.show()
