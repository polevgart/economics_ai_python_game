class Registrant:
    def __init__(self):
        self._participants = {}

    def register(self, participant: type):
        assert participant.__name__ not in self._participants
        self._participants[participant.__name__] = participant

    def get_participant(self, name):
        if name not in self._participants:
            raise ValueError(f"Participant {name} is not registered")

        return self._participants[name]


strategies_registrant = Registrant()


def register_strategy(strategy_cls):
    strategies_registrant.register(strategy_cls)
    return strategy_cls
