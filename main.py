import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

### OKLAB <-> RGB conversions
# converted from: https://gist.github.com/earthbound19/e7fe15fdf8ca3ef814750a61bc75b5ce

def gammaToLinear(c):
    if c > 0.04045:
        return pow((c + 0.055) / 1.055, 2.4)
    else:
        return c / 12.92

def linearToGamma(c):
    if c >= 0.0031308:
        return 1.055 * pow(c, 1 / 2.4) - 0.055
    else:
        12.92 * c

def cubeRoot(x):
    return x ** (1. / 3)
def rgbToOklab(rgbData):
    r, g, b = rgbData

    r = gammaToLinear(r/255.0)
    g = gammaToLinear(g/255.0)
    b = gammaToLinear(b/255.0)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l = cubeRoot(l)
    m = cubeRoot(m)
    s = cubeRoot(s)

    resultOKLAB = (
        l * +0.2104542553 + m * +0.7936177850 + s * -0.0040720468,
        l * +1.9779984951 + m * -2.4285922050 + s * +0.4505937099,
        l * +0.0259040371 + m * +0.7827717662 + s * -0.8086757660
    )

    return resultOKLAB

def oklabToRgb(oklabData):
    L, a, b = oklabData

    l = L + a * +0.3963377774 + b * +0.2158037573
    m = L + a * -0.1055613458 + b * -0.0638541728
    s = L + a * -0.0894841775 + b * -1.2914855480

    l = l**3
    m = m**3
    s = s**3

    r = l * +4.0767416621 + m * -3.3077115913 + s * +0.2309699292
    g = l * -1.2684380046 + m * +2.6097574011 + s * -0.3413193965
    b = l * -1.2684380046 + m * +2.6097574011 + s * -0.3413193965

    r = 255 * linearToGamma(r)
    g = 255 * linearToGamma(g)
    b = 255 * linearToGamma(b)

    r = round(r)
    g = round(g)
    b = round(b)

    return (r,g,b)


def oklabDistance(colorData1, colorData2):
    a, b, c = colorData1['oklab']
    x, y, z = colorData2['oklab']

    diffSum = (a-x)**2 + (b-y)**2 + (c-z)**2


    return diffSum