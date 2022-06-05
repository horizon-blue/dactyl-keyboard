from helpers_solid import *
import os.path as path
import numpy
import cadquery as cq

ball_diam = 34  # ball diameter
ball_space = 1  # additional room around ball in socket, 1mm


def get_ball(with_space: False):
    diam = ball_diam
    if with_space:
        diam += ball_space
    return sphere(diam / 2)


def trackball_rim():

    return translate(   # translate A
        difference(
            cylinder(25, 8),
            [translate(cylinder(22.7, 12), [0, 0, -1]),
             translate(box(4, 4, 4), [24, 0, 2.5])]),
        [0, 0, 22.5])  # translate A coords


def gen_holder():
    # PMW3360 dimensions
    # 28mm x 21mm
    l = 28  # not used for now, fudged with base_shape build
    w = 22
    h = 4.0

    # 24mm between screw centers
    screw_dist = 24
    # Screw holes 2.44mm, 2.2mm for snug tapped fit
    screw_hole_d = 2.2

    # circles at either side
    cyl1 = translate(cylinder(w / 2, h, 100), (0, 5, 0))
    cyl2 = translate(cylinder(w / 2, h, 100), (0, -5, 0))

    # tape those bits together
    base_shape = hull_from_shapes([cyl1, cyl2])

    # Ball with 2mm space extra diameter for socket
    ball = translate(get_ball(True), (0, 0, 17.8))

    # Screw holes with a bit of extra height to subtract cleanly
    # May need to be offset by one, as per the bottom hole...?
    screw1 = translate(cylinder(screw_hole_d / 2, h + 1, 20), (0, screw_dist / 2, 0))
    screw2 = translate(cylinder(screw_hole_d / 2, h + 1, 20), (0, -(screw_dist / 2), 0))

    # Attempt at bottom hole, numbers mostly fudged but seems in ballpark
    bottom_hole = union([translate(box(4.5, 4, 6), (0, -2, 0)), translate(cylinder(2.25, 6, 40), (0, 0, 0))])

    final = difference(base_shape, [ball, screw1, screw2, bottom_hole])

    return final  # translate(final, [0, l / 2, 0])


def coords(angle, dist):
    x = numpy.sin(angle) * dist
    y = numpy.cos(angle) * dist
    return x, y


def gen_socket_shape(radius, wall):
    diam = radius * 2
    ball = sphere(radius)
    socket_base = difference(ball, [translate(box(diam + 1, diam + 1, diam), (0, 0, diam / 2))])
    top_cylinder = translate(difference(cylinder(radius, 4), [cylinder(radius - wall, 6)]), (0, 0, 2))
    socket_base = union([socket_base, top_cylinder])

    return socket_base


def socket_bearing_fin(outer_r, outer_depth, axle_r, axle_depth, cut_offset, groove):
    pi3 = (numpy.pi / 2)
    l = 20

    x, y = coords(0, l)
    t1 = translate(cylinder(outer_r, outer_depth), (x, y, 0))

    x, y = coords(pi3, l)
    t2 = translate(cylinder(outer_r, outer_depth), (x, y, 0))

    x, y = coords(pi3 * 2, l)
    t3 = translate(cylinder(outer_r, outer_depth), (x, y, 0))

    big_triangle = hull_from_shapes([t1, t2, t3])

    x, y = coords(0, l)
    t4 = translate(cylinder(axle_r, axle_depth), (x, y, 0))

    x, y = coords(pi3, l)
    t5 = translate(cylinder(axle_r, axle_depth), (x, y, 0))

    x, y = coords(pi3 * 2, l)
    t6 = translate(cylinder(axle_r, axle_depth), (x, y, 0))

    if groove:
        t6 = t4

    axle_shaft = hull_from_shapes([t4, t5, t6])
    base_shape = union([big_triangle, axle_shaft])
    cutter = rotate(translate(box(80, 80, 20), (0, cut_offset, 0)), (0, 0, 15))

    return rotate(difference(base_shape, [cutter]), (0, -90, 0))

