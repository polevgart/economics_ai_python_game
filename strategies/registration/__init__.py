class Registrant:
    def __init__(self):
        self._participants = {}

    def registry(self, participant: type):
        assert participant.__name__ not in self._participants
        self._participants[participant.__name__] = participant

    def get_participant(self, name):
        if name not in self._participants:
            raise ValueError(f"Participant {name} is not registered")

        return self._participants[name]


strategies_registrant = Registrant()


def registry_strategy(strategy_cls):
    strategies_registrant.registry(strategy_cls)
    return strategy_cls
