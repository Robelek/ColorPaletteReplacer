import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os
import numpy as np

### OKLAB <-> RGB conversions
# converted from: https://gist.github.com/earthbound19/e7fe15fdf8ca3ef814750a61bc75b5ce

inputImage = None
inputImagePath = None

inputPalette = None
inputPalettePath = None

paletteData = []


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
    a, b, c = colorData1
    x, y, z = colorData2

    diffSum = (a-x)**2 + (b-y)**2 + (c-z)**2


    return diffSum


def pickImage():
    currentlySelectedImagePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")], initialdir=".")
    if currentlySelectedImagePath:
        currentImage = Image.open(currentlySelectedImagePath)



        return currentImage, currentlySelectedImagePath

    return None, None

def getInputImage():
    global inputImage
    global inputImagePath
    global imageNameLabelText

    inputImage, inputImagePath = pickImage()
    if inputImagePath is None:
        imageNameLabelText.set("Currently selected image: none")
    else:
        imageNameLabelText.set(f"Currently selected image: {inputImagePath}")

def setPaletteData():
    global inputPalette
    global paletteData

    paletteData = []

    for y in range(paletteData.shape[0]):
        for x in range(paletteData.shape[1]):
            r, g, b = paletteData[y, x]
            palettePixel = r, g, b

            oklabColor = rgbToOklab(palettePixel)

            paletteData.append(
                {
                    "rgb": palettePixel,
                    "oklab": oklabColor
                }
             )

def getPaletteImage():
    global inputPalette
    global inputPalettePath
    global paletteNameLabelText

    inputPalette, inputPalettePath = pickImage()

    if inputPalettePath is None:
        paletteNameLabelText.set("Currently selected palette: none")
    else:
        paletteNameLabelText.set(f"Currently selected palette: {inputPalettePath}")
        setPaletteData()



def getClosestColorFromPalette(color):
    global inputPalette
    global inputPalettePath

    paletteData = np.array(inputPalette)

    closestColor = None
    closestDist = None

    for paletteColorData in paletteData:
            colorOklab = rgbToOklab(color)

            dist = oklabDistance(paletteColorData['oklab'], colorOklab)

            if closestDist is None or dist < closestDist:
                closestColor = paletteColorData['rgb']
                closestDist = dist

    return closestColor
def replacePalette():
    global inputImage
    global inputImagePath


    if inputImage is None or inputPalette is None:
        tk.messagebox.showerror(message="At least one of the inputs wasn't provided")
        return

    originalData = np.array(inputImage)

    for y in range(originalData.shape[0]):
        for x in range(originalData.shape[1]):
            r,g,b = originalData[y, x]
            originalPixel = r, g, b

            originalData[y, x] = getClosestColorFromPalette(originalPixel)

    imageAfterChanges = Image.fromarray(originalData)
    pathToOriginalImageDir = os.path.dirname(inputImagePath)
    originalImageName = os.path.splitext(os.path.basename(inputImagePath))[0]

    paletteImageName = os.path.splitext(os.path.basename(inputPalettePath))[0]

    newImagePath = f"{pathToOriginalImageDir}/{originalImageName}_{paletteImageName}.png"

    imageAfterChanges.save(newImagePath)

    tk.messagebox.showinfo(message=f"Successfully saved new image to: {newImagePath}")


root = tk.Tk()
root.title("Color Palette Replacer")
root.minsize(400, 30)

browseImagesButton = tk.Button(root, text="Pick input image", command=getInputImage, pady=5)
browseImagesButton.pack(pady=10)

imageNameLabelText = tk.StringVar()
imageNameLabelText.set("Currently selected image: none")
imageNameLabel = tk.Label(root, textvariable=imageNameLabelText, pady=10)
imageNameLabel.pack()

browsePalettesButton = tk.Button(root, text="Pick input palette", command=getPaletteImage, pady=5)
browsePalettesButton.pack(pady=10)

paletteNameLabelText = tk.StringVar()
paletteNameLabelText.set("Currently selected palette: none")
paletteNameLabel = tk.Label(root, textvariable=paletteNameLabelText, pady=10)
paletteNameLabel.pack()

browseImagesButton = tk.Button(root, text="Replace palette", command=replacePalette, pady=5)
browseImagesButton.pack(pady=10)

root.mainloop()