def gen_sensor(w=22, l=32, t=10, cut=4.7, screw_dia=2, cutout=True):
    shp = union([translate(cylinder(w / 2, t), (0, +(l - w) / 2, 0)),  # start with circle left
                 box(w, l - w, t),  # center box
                 translate(cylinder(w / 2, t), (0, -(l - w) / 2, 0))])  # end with circle right
    if cutout:
        screw_diff = 26.8  # why not 25.4
        screw_exentric = -1.05  # move both screws in Y direction
        offset_screw_1 = -(screw_diff) / 2 - screw_exentric
        offset_screw_2 = +(screw_diff) / 2 + screw_exentric
        offset_sens = 0.0
        t_cut = 1.01 * t
        shp = difference(shp, [
            translate(union([cylinder(cut / 2, t_cut), translate(box(cut, cut, t_cut), (0, -cut / 2, 0))]),
                      (0, offset_sens, 0)),  # rounded box
            translate(cylinder(screw_dia / 2, t_cut), (0, offset_screw_1, 0)),  # screw 1
            translate(cylinder(screw_dia / 2, t_cut), (0, offset_screw_2, 0))])  # screw 2
    return shp


def standard_parts(balldiameter, ring_height, r_gap, t_wall):
    # setup inner variables
    r_ball = balldiameter / 2.0
    r_inner = r_ball + r_gap
    r_outer = r_ball + r_gap + t_wall

    # start with outer wall and top cylinder

    shape = union([sphere(r_outer), translate(cylinder(r_outer, ring_height), (0, 0, ring_height / 2))])

    sensor = difference(translate(gen_sensor(t=r_inner, cutout=True), (0, 0, -r_inner / 2)), [sphere(r_inner)])

    return shape, sensor


def finalize_trackball(shape, ring_height, r_gap, r_inner, r_outer, height):
    shape = difference(shape, [sphere(r_inner),
                               translate(cylinder(1.1 * r_outer, height), (0, 0, height / 2 + ring_height)),
                               # above cylinder
                               translate(cylinder(r_inner, r_outer), (0, 0, r_outer / 2))])  # inner Cylinder
    top_lip = translate(difference(cylinder(r_outer, ring_height / 8), [cylinder(r_inner - (r_gap * 0.92), ring_height / 7)]),
                        (0, 0, ring_height - 0.1))
    cutout = union([translate(gen_sensor(t=r_outer, cutout=False), (0, 0, -r_outer)),
                    translate(cylinder(r_inner, height - r_inner), (0, 0, (height - r_inner) / 2)),
                    sphere(r_inner)])
    cutout = difference(cutout, [top_lip])
    shape = union([shape, top_lip])

    return shape, cutout

def bearing_trackball_socket(balldiameter, ring_height, r_gap, t_wall, bear_do=6, bear_di=3, bear_t=2.5, bolt_d=3.0,
                             bolt_l=8, bolt_extern=False):
    """Generate a trackball sockets for all diameters."""

    # ========== START internal functions ==========
    def trans_bear(shp, rot_r=0, rot_depth=25):
        shp = translate(shp, (-r_ball - bear_do / 2 - 1, 0, -0.5))
        shp = rotate(shp, (90, -rot_depth, rot_r))
        return shp

    def gen_fastening(r=10, t=5, alpha=30, beta=40):
        shp = union([cylinder(r, t),  # start with circle
                     rotate(translate(box(3 * r, 2 * r, t), (1.5 * r, 0, 0)), (0, 0, alpha)),
                     rotate(translate(box(3 * r, 2 * r, t), (1.5 * r, 0, 0)), (0, 0, -beta))])
        return shp

    # ========== END internal functions ==========

    # setup inner variables
    r_ball = balldiameter / 2.0
    r_inner = r_ball + r_gap
    r_outer = r_ball + r_gap + t_wall
    t_bear_gap = r_gap / 2
    height = ring_height + r_outer

    show_ext_obj = False  # Ball and bearing, only for development

    # start with outer wall and top cylinder

    shape, sensor = standard_parts(balldiameter, ring_height, r_gap, t_wall)

    for i in range(3):
        bolt_orientation = 1
        rot = -30 + 120 * i
        # start with outer object
        outer_t = bear_do / 2 + t_wall

        outer = union([gen_fastening(outer_t, bolt_l + 2 * t_wall),
                       translate(box(3 * outer_t, 2 * outer_t, outer_t), (3 * outer_t / 2, 0, 0))])
        shape = union([shape, trans_bear(outer, rot_r=rot)])

        shape = difference(shape,
                           [trans_bear(gen_fastening(bear_do / 2 + t_bear_gap, bear_t + 2 * t_bear_gap), rot_r=rot),
                            # opening for bearing
                            trans_bear(cylinder(bolt_d / 2, bolt_l), rot_r=rot)])  # bolt

        if bolt_extern:
            bolt_insert = trans_bear(translate(cylinder(bolt_d / 2, r_ball), (0, 0, bolt_orientation * r_ball / 2)),
                                     rot_r=rot)
            bolt_inspect = trans_bear(translate(cylinder(.75, r_ball), (0, 0, -bolt_orientation * r_ball / 2)),
                                      rot_r=rot)
            shape = difference(shape, [bolt_insert, bolt_inspect])
        else:
            bolt_insert = trans_bear(gen_fastening(bolt_d / 2.1, bolt_l * 1.1, alpha=25, beta=-25), rot_r=rot)
            shape = difference(shape, [bolt_insert])

    shape, cutout = finalize_trackball(shape, ring_height, r_gap, r_inner, r_outer, height)

    if show_ext_obj:
        all_sh = [shape, sphere(r_ball)]
        for i in range(3):
            rot = -60 + 120 * i
            all_sh.append(
                trans_bear(difference(cylinder(bear_do / 2, bear_t), [cylinder(bolt_d / 2, bolt_l)]), rot_r=rot))
        shape = union(all_sh)

    cutout_inlets = [cutout]
    for i in range(3):
        bolt_orientation = 1
        rot = -30 + 120 * i
        #  rot = 0
        cutout_inlets.append(trans_bear(gen_fastening(bear_do / 2 + t_bear_gap, bear_t + t_bear_gap), rot_r=rot))
    cutout = union(cutout_inlets)

    return shape, cutout, sensor

