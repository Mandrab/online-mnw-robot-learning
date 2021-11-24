from controller import Robot


class Sensor(str):
    def init(self, robot: Robot, update_frequency: int):
        self.__robot = robot
        self.__device = robot.getDevice(self)
        self.__device.enable(update_frequency)

    @property
    def read(self):
        return self.__device.getValue()


# Map the sensor angle to its string name.
# The angle is clock wise from the front of the robot.
sensors = {
    'A25': Sensor('ps0'),   # ~front
    'A45': Sensor('ps1'),   # front right
    'A90': Sensor('ps2'),   # right
    'A155': Sensor('ps3'),  # back right
    'A205': Sensor('ps4'),  # back left
    'A270': Sensor('ps5'),  # left
    'A315': Sensor('ps6'),  # front left
    'A335': Sensor('ps7'),  # ~front
}


class Motor(str):
    @property
    def robot(self):
        return self.__robot

    @robot.setter
    def robot(self, robot: Robot):
        self.__robot = robot
        self.__device = robot.getDevice(self)
        self.__device.setVelocity(0.0)

    @property
    def speed(self) -> float:
        return self.__device.getVelocity()

    @speed.setter
    def speed(self, speed: float):
        self.__device.setVelocity(speed)


motors = {
    'LEFT': Motor('left wheel motor'),
    'RIGHT': Motor('right wheel motor')
}
