def correct_cui(true:set, predicted:set):
    return len(true & predicted)