def track_outer():
    wall = 4
    ball = gen_socket_shape((ball_diam + wall) / 2, wall / 2)
    outer_radius = 4
    outer_width = 5
    axle_radius = 3
    axle_width = 8
    base_fin = socket_bearing_fin(outer_radius, outer_width, axle_radius, axle_width, -22, False)
    offsets = (0, -2, -6)

    cutter1 = translate(base_fin, offsets)
    cutter2 = rotate(translate(base_fin, offsets), (0, 0, 120))
    cutter3 = rotate(translate(base_fin, offsets), (0, 0, 240))

    return union([ball, cutter1, cutter2, cutter3])


def track_cutter():
    wall = 4
    ball = gen_socket_shape(ball_diam / 2, wall / 2)
    outer_radius = 2.5
    outer_width = 3
    axle_radius = 1.5
    axle_width = 6.5
    base_fin = socket_bearing_fin(outer_radius, outer_width, axle_radius, axle_width, -25, True)
    offsets = (0, -2, -6)

    cutter1 = translate(base_fin, offsets)
    cutter2 = rotate(translate(base_fin, offsets), (0, 0, 120))
    cutter3 = rotate(translate(base_fin, offsets), (0, 0, 240))

    return union([ball, cutter1, cutter2, cutter3])


def cq_stuff():
    return (
        cq.Sketch()
            .segment((0., 0), (0., 2.))
            .segment((2.,0))
            .close()
            .arc((.6, .6), 0.4, 0., 360.)
            .assemble(tag='face')
            .edges('%LINE', tag='face')
            .vertices()
            .chamfer(0.2)
    )


def gen_track_socket():
    return difference(track_outer(), [translate(track_cutter(), [0.001, 0, 0])])


# cutter_fin = socket_bearing_fin(7, 3, 2, 7, -35)
# main_fin = socket_bearing_fin(10, 7, 5, 10, -25)

# result = cq_stuff()
# export_file(shape=result, fname=path.join("..", "things", "cq_play"))

shape, cutout, no = bearing_trackball_socket(34, 8, 1, 3, bear_do=6, bear_di=3, bear_t=2.5, bolt_d=3, bolt_l=6)
export_file(shape=difference(shape, [cutout]), fname=path.join("..", "things", "trackball_bearing_cutout"))

# inner_fin = socket_bearing_fin(2.5, 3, 1.5, 6.5, -25, True)
# outer_fin = socket_bearing_fin(4, 5, 3, 8, -22, False)
# export_file(shape=union([difference(shape, [cutout]), sensor]), fname=path.join("..", "things", "trackball_bearing_socket"))
# export_file(shape=cutout, fname=path.join("..", "things", "trackball_bearing_cutout"))
# export_file(shape=difference(outer_fin, [inner_fin]), fname=path.join("..", "things", "trackball_bearing_socket"))
