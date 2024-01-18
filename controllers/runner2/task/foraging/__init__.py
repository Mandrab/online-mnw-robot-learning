from inout.loader import configs
from simulation.replica import range2range
from webots.supervisor import supervisor

TASK_TYPE = configs["task"]["type"]
TIME_STEP = configs["task"]["time_step_ms"]
MAX_INPUT = configs["sensors"]["max_input"]
MAX_OUTPUT = configs["actuators"]["max_output"]


def gripper_action(value: float):

    # if the control signal is greater than the threshold, commute the state of the gripper
    gripper_action.__dict__["state_changed"] = value > MAX_OUTPUT / 2
    if gripper_action.__dict__["state_changed"]:
        gripper_action.__dict__["close"] = not gripper_action.__dict__["close"]


gripper_action.__dict__["close"] = False
gripper_action.__dict__["state_changed"] = False

if TASK_TYPE == "FORAGING":
    # REVERSE GROUND SENSOR

    # get the ground sensor device
    gs = supervisor.getDevice("gs2")
    gs.enable(TIME_STEP)

    # override the ground sensor device with a function that returns the negation of its value
    gs.getValue = lambda: range2range(supervisor.getDevice("gs0").getValue(), (0, MAX_INPUT), (MAX_INPUT, 0))

    # GRIPPER ACTUATOR

    # get the LED device
    gripper = supervisor.getDevice("gripper")

    # override the set velocity to act as a gripper in this specific task
    gripper.setVelocity = gripper_action
    gripper.setPosition = lambda _: None

    gripper.is_state_changed = lambda: gripper_action.__dict__["state_changed"]
    gripper.is_close = lambda: gripper_action.__dict__["close"]


    def set_prey_index(prey_index: int | None):
        gripper_action.__dict__["prey_index"] = prey_index


    gripper.set_prey_index = set_prey_index
    gripper.get_prey_index = lambda: gripper_action.__dict__.get("prey_index", None)
