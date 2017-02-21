#-*- coding:utf8 -*-
from PIL import Image
im = Image.open("captcha.gif")
#(将图片转换为8位像素模式)
im = im.convert("L")
#打印颜色直方图
#print (im.histogram())
'''颜色直方图的每一位数字都代表了在图片中含有对应位的颜色的像素的数量。
每个像素点可表现256种颜色，你会发现白点是最多（白色序号255的位置，也就是
最后一位，可以看到，有625个白色像素）。红像素在序号200左右，我们可以通过
排序，得到有用的颜色。'''

his = im.histogram()
values = {}
for i in range(256):
    values[i] = his[i]
for j,k in sorted(values.items(),key=lambda x:x[1],reverse = True)[:10]:
    print (j,k)
'''我们得到了图片中最多的10种颜色，其中 220 与 227 才是我们需要的红色和灰
色，可以通过这一讯息构造一种黑白二值图片。'''


im = Image.open("captcha.gif")
im = im.convert("L")
im2 = Image.new("L",im.size,255)


for x in range(im.size[1]):
    for y in range(im.size[0]):
        pix = im.getpixel((y,x))
        if pix == 220 or pix == 227: # these are the numbers to get
            im2.putpixel((y,x),0)

#im2.show()


'''提取单个字符图片
接下来的工作是要得到单个字符的像素集合，由于例子比较简单，我们对其进行纵向切割：'''
inletter = False
foundletter=False
start = 0
end = 0

letters = []

for y in range(im2.size[0]):
    for x in range(im2.size[1]):
        pix = im2.getpixel((y,x))
        if pix != 255:
            inletter = True
    if foundletter == False and inletter == True:
        foundletter = True
        start = y

    if foundletter == True and inletter == False:
        foundletter = False
        end = y
        letters.append((start,end))

    inletter=False

'''对图片进行切割，得到每个字符所在的那部分图片。'''
import hashlib
import time

count = 0
for letter in letters:
    m = hashlib.md5()
    im3 = im2.crop(( letter[0] , 0, letter[1],im2.size[1] ))
    m.update("%s%s"%(time.time(),count))
    im3.save("./%s.gif"%(m.hexdigest()))
    count += 1



'''使用向量空间搜索引擎来做字符识别，它具有很多优点：
不需要大量的训练迭代
不会训练过度
你可以随时加入／移除错误的数据查看效果
很容易理解和编写成代码
提供分级结果，你可以查看最接近的多个匹配
对于无法识别的东西只要加入到搜索引擎中，马上就能识别了。
缺点:例如分类的速度比神经网络慢很多，它不能找到自己的方法解决问题等等。'''
###用 Python 类实现向量空间：
import math

class VectorCompare:
    #计算矢量大小
    def magnitude(self,concordance):
        total = 0
        for word,count in concordance.iteritems():
            total += count ** 2
        return math.sqrt(total)

    #计算矢量之间的 cos 值
    def relation(self,concordance1, concordance2):
        relevance = 0
        topvalue = 0
        for word, count in concordance1.iteritems():
            if concordance2.has_key(word):
                topvalue += count * concordance2[word]
        return topvalue / (self.magnitude(concordance1) * self.magnitude(concordance2))



#将图片转换为矢量
def buildvector(im):
    d1 = {}
    count = 0
    for i in im.getdata():
        d1[count] = i
        count += 1
    return d1

v = VectorCompare()

iconset = ['0','1','2','3','4','5','6','7','8','9','0','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

#加载训练集
import  os
imageset = []
for letter in iconset:
    for img in os.listdir('./iconset/%s/'%(letter)):
        temp = []
        if img != "Thumbs.db" and img != ".DS_Store":
            temp.append(buildvector(Image.open("./iconset/%s/%s"%(letter,img))))
        imageset.append({letter:temp})


count = 0
#对验证码图片进行切割
for letter in letters:
    m = hashlib.md5()
    im3 = im2.crop(( letter[0] , 0, letter[1],im2.size[1] ))

    guess = []

    #将切割得到的验证码小片段与每个训练片段进行比较
    for image in imageset:
        for x,y in image.iteritems():
            if len(y) != 0:
                guess.append( ( v.relation(y[0],buildvector(im3)),x) )

    guess.sort(reverse=True)
    print ("",guess[0])
    count += 1