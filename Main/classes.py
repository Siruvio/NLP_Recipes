class ExtractedObject:
    def __init__(self, lemma: str, obj: str, verb: str) -> None:
        self._lemma = lemma
        self._obj = obj
        self._verb = verb
        self._hyper_names = []
        self._best_hyper = -1

    def add_hyper(self, category: str, depth: int, simil: float) -> None:
        triplet = (category, depth, simil)
        self._hyper_names.append(triplet)

        if len(self._hyper_names) == 1:
            self._best_hyper = 0
        else:
            if (depth < self._hyper_names[self._best_hyper][1] or
                    (depth == self._hyper_names[self._best_hyper][1] and
                     simil > self._hyper_names[self._best_hyper][2])):
                self._best_hyper = self._hyper_names.index(triplet)

    def get_lemma(self) -> str:
        return self._lemma

    def get_direct_object(self) -> str:
        return self._obj

    def get_verb(self) -> str:
        return self._verb

    def get_hypers(self) -> [(str, int, float)]:
        return self._hyper_names

    def get_best_hyper(self) -> (str, int, float):
        if self._best_hyper != -1:
            return self._hyper_names[self._best_hyper]
        else:
            return "Other", 0, 0.0
