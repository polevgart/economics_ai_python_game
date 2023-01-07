import argparse
import yaml
import pickle


def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to yaml config")

    args = parser.parse_args()

    with open(args.config) as fin:
        config = yaml.safe_load(fin)

    return config


def group(iter_obj, group_size):
    yield from zip(*(iter(iter_obj),) * group_size)


def load_pickle(config, cls: type):
    pickle_filename = config.get("load_pickle", {}).get(cls.__name__)
    if not pickle_filename:
        return

    with open(pickle_filename, "rb") as fin:
        return pickle.load(fin)


def load_pickle_or_init(config, cls: type):
    obj = load_pickle(config, cls)
    if obj:
        return obj

    return cls(**config.get(cls.__name__, {}))


def dump_pickle_if_need(config, object):
    pickle_filename = config.get("dump_pickle", {}).get(object.__class__.__name__)
    if not pickle_filename:
        return

    with open(pickle_filename, "wb") as fout:
        pickle.dump(object, fout)
