from typing import Dict, List, Callable, Tuple
from itertools import product
from concurrent.futures import ProcessPoolExecutor
from random import random, choice
from time import perf_counter
from multiprocessing import Manager, Pool, get_context
from decimal import Decimal

from deap import creator, base, tools, algorithms


OUTPUT_FUNC = Callable[[str], None]
EVALUATE_FUNC = Callable[[dict], dict]
KEY_FUNC = Callable[[list], float]


# Create individual class used in genetic algorithm optimization
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)


class OptimizationSetting:
    """
    Setting for runnning optimization.
    """

    def __init__(self) -> None:
        """"""
        self.params: Dict[str, List] = {}
        self.target_name: str = ""

    def add_parameter(
        self,
        name: str,
        start: float,
        end: float = None,
        step: float = None
    ) -> Tuple[bool, str]:
        """"""
        if isinstance(start, list):
            self.params[name] = start
            return True, "列表参数添加成功"

        if end is None and step is None or start == end:
            self.params[name] = [start]
            return True, "固定参数添加成功"

        if start >= end:
            return False, "参数优化起始点必须小于终止点"

        if step <= 0:
            return False, "参数优化步进必须大于0"

        decimal_value = Decimal(str(start))
        decimal_end = Decimal(str(end))
        decimal_step = Decimal(str(step))
        value_type = int if isinstance(start, int) and isinstance(step, int) else float
        value_list = []

        while decimal_value <= decimal_end:
            value_list.append(value_type(decimal_value))
            decimal_value += decimal_step

        self.params[name] = value_list

        return True, f"范围参数添加成功，数量{len(value_list)}"

    def set_target(self, target_name: str) -> None:
        """"""
        self.target_name = target_name

    def generate_settings(self) -> List[dict]:
        """"""
        keys = self.params.keys()
        values = self.params.values()
        products = list(product(*values))

        settings = []
        for p in products:
            setting = dict(zip(keys, p))
            settings.append(setting)

        return settings


def check_optimization_setting(
    optimization_setting: OptimizationSetting,
    output: OUTPUT_FUNC = print
) -> bool:
    """"""
    if not optimization_setting.generate_settings():
        output("优化参数组合为空，请检查")
        return False

    if not optimization_setting.target_name:
        output("优化目标未设置，请检查")
        return False

    return True


def run_bf_optimization(
    evaluate_func: EVALUATE_FUNC,
    optimization_setting: OptimizationSetting,
    key_func: KEY_FUNC,
    max_workers: int = None,
    output: OUTPUT_FUNC = print
) -> List[Tuple]:
    """Run brutal force optimization"""
    settings: List[Dict] = optimization_setting.generate_settings()

    output(f"开始执行穷举算法优化")
    output(f"参数优化空间：{len(settings)}")

    start: int = perf_counter()

    with ProcessPoolExecutor(
        max_workers,
        mp_context=get_context("spawn")
    ) as executor:
        results: List[Tuple] = list(executor.map(evaluate_func, settings))
        results.sort(reverse=True, key=key_func)

        end: int = perf_counter()
        cost: int = int((end - start))
        output(f"穷举算法优化完成，耗时{cost}秒")

        return results


def run_ga_optimization(
    evaluate_func: EVALUATE_FUNC,
    optimization_setting: OptimizationSetting,
    key_func: KEY_FUNC,
    max_workers: int = None,
    population_size: int = 100,
    ngen_size: int = 30,
    output: OUTPUT_FUNC = print
) -> List[Tuple]:
    """Run genetic algorithm optimization"""
    # Define functions for generate parameter randomly
    buf: List[Dict] = optimization_setting.generate_settings()
    settings: List[Tuple] = [list(d.items()) for d in buf]

    def generate_parameter() -> list:
        """"""
        return choice(settings)

    def mutate_individual(individual: list, indpb: float) -> tuple:
        """"""
        size = len(individual)
        paramlist = generate_parameter()
        for i in range(size):
            if random() < indpb:
                individual[i] = paramlist[i]
        return individual,

    # Set up multiprocessing Pool and Manager
    with Manager() as manager, Pool(max_workers) as pool:
        # Create shared dict for result cache
        cache: Dict[Tuple, Tuple] = manager.dict()

        # Set up toolbox
        toolbox = base.Toolbox()
        toolbox.register("individual", tools.initIterate, creator.Individual, generate_parameter)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", mutate_individual, indpb=1)
        toolbox.register("select", tools.selNSGA2)
        toolbox.register("map", pool.map)
        toolbox.register(
            "evaluate",
            ga_evaluate,
            cache,
            evaluate_func,
            key_func
        )

        total_size: int = len(settings)
        pop_size: int = population_size                      # number of individuals in each generation
        lambda_: int = pop_size                              # number of children to produce at each generation
        mu: int = int(pop_size * 0.8)                        # number of individuals to select for the next generation

        cxpb: float = 0.95         # probability that an offspring is produced by crossover
        mutpb: float = 1 - cxpb    # probability that an offspring is produced by mutation
        ngen: int = ngen_size    # number of generation

        pop: list = toolbox.population(pop_size)

        # Run ga optimization
        output(f"开始执行遗传算法优化")
        output(f"参数优化空间：{total_size}")
        output(f"每代族群总数：{pop_size}")
        output(f"优良筛选个数：{mu}")
        output(f"迭代次数：{ngen}")
        output(f"交叉概率：{cxpb:.0%}")
        output(f"突变概率：{mutpb:.0%}")

        start: int = perf_counter()

        algorithms.eaMuPlusLambda(
            pop,
            toolbox,
            mu,
            lambda_,
            cxpb,
            mutpb,
            ngen,
            verbose=False
        )

        end: int = perf_counter()
        cost: int = int((end - start))

        output(f"遗传算法优化完成，耗时{cost}秒")

        results: list = list(cache.values())
        results.sort(reverse=True, key=key_func)
        return results


def ga_evaluate(
    cache: dict,
    evaluate_func: callable,
    key_func: callable,
    parameters: list
) -> float:
    """
    Functions to be run in genetic algorithm optimization.
    """
    tp: tuple = tuple(parameters)
    if tp in cache:
        result: tuple = cache[tp]
    else:
        setting: dict = dict(parameters)
        result: dict = evaluate_func(setting)
        cache[tp] = result

    value: float = key_func(result)
    return (value, )
