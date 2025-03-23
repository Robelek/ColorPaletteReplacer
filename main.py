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

paletteRGB = None
paletteOKLAB = None

paletteData = []


def gammaToLinear(c):
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)

def cubeRoot(x):
    return x ** (1. / 3)
def rgbToOklab(rgbData):
    rgb = rgbData / 255.0

    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]

    r = gammaToLinear(r)
    g = gammaToLinear(g)
    b = gammaToLinear(b)

    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

    l = cubeRoot(l)
    m = cubeRoot(m)
    s = cubeRoot(s)

    resultOKLAB = np.stack([
        l * +0.2104542553 + m * +0.7936177850 + s * -0.0040720468,
        l * +1.9779984951 + m * -2.4285922050 + s * +0.4505937099,
        l * +0.0259040371 + m * +0.7827717662 + s * -0.8086757660 ], axis=-1
    )

    return resultOKLAB


def oklabDistance(colorData1, colorData2):
    a, b, c = colorData1
    x, y, z = colorData2

    diffSum = (a-x)**2 + (b-y)**2 + (c-z)**2


    return diffSum


def pickImage():
    currentlySelectedImagePath = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")], initialdir=".")
    if currentlySelectedImagePath:
        currentImage = Image.open(currentlySelectedImagePath).convert('RGB')



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
    global paletteRGB
    global paletteOKLAB

    paletteData = []

    paletteRGB = np.array(inputPalette).reshape(-1, 3)
    paletteOKLAB = rgbToOklab(paletteRGB)

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




def replacePalette():
    global inputImage
    global inputImagePath
    global paletteRGB
    global paletteOKLAB

    if inputImage is None or inputPalette is None:
        tk.messagebox.showerror(message="At least one of the inputs wasn't provided")
        return

    originalData = np.array(inputImage)

    #we convert it to be 1dimensional
    reshaped = originalData.reshape(-1, 3)
    imageInOKLAB = rgbToOklab(reshaped)

    #not very fun numpy thingy, that makes it repeat a value
    differences = imageInOKLAB[:, np.newaxis, :] - paletteOKLAB[np.newaxis, :, :]

    distances = np.sum(differences**2, axis=2)
    closest = np.argmin(distances, axis=1)
    finalImageRGB = paletteRGB[closest]


    finalImageData = finalImageRGB.reshape(originalData.shape)
    imageAfterChanges = Image.fromarray(finalImageData)
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

replacePaletteButton = tk.Button(root, text="Replace palette", command=replacePalette, pady=5)
replacePaletteButton.pack(pady=10)

root.mainloop()