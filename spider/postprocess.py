import re
import time
from typing import Any, Callable, Generator


class Splitter():

    def __init__(self, src: str, split: str, keep: bool, *dest: str):
        self.src = src
        self.split = split
        self.keep = keep
        self.dest = dest

    def __call__(self, **kwargs):
        for k, v in zip(self.dest, kwargs[self.src].split(self.split)):
            kwargs[k] = v
        if not self.keep and self.src not in self.dest:
            del kwargs[self.src]
        return kwargs


class Converter():

    def __init__(self, src: str, to: type):
        self.src = src
        self.to = to

    def __call__(self, **kwargs):
        try:
            kwargs[self.src] = self.to(kwargs[self.src])
        except ValueError:
            kwargs[self.src] = 0
        return kwargs


class DateField():

    def __init__(self, src: str, format_str: str):
        self.src = src
        self.format_str = format_str

    def __call__(self, **kwargs):
        try:
            kwargs[self.src] = time.mktime(
                time.strptime(kwargs[self.src], self.format_str))
        except ValueError:
            kwargs[self.src] = 0
        return kwargs


class Extractor():

    def __init__(self, src: str, keep: bool, *dest: str):
        self.src = src
        self.keep = keep
        if dest:
            self.dest = dest
        else:
            self.dest = (src, )

    @staticmethod
    def extract_num(s: str) -> Generator[str, None, None]:
        yield from re.findall('[\d\.]+', s)

    def __call__(self, **kwargs):
        for k, v in zip(self.dest, self.extract_num(kwargs[self.src])):
            kwargs[k] = v
        if not self.keep and self.src not in self.dest:
            del kwargs[self.src]
        return kwargs


class Encoder():

    def __init__(self, src: str, mapping: dict, default: Any):
        self.src = src
        self.mapping = mapping
        self.default = default

    def __call__(self, **kwargs):
        kwargs[self.src] = self.mapping.get(kwargs[self.src], self.default)
        return kwargs


class Custom():

    def __init__(self, src: str, func: Callable):
        self.src = src
        self.func = func

    def __call__(self, **kwargs):
        kwargs[self.src] = self.func(kwargs[self.src])
        return kwargs


class Processor():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = []

    def addSplitter(self, src: str, split: str, keep: bool, *dest: str):
        self.actions.append(Splitter(src, split, keep, *dest))

    def addConverter(self, src: str, to: type):
        self.actions.append(Converter(src, to))

    def addExtractor(self, src: str, keep: bool, *dest: str):
        self.actions.append(Extractor(src, keep, *dest))

    def addEncoder(self, src: str, mapping: dict, default: Any):
        self.actions.append(Encoder(src, mapping, default))

    def addDate(self, src: str, format_str: str):
        self.actions.append(DateField(src, format_str))

    def addCustom(self, src: str, func: Callable):
        self.actions.append(Custom(src, func))

    def __call__(self, **kwargs):
        try:
            for _ in self.actions:
                kwargs = _(**kwargs)
        except Exception as e:
            print(kwargs)
            print(e)

        return kwargs
