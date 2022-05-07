import taichi as ti

from differentiation import (
    sample,
    diff_x,
    diff_y,
    fdiff_x,
    fdiff_y,
    bdiff_x,
    bdiff_y,
    diff2_x,
    diff2_y,
    diff3_x,
    diff3_y,
)


@ti.func
def advect(vc, phi, i, j):
    """Central Differencing"""
    return vc[i, j].x * diff_x(phi, i, j) + vc[i, j].y * diff_y(phi, i, j)


@ti.func
def advect_upwind(vc, phi, i, j):
    """Upwind differencing

    http://www.slis.tsukuba.ac.jp/~fujisawa.makoto.fu/cgi-bin/wiki/index.php?%B0%DC%CE%AE%CB%A1#tac8e468
    """
    k = i if vc[i, j].x < 0.0 else i - 1
    a = vc[i, j].x * fdiff_x(phi, k, j)

    k = j if vc[i, j].y < 0.0 else j - 1
    b = vc[i, j].y * fdiff_y(phi, i, k)

    return a + b


@ti.func
def advect_kk_scheme(vc, phi, i, j):
    """Kawamura-Kuwabara Scheme

    http://www.slis.tsukuba.ac.jp/~fujisawa.makoto.fu/cgi-bin/wiki/index.php?%B0%DC%CE%AE%CB%A1#y2dbc484
    """
    coef = [-2, 10, -9, 2, -1]
    v = ti.Vector([0.0, 0.0, 0.0, 0.0, 0.0])

    if vc[i, j].x < 0:
        v = ti.Vector(coef)
    else:
        v = -ti.Vector(coef[::-1])

    mx = ti.Matrix.cols(
        [
            sample(phi, i + 2, j),
            sample(phi, i + 1, j),
            sample(phi, i, j),
            sample(phi, i - 1, j),
            sample(phi, i - 2, j),
        ]
    )
    a = mx @ v / 6

    if vc[i, j].y < 0:
        v = ti.Vector(coef)
    else:
        v = -ti.Vector(coef[::-1])

    my = ti.Matrix.cols(
        [
            sample(phi, i, j + 2),
            sample(phi, i, j + 1),
            sample(phi, i, j),
            sample(phi, i, j - 1),
            sample(phi, i, j - 2),
        ]
    )
    b = my @ v / 6

    return vc[i, j].x * a + vc[i, j].y * b
