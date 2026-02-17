import random, math

def mutate(genome):
    g = dict(genome)

    g["A"] += random.uniform(-0.05,0.05)
    g["B"] += random.uniform(-0.05,0.05)
    g["W"] += random.uniform(-0.05,0.05)

    modes = ["sin","cos","sin_rr","cos_rr","sin_cos","sin_mul_cos"]

    for k in ["mode_a","mode_b","mode_c"]:
        if random.random()<0.2:
            g[k] = random.choice(modes)

    return g
