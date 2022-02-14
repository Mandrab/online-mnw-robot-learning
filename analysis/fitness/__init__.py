import matplotlib.pyplot as plt

from collections import defaultdict
from itertools import product
from typing import Dict, List, Any, Callable


def group(dataset: List[Dict], by_key: str, extract_key: str = '') -> Dict:
    result = defaultdict(list)
    for d in dataset:
        result[d[by_key]].append(d if extract_key == '' else d[extract_key])
    return result


def transform(dataset: Dict[Any, List[Any]], strategy: Callable):
    return {k: strategy(vs) for k, vs in dataset.items()}


def boxplot(p_title: str, x_label: str, y_label: str, dataset: Dict[str, List]):
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.boxplot(dataset.values())

    ax.set(title=p_title, xlabel=x_label, ylabel=y_label)
    ax.set_xticks([*range(len(dataset) + 2)], labels=[None, *dataset, None])
    ax.yaxis.grid(True, linestyle='dotted')

    plt.tight_layout()
    plt.show()


def statistics(dataset: List[Dict], by_key: str):
    dataset = group(dataset, by_key)
    dataset = {k: [max(v['fitness']) for v in vs] for k, vs in dataset.items()}

    def to_table(*strings) -> str:
        return '\t\t\t| '.join(map(str, strings))

    print(to_table(by_key, '_ < 40') + '\t\t| 40 <= _ < 50' + '\t| _ >= 50')

    def percentage(key_range) -> float:
        filtered = list(filter(key_range[1], dataset[key_range[0]]))
        return 100.0 * len(list(filtered)) / len(dataset[key_range[0]])

    def formats(v) -> str:
        return '{v:.2f}'.format(v=v) if v < 1000 else '{v:.0e}'.format(v=v)

    ranges = [lambda _: _ < 40, lambda _: 40 <= _ < 50, lambda _: _ >= 50]

    total = 0.0, 0.0, 0.0
    for by_key in dataset:
        statistic = list(map(percentage, product([by_key], ranges)))
        print(to_table(formats(by_key), *map(formats, statistic)))
        total = map(sum, zip(total, statistic))

    print(to_table('Average', *[formats(_ / len(dataset)) for _ in total]))
