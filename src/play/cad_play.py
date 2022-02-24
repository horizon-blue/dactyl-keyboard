from helpers_cadquery import *
from os import path
import math
import random
import vg


def plate():
    length = 80.0
    height = 60.0
    thickness = 10.0
    center_hole_dia = 22.0

    result = (cq.Workplane("XY").box(length, height, thickness).faces(">Z").workplane().hole(center_hole_dia))
    return result


def circle_extrude():
    result = cq.Workplane("front").circle(2.0)
    result = result.pushPoints([(1.5, 0), (0, 1.5), (-1.5, 0), (0, -1.5)])
    result = result.circle(0.25)
    result = result.extrude(-0.125)
    return result


def dotproduct(v1, v2):
    return sum((a * b) for a, b in zip(v1, v2))


def length(v):
    return math.sqrt(dotproduct(v, v))


def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def multiDimenDist(point1, point2):
    # find the difference between the two points, its really the same as below
    deltaVals = [point2[dimension] - point1[dimension] for dimension in range(len(point1))]
    runningSquared = 0
    # because the pythagarom theorm works for any dimension we can just use that
    for coOrd in deltaVals:
        runningSquared += coOrd ** 2
    return runningSquared ** (1 / 2)


def findVec(point1, point2, unitSphere=False):
    # setting unitSphere to True will make the vector scaled down to a sphere with a radius one, instead of it's orginal length
    finalVector = [0 for coOrd in point1]
    for dimension, coOrd in enumerate(point1):
        # finding total differnce for that co-ordinate(x,y,z...)
        deltaCoOrd = point2[dimension] - coOrd
        # adding total difference
        finalVector[dimension] = deltaCoOrd
    if unitSphere:
        totalDist = multiDimenDist(point1, point2)
        unitVector = []
        for dimen in finalVector:
            unitVector.append(dimen / totalDist)
        return unitVector
    else:
        return finalVector


def try_vect():
    pts = [
        [1, 1, 5],
        [1, -1, 5],
        [-1, 1, 5],
        [-1, -1, 5]
    ]

    for pnt in pts:
        vec1 = np.array([0, 0, 0])
        vec2 = np.array(pnt)

        vector = vg.angle(vec1, vec2)
        print(vector)


def add_branch(shape, origin, vec):
    return shape.union(cq.Solid.makeCylinder(pnt=origin, dir=vec, radius=0.2, height=10))


def play():
    origin = cq.Vector(0, 0, 5)
    vecs = [
        cq.Vector(random.randrange(1, 5), random.randrange(1, 5), random.randrange(2, 7)),
        cq.Vector(random.randrange(1, 5), random.randrange(-5, -1), random.randrange(2, 7)),
        cq.Vector(random.randrange(-5, -1), random.randrange(-5, -1), random.randrange(2, 7)),
        cq.Vector(random.randrange(-5, -1), random.randrange(1, 5), random.randrange(2, 7))
    ]

    # base = cq.Workplane("XY").circle(0.5).extrude(10)
    base = cq.Workplane("XY").box(1, 1, 10)
    top = base  # base.faces(">Z").vertices()

    for vec in vecs:
        top = add_branch(top, origin, vec)

    result = base.union(top)
    # result = result.pushPoints([(1.5, 0), (0, 1.5), (-1.5, 0), (0, -1.5)])
    # result = result.circle(0.25)
    # result = result.center(-1.5, 1.5).circle(0.25)
    # result = result.extrude(0.25)
    return result


def connect_two_points():
    point_1 = [-10, -3, -4]
    point_2 = [4, 8, 9]

    unit_1 = vector_1 / np.linalg.norm(vector_1)
    unit_2 = vector_2 / np.linalg.norm(vector_2)
    dot = np.dot(unit_1, unit_2)

    print(dot)

def rj9_cube():
    debugprint('rj9_cube()')
    shape = box(14.78, 13, 22.38)

    return shape


def run():
    # try_vect()
    cq.exporters.export(rj9_cube(), "../../things/rj9.stl", exportType="STL")
    # export_stl(play(), path.join("..", "..", "things", "joyful"))
    # connect_two_points()


run()
