import matplotlib.patches as ptc
import matplotlib.pyplot as plt

from collections import defaultdict
from functools import reduce
from itertools import product
from typing import Dict, List, Any, Callable


def formats(v) -> str: return ('{v:.2f}' if v < 1000 else '{v:.0e}').format(v=v)


def group(data: List[Dict], by_key: str, extract_key: str = '') -> Dict:
    result = defaultdict(list)
    for d in data:
        result[d[by_key]].append(d if extract_key == '' else d[extract_key])
    return result


def transform(data: Dict[Any, List[Any]], strategy: Callable):
    return {k: strategy(vs) for k, vs in data.items()}


def boxplot(p_title: str, y_label: str, x_label: str, data: Dict[str, List]):
    """Create a boxplot with x = dict keys; y = dict value."""
    fig, ax = plt.subplots()

    data = sorted(data.items(), key=lambda _: _[0][0], reverse=True)
    ax.boxplot([v for _, v in data], vert=False)

    ax.set(title=p_title, xlabel=x_label, ylabel=y_label)
    labels = [None, *[k for k, _ in data], None]
    ax.set_yticks([*range(len(data) + 2)], labels=labels)
    ax.yaxis.grid(True, linestyle='dotted')

    plt.tight_layout()
    plt.show()


def statistics(data: List[Dict], by_key: str, limits: List[float]):
    """
    Print some statistics related to fitness according to a specific property of
    the configuration.
    """
    if len(limits := sorted(limits)) <= 0:
        return

    ranges = [(float('-inf'), next(iter(limits)))] + [*zip(limits, limits[1:])]
    ranges += [(next(iter(reversed(limits))), float('inf'))]

    data = group(data, by_key)
    data = {k: [max(v['fitness']) for v in vs] for k, vs in data.items()}

    def to_table(*strings) -> str:
        return '\t\t\t| '.join(map(str, strings))

    print(to_table(by_key, '\t| '.join(['[%.1f, %.1f)' % _ for _ in ranges])))

    def percentage(key_range) -> float:
        filtered = list(filter(key_range[1], data[key_range[0]]))
        return 100.0 * len(list(filtered)) / len(data[key_range[0]])

    ranges = [lambda _: a <= _ < b for a, b in ranges]

    total = 0.0, 0.0, 0.0
    for by_key in data:
        statistic = list(map(percentage, product([by_key], ranges)))
        print(to_table(formats(by_key), *map(formats, statistic)))
        total = map(sum, zip(total, statistic))

    print(to_table('Average', *[formats(_ / len(data)) for _ in total]))


def evolutions(data: List[Dict], by_key: str):
    """"
    Plot the evolution of the configurations fitness according to a property.
    """
    fig, ax = plt.subplots()

    groups = group(data, by_key, 'fitness')
    colors = plt.get_cmap('tab10')

    for key_i, (k, v) in enumerate(groups.items()):
        averages = []
        for i in range(len(v[0])):
            fitness = list(map(max, [_[:i + 1] for _ in v]))
            averages.append(sum(fitness) / len(fitness))

        ax.plot(averages, color=colors(key_i), label=k)

    ax.set(xlabel='Iterations', ylabel='Fitness')

    plt.title('Fitness evolution according to iterations (average of maxima)')
    patches = [
        ptc.Patch(color=colors(i), label=by_key + ' ' + formats(k))
        for i, k in enumerate(groups)
    ]
    plt.legend(handles=patches, loc='lower right')
    plt.show()


def evolution(data: Dict) -> Dict:
    return reduce(
        lambda a, b: a | dict(b),
        [
            ((f'initial {k}', [_[0] for _ in v]), (f'max {k}', [*map(max, v)]))
            for k, v in dict(data).items()
        ],
        defaultdict(list)
    )
