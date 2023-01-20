"""
a file to build a frame for a painting
"""
from matplotlib import pyplot as plt

from .dataclasses.coordinate import Coordinate
from .dataclasses.coordinate_list import CoordinateList
from .dataclasses.frame_layout import FrameLayout
from .dataclasses.frame_size import FrameSize
from .dataclasses.painting_information import PaintingInformation


def build_frame(
        painting: PaintingInformation,
        at: Coordinate = Coordinate(x=0, y=0),
        frame: FrameSize = FrameSize(width_in=2, height_in=1)
) -> FrameLayout:
    """ build a frame layout for a painting
    :param painting: the painting to frame
    :param at: the location of the painting
    :param frame: the size of the frame.
    :return: the frame layout
    """

    # find the delta between the min and max painting size
    od_width_delta = painting.width_max_cm - painting.width_min_cm
    od_height_delta = painting.height_max_cm - painting.height_min_cm

    # find the center offset between the min and max painting size
    minimum_edge_at = Coordinate(
        x=at.x + od_width_delta / 2,
        y=at.y + od_height_delta / 2
    )

    # find the interior edge that covers the painting
    interior_edge_at = Coordinate(
        x=at.x + painting.hide_left_offset_cm,
        y=at.y + painting.hide_bottom_offset_cm
    )

    # build a vertex list of the maximum painting boundary
    painting_maximum_boundary = CoordinateList(
        [
            Coordinate(
                x=at.x,
                y=at.y
            ),
            Coordinate(
                x=at.x + painting.width_max_cm,
                y=at.y
            ),
            Coordinate(
                x=at.x + painting.width_max_cm,
                y=at.y + painting.height_max_cm
            ),
            Coordinate(
                x=at.x,
                y=at.y + painting.height_max_cm
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
                x=minimum_edge_at.x + painting.width_min_cm,
                y=minimum_edge_at.y
            ),
            Coordinate(
                x=minimum_edge_at.x + painting.width_min_cm,
                y=minimum_edge_at.y + painting.height_min_cm
            ),
            Coordinate(
                x=minimum_edge_at.x,
                y=minimum_edge_at.y + painting.height_min_cm
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
                        painting.width_max_cm - painting.hide_right_offset_cm - painting.hide_left_offset_cm),
                y=interior_edge_at.y
            ),
            Coordinate(
                x=interior_edge_at.x + (
                        painting.width_max_cm - painting.hide_right_offset_cm - painting.hide_left_offset_cm),
                y=interior_edge_at.y + (
                        painting.height_max_cm - painting.hide_top_offset_cm - painting.hide_bottom_offset_cm)
            ),
            Coordinate(
                x=interior_edge_at.x,
                y=interior_edge_at.y + (
                        painting.height_max_cm - painting.hide_top_offset_cm - painting.hide_bottom_offset_cm)
            ),
            Coordinate(
                x=interior_edge_at.x,
                y=interior_edge_at.y
            ),
        ]
    )

    # build a vertex list of the exterior edge of the frame
    exterior_edge = CoordinateList(
        [
            interior_edge[0] + Coordinate(
                x=-frame.width_cm,
                y=-frame.width_cm
            ),
            interior_edge[1] + Coordinate(
                x=frame.width_cm,
                y=-frame.width_cm
            ),
            interior_edge[2] + Coordinate(
                x=frame.width_cm,
                y=frame.width_cm
            ),
            interior_edge[3] + Coordinate(
                x=-frame.width_cm,
                y=frame.width_cm
            ),
            interior_edge[4] + Coordinate(
                x=-frame.width_cm,
                y=-frame.width_cm
            )
        ]
    )

    # cleanup the vertex lists to get all vertexes into quadrant 1
    # find min x and y
    min_x = abs(exterior_edge.x_min)
    min_y = abs(exterior_edge.y_min)

    # create a offset coordinate
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


def plot_frame(input_frame: FrameLayout, axis_offset: float = 1) -> None:
    """ plot a frame layout
    :param input_frame: the frame layout to plot
    :param axis_offset: the offset to apply to the axis
    """

    # find the min and max axis ranges from the outside boundary
    min_x = input_frame.frame_exterior_boundary.x_min
    max_x = input_frame.frame_exterior_boundary.x_max
    min_y = input_frame.frame_exterior_boundary.y_min
    max_y = input_frame.frame_exterior_boundary.y_max

    # to make the axis equal, find the common min and max between x and y and add small offset
    eq_min = min(min_x, min_y) - axis_offset
    eq_max = max(max_x, max_y) + axis_offset

    plt.xlim(eq_min, eq_max)
    plt.ylim(eq_min, eq_max)
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')

    plt.plot(input_frame.painting_max_boundary.xs, input_frame.painting_max_boundary.ys, 'k')
    plt.plot(input_frame.painting_min_boundary.xs, input_frame.painting_min_boundary.ys, 'b')
    plt.plot(input_frame.painting_overlap_boundary.xs, input_frame.painting_overlap_boundary.ys, 'r')
    plt.plot(input_frame.frame_exterior_boundary.xs, input_frame.frame_exterior_boundary.ys, 'g')
    plt.show()
