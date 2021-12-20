from controllers.runner.utils import adapt


assert adapt(0, (0, 10), (0, 5)) == 0
assert adapt(5, (0, 10), (0, 5)) == 2.5
assert adapt(10, (0, 10), (0, 5)) == 5
assert adapt(-10, (-10, 10), (0, 5)) == 0
assert adapt(0, (-10, 10), (0, 5)) == 2.5
assert adapt(10, (-10, 10), (0, 5)) == 5
assert adapt(-10, (-10, 0), (0, 5)) == 0
assert adapt(-5, (-10, 0), (0, 5)) == 2.5
assert adapt(0, (-10, 0), (0, 5)) == 5
assert adapt(0, (0, 10), (-5, 5)) == -5
assert adapt(5, (0, 10), (-5, 5)) == 0
assert adapt(10, (0, 10), (-5, 5)) == 5
assert adapt(0, (0, 10), (0, -5)) == 0
assert adapt(5, (0, 10), (0, -5)) == -2.5
assert adapt(10, (0, 10), (0, -5)) == -5
assert adapt(0, (0, 10), (5, -5)) == 5
assert adapt(5, (0, 10), (5, -5)) == 0
assert adapt(10, (0, 10), (5, -5)) == -5
assert adapt(0, (-10, 0), (0, 5)) == 5
assert adapt(-5, (-10, 0), (0, 5)) == 2.5
assert adapt(-10, (-10, 0), (0, 5)) == 0
