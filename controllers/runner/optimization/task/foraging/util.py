from math import atan2, cos, isclose, sin


def is_facing(robot, obj) -> bool:
    """ Check if the robot is facing (i.e., is in front) the object. """

    if not obj.getContactPoints():
        return False

    # get the robot position and direction
    robot_x, _, robot_y = robot.getFromDef('evolvable').getPosition()
    _, a, _, b = robot.getFromDef('evolvable').getField('rotation').getSFRotation()

    # get obj contact point and calculate its angle/direction referred to the robot center
    contact_x, _, contact_y = obj.getContactPoint(0)
    contact_angle = atan2(robot_x - contact_x, robot_y - contact_y)

    # calculate the cos and sin of the robot direction and collision point
    cr, sr = cos(a * b), sin(a * b)
    cc, sc = cos(contact_angle), sin(contact_angle)

    # calculate if the robot faces an object on its north, east, sud, west
    ns_facing = isclose(cc, cr, abs_tol=0.5) and sr * sc > 0
    we_facing = isclose(sc, sr, abs_tol=0.5) and cr * cc > 0

    return ns_facing or we_facing


def on_nest(robot):

    pgs = next(filter(lambda sensor: sensor.startswith('gs0'), robot.sensors))
    ngs = next(filter(lambda sensor: sensor.startswith('gs2'), robot.sensors))

    return pgs.value < 800 and ngs.value > 200


def on_plate(robot):

    pgs = next(filter(lambda sensor: sensor.startswith('gs0'), robot.sensors))
    ngs = next(filter(lambda sensor: sensor.startswith('gs2'), robot.sensors))

    return pgs.value > 900 and ngs.value < 100
