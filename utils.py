

from pathlib import Path
import random
import string

random.seed("benchmark")

IMAGES_PATH = Path('./test_images')


def get_random_data():
    t = random.choice('int', 'float', 'str', 'list')
    if t == 'int':
        return random.randint(-2147483648, 2147483647)
    elif t == 'float':
        return random.random()
    elif t == 'str':
        return ''.join(random.choices(string.printable, k=random.randint[50, 1000]))
    else:
        return [random.random() for _ in range(random.randint(10, 200))]


def generate_random_key(k=25):
    return ''.join(random.choices(string.ascii_letters+string.digits, k))


def generate_dict(keys=10000, depth=10):
    data = {}
    
    for _ in range(keys):
        level = data.setdefault(generate_random_key(25), {})
        for _ in range(depth-1):
            level = level.setdefault(generate_random_key(25), {})
        
        level[generate_random_key(25)] = get_random_data()


def read_image(img):
    with open(img, "rb") as f:
        return f.read()
