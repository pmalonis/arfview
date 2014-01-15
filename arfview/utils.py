''' general utilities for the program '''

def is_simple_event(dataset):
    if dataset.attrs['datatype'] >= 1000 and dataset.dtype.names is None:
        return True
    else:
        return False

def is_complex_event(dataset):
    if dataset.attrs['datatype'] >= 1000 and dataset.dtype.names is not None \
    and set(('name', 'start', 'stop')).issubset(dataset.dtype.names):
        return True
    else:
        return False























