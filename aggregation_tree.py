import copy

class ANode(object):
    def __init__(self, name=None):
        self.name = name

    def __call__(self, target):
        raise NotImplementedError()

    def __or__(self, other):
        return OrCombiner([self, other])

    def __and__(self, other):
        return AndCombiner([self, other])

    def __add__(self, other):
        return SumCombiner([self, other])

    def __invert__(self):
        return Negation(self)

class FrozenANode(object):
    def __init__(self, result, children, name):
        self.result = result
        self._children = children
        self.name = name

    def by_name(self, name):
        result = []
        if self.name == name:
            result.append(self)
        else:
            for c in self._children:
                result.extend(c.by_name(name))
        return result

    def __bool__(self):
        return self.result
    # This gives consistent behavior in both Python2 and 3
    __nonzero__ = __bool__

class Combiner(ANode):
    def __init__(self, children, name=None):
        super(Combiner, self).__init__(name=name)
        self._children = children

    def _fold_children(self, target, initial, fun):
        result = initial
        child_results = []
        for c in self._children:
            child_result = c(target)
            child_results.append(child_result)
            result = fun(result, child_result.result)
        return FrozenANode(result, child_results, self.name)

class OrCombiner(Combiner):
    def __call__(self, target):
        return self._fold_children(target, False, lambda a, b: a or b)

class AndCombiner(Combiner):
    def __call__(self, target):
        return self._fold_children(target, True, lambda a, b: a and b)

class SumCombiner(Combiner):
    def __call__(self, target):
        return self._fold_children(target, 0, lambda a, b: a + b)

class MeanCombiner(Combiner):
    def __call__(self, target):
        total = self._fold_children(target, 0, lambda a, b: a + b)
        total.result /= float(len(self._children))
        return total

class Mutator(ANode):
    def __init__(self, child, name=None):
        super(Mutator, self).__init__(name)
        self._child = child

class Threshold(Mutator):
    def __init__(self, child, threshold, name=None):
        super(Threshold, self).__init__(child, name)
        self.threshold = threshold

    def __call__(self, target):
        child_result = self._child(target)
        result = child_result.result > self.threshold
        return FrozenANode(result, [child_result], self.name)

class Negation(Mutator):
    def __call__(self, target):
        child_result = self._child(target)
        result = not child_result.result
        return FrozenANode(result, [child_result], self.name)

    
class A(ANode):
    def __init__(self, fun, name=None):
        super(A, self).__init__(name=name)
        self.fun = fun

    def __call__(self, target):
        return FrozenANode(self.fun(target), [], self.name)


    
