# ===== string cleaning functions ====
def remove_non_ascii(x):
    try:
        y = ''.join([i if 32 < ord(i) < 126 else " " for i in x])
        return y
    except:
        return None


def cat_texts(x):
    return ' '.join(x.astype(str))


