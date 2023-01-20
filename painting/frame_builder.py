"""
a class to build a frame for a painting
"""
from matplotlib import pyplot as plt

from painting.dataclasses.coordinate import Coordinate
from painting.dataclasses.coordinate_list import CoordinateList
from painting.dataclasses.frame_layout import FrameLayout
from painting.dataclasses.frame_size import FrameSize
from painting.dataclasses.painting_information import PaintingInformation
from painting.enums.frame_coordinate import FrameCoordinate
from painting.mathematics.units import (
    cm_to_in,
    in_to_tape_measure
)


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

    def calculate_build_dimensions(self):
        """ calculate the build dimensions for the frame

        :return:
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

        # cast the inner build dimensions to inches
        bottom_id_in = cm_to_in(bottom_id_cm)
        right_id_in = cm_to_in(right_id_cm)
        top_id_in = cm_to_in(top_id_cm)
        left_id_in = cm_to_in(left_id_cm)

        # cast the outer build dimensions to inches
        bottom_od_in = in_to_tape_measure(cm_to_in(bottom_od_cm))
        right_od_in = in_to_tape_measure(cm_to_in(right_od_cm))
        top_od_in = in_to_tape_measure(cm_to_in(top_od_cm))
        left_od_in = in_to_tape_measure(cm_to_in(left_od_cm))

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
