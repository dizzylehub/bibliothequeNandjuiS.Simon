"""Textures raccordables (512 px) de la palette K&Démi, jointes à la maquette IFC."""
import sys, os
import numpy as np
from PIL import Image

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
N = 512
rng = np.random.default_rng(11)
y, x = np.mgrid[0:N, 0:N] / N
hexrgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255.0

def periodic_noise(octaves=((4, .5), (8, .3), (16, .2)), seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((N, N))
    for f_, a in octaves:
        for _ in range(6):
            kx, ky = r.integers(1, f_ + 1, 2) * r.choice([-1, 1], 2)
            out += a * np.sin(2 * np.pi * (kx * x + ky * y) + r.uniform(0, 2 * np.pi)) / 6
    return out

def save(name, img):
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(os.path.join(OUT, name))

def plaster(hexc, amp, seed):
    c = hexrgb(hexc)
    n = periodic_noise(seed=seed) * amp + rng.normal(0, amp * .25, (N, N))
    return c[None, None] * (1 + n[..., None])

save("enduit_chaux_blanc.png", plaster("#F3EFE6", .035, 1))
save("enduit_terre_cuite.png", plaster("#B4583E", .06, 2))
save("enduit_chaux_sable.png", plaster("#E6D6BF", .05, 3))
save("acier_noir_mat.png", plaster("#1E1E1E", .10, 4))
save("vegetal.png", plaster("#5E8C4A", .25, 5))

# iroko : fil du bois vertical, raccordable
c = hexrgb("#9A6B43")
g = np.sin(2 * np.pi * (6 * x + 0.15 * np.sin(2 * np.pi * 2 * y) + 0.05 * np.sin(2 * np.pi * 7 * y)))
g2 = np.sin(2 * np.pi * (23 * x + 0.1 * np.sin(2 * np.pi * 3 * y)))
save("iroko_huile.png", c[None, None] * (0.9 + 0.08 * g[..., None] + 0.03 * g2[..., None]))

# grès cérame 60 x 60 : un carreau par tuile de texture, joint clair
img = plaster("#D9CDB8", .03, 6)
img[:3, :] = img[-3:, :] = img[:, :3] = img[:, -3:] = hexrgb("#BDB2A0")
save("gres_cerame_sable.png", img)

# tissu bouclette terre cuite
c = hexrgb("#A9533A")
wv = ((np.floor(x * 64) + np.floor(y * 64)) % 2) * 0.07
save("tissu_terre_cuite.png", c[None, None] * (0.92 + wv[..., None] + rng.normal(0, .02, (N, N, 1))))

# claustra terre cuite : anneaux + pontets sur fond sombre (module 20 cm = une tuile)
fond, terre = hexrgb("#3B2A24"), hexrgb("#B4583E")
u, v = (x % 1) - .5, (y % 1) - .5
rr = np.hypot(u, v)
ring = (rr > .26) & (rr < .37)
bridge = ((np.abs(v) < .06) & (np.abs(u) > .36)) | ((np.abs(u) < .06) & (np.abs(v) > .36))
dot = np.hypot(np.abs(u) - .5, np.abs(v) - .5) < .08
mask = ring | bridge | dot
img = np.where(mask[..., None], terre[None, None], fond[None, None])
save("claustra_terre_cuite.png", img * (1 + 0.04 * periodic_noise(seed=7)[..., None]))

# livres : dos colorés
pal = [hexrgb(h) for h in ("#B4583E", "#C89B5B", "#7F8F6A", "#E9DFC9", "#5B4636", "#9EA7A0", "#D2B48C", "#6E2F25")]
img = np.zeros((N, N, 3)); xpos = 0
while xpos < N:
    w = rng.integers(10, 26)
    img[:, xpos:xpos + w] = pal[rng.integers(len(pal))]
    img[:, xpos:xpos + 1] = .15
    xpos += w
save("livres.png", img)
print("ok", sorted(os.listdir(OUT)))
