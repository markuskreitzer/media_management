from PIL import Image
from PIL import ImageChops
from PIL import ImageDraw

imageA= Image.open("Original.jpg")
imageB= Image.open("Editted.jpg")

dif = ImageChops.difference(imageB, imageA).getbbox()
draw = ImageDraw.Draw(imageB)
draw.rectangle(dif)
imageB.show()
