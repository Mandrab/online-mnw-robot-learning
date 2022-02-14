import matplotlib.patches as ptc
import matplotlib.pyplot as plt

from collections import defaultdict
from itertools import product
from typing import Dict, List, Any, Callable


def formats(v) -> str:
    return '{v:.2f}'.format(v=v) if v < 1000 else '{v:.0e}'.format(v=v)


def group(data: List[Dict], by_key: str, extract_key: str = '') -> Dict:
    result = defaultdict(list)
    for d in data:
        result[d[by_key]].append(d if extract_key == '' else d[extract_key])
    return result


def transform(data: Dict[Any, List[Any]], strategy: Callable):
    return {k: strategy(vs) for k, vs in data.items()}


def boxplot(p_title: str, x_label: str, y_label: str, data: Dict[str, List]):
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.boxplot(data.values())

    ax.set(title=p_title, xlabel=x_label, ylabel=y_label)
    ax.set_xticks([*range(len(data) + 2)], labels=[None, *data, None])
    ax.yaxis.grid(True, linestyle='dotted')

    plt.tight_layout()
    plt.show()


def statistics(data: List[Dict], by_key: str):
    """
    Print some statistics related to fitness according to a specific property of
    the configuration.
    """
    data = group(data, by_key)
    data = {k: [max(v['fitness']) for v in vs] for k, vs in data.items()}

    def to_table(*strings) -> str:
        return '\t\t\t| '.join(map(str, strings))

    print(to_table(by_key, '_ < 40') + '\t\t| 40 <= _ < 50' + '\t| _ >= 50')

    def percentage(key_range) -> float:
        filtered = list(filter(key_range[1], data[key_range[0]]))
        return 100.0 * len(list(filtered)) / len(data[key_range[0]])

    ranges = [lambda _: _ < 40, lambda _: 40 <= _ < 50, lambda _: _ >= 50]

    total = 0.0, 0.0, 0.0
    for by_key in data:
        statistic = list(map(percentage, product([by_key], ranges)))
        print(to_table(formats(by_key), *map(formats, statistic)))
        total = map(sum, zip(total, statistic))

    print(to_table('Average', *[formats(_ / len(data)) for _ in total]))


def evolutions(data: List[Dict], by_key: str):
    """"
    Plot the evolution of the configurations fitness according to a property
    """
    fig, ax = plt.subplots()

    groups = group(data, by_key, 'fitness')
    colors = plt.get_cmap('tab10')

    for key_i, (k, v) in enumerate(groups.items()):
        iteration_count = len(v[0])

        for i in range(iteration_count):
            fitness = list(map(max, [_[:i + 1] for _ in v]))
            average = sum(fitness) / len(fitness)

            ax.plot(i, average, 'o', markersize=1, color=colors(key_i), label=k)

    plt.title('Average fitness evolution according to iterations')
    patches = [
        ptc.Patch(color=colors(i), label=by_key + ' ' + formats(k))
        for i, k in enumerate(groups)
    ]
    plt.legend(handles=patches, loc='lower right')
    plt.show()
