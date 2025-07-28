from functools import wraps
from typing import Any, Dict, Tuple


def singleton_per_signature(cls):
    instances: Dict[Tuple[Any, ...], Any] = {}
    initialized_instances: Dict[Tuple[Any, ...], bool] = {}  # Verwende den Signaturschlüssel als Schlüssel

    class ClassWrapper(cls):
        def __new__(cls_, *args, **kwargs):
            # Erzeuge einen Schlüssel basierend auf der Signatur (args und kwargs)
            key = (args, tuple(sorted(kwargs.items())))
            if key not in instances:
                # Neue Instanz erstellen und speichern
                instance = super(ClassWrapper, cls_).__new__(cls_)
                instances[key] = instance
                initialized_instances[key] = False  # Markiere Instanz als nicht initialisiert
            return instances[key]

        def __init__(self, *args, **kwargs):
            # Erzeuge einen Schlüssel basierend auf der Signatur (args und kwargs)
            key = (args, tuple(sorted(kwargs.items())))
            if not initialized_instances.get(key, False):
                # Initialisiere nur, wenn diese Signatur noch nicht initialisiert wurde
                super(ClassWrapper, self).__init__(*args, **kwargs)
                initialized_instances[key] = True  # Markiere die Signatur als initialisiert

    # Behalte die Klasseneigenschaften
    ClassWrapper.__name__ = cls.__name__
    ClassWrapper.__module__ = cls.__module__
    ClassWrapper.__doc__ = cls.__doc__

    return ClassWrapper
