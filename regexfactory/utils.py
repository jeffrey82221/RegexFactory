import copy
from typing import List, Dict, Tuple, Iterator, Callable
import itertools
from functools import reduce
from .pattern import RegexPattern



def reduce_regex_list(regex_list: List[RegexPattern], mapping: Dict[Tuple[RegexPattern], RegexPattern]) -> List[RegexPattern]:
    _regex_list = copy.deepcopy(regex_list)
    _mapping = copy.deepcopy(mapping)
    try:
        merged_regex_from_list = sorted([e for e in _mapping.keys()], key=len, reverse=True)
        for merged_regex_tuple in merged_regex_from_list:
            if set(merged_regex_tuple).issubset(_regex_list):
                for reg in merged_regex_tuple:
                    _regex_list.remove(reg)
                _regex_list.append(_mapping[merged_regex_tuple])
        return _regex_list
    except BaseException as e:
        msg = 'regex_list:' + str(regex_list) + '\n'
        msg += 'mapping:' + str(mapping) + '\n'
        raise ValueError(msg) from e

def find_merge_ways(regex_groups: List[RegexPattern], example_inference_callable: Callable=lambda x: None) -> Dict[Tuple[RegexPattern], RegexPattern]:
    """
    Find way to merge a set of regex and return the merging way 
    as mapping dictionary. 

    Args:
        - regex_groups: a list of regex to be merged 
    Return:
        - mapping: a dictionary where key is a group of regex to be match to 
            its corresponding regex value. 
    """
    try:
        mapping = dict()
        for mg in _combination_generate(regex_groups):
            ue = reduce(lambda x,y: x|y, map(lambda m: m.examples, mg))
            if sp_char_regex:=example_inference_callable(ue):
                if not any(map(lambda key: ue.issubset(mapping[key]['examples']), mapping.keys())):
                    mapping[tuple(mg)] = {
                        'examples': ue,
                        'regex': sp_char_regex
                    }
        for key in mapping:
            mapping[key] = mapping[key]['regex']
        return mapping
    except BaseException as e:
        msg = 'Input:' + str(regex_groups)
        raise ValueError(msg) from e
    
def _combination_generate(input_list) -> Iterator[Tuple[RegexPattern]]:
    """
    Generate all subset combination of the input set 

    Args:
        input_list: the input set 
    Return:
        a generator that generate the combination in tuple 
    """
    length = len(input_list)
    for i in range(length-1, 0, -1):
        for e in itertools.combinations(input_list, i):
            yield e