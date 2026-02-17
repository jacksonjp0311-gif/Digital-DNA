import json, math, random

GENOME = r"C:\Users\jacks\OneDrive\Desktop\Digital-DNA\engine\genome.json"

try:
    g = json.load(open(GENOME))
except:
    g = {"A":0.5,"B":0.5,"W":1.0,"mode_a":"sin","mode_b":"cos","mode_c":"sin"}

A,B,W = g["A"],g["B"],g["W"]
mode_a = g["mode_a"]
mode_b = g["mode_b"]
mode_c = g["mode_c"]

def f(mode,r):
    if mode=="sin": return math.sin(r)
    if mode=="cos": return math.cos(r)
    if mode=="sin2": return math.sin(r*r)
    if mode=="mix": return math.sin(r)+0.25*math.cos(r)
    return math.sin(r)

r = random.random()*3

score = (
    f(mode_a,r)*A +
    f(mode_b,r)*B +
    f(mode_c,r)*W
)

score = abs(score)

print("STABILITY:",score)
