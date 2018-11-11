import itertools
import re


def generate_strings_by_template(template, keys):
    products = [dict(zip(keys, values)) 
                for values in itertools.product(*keys.values())]
    return [template.format(**p) for p in products]


def unpack_template(template):
    return re.findall('\{(\w*)\}', template)


def flatten_list(nested_list):
    return list(itertools.chain.from_iterable(nested_list))