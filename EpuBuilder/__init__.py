

import math
from time import time
import os
import re
from PIL import Image
import shutil


# 测试内容懒得删
# BOOK = {
#     "meta":{
#         "title" : 'THIS IS TITLE',
#         "subtitle" : 'THIS IS SUBTITLE',
#         "author" : 'THIS iS AUTHOR',
#         "publisher" : 'THIS IS PUBLISHER',
#         "ID": 'THIS IS ID',
#         "lang": 'zh-CN'},
#     "syno": ["简介略"],
#     "info":{
#         "书名": "马卡龙与不可思议的福林",
#         "又名": "喵卡龙其实是马卡龙的马甲",
#         "译名": "MR.MACARON AND THE UNBELIEVABLE FULIN~",
#         "来源网址": "饼组图书库：https://www.binzutushu.com/",
#         "发布日期": "2077年7月7日",
#         "评分": "5.0",
#         "标签": "R-18  恋爱 冒险  异世界  主角最强",
#         "免责声明": "<br/>该电子书仅供学习交流，禁止非法传播或用于商业用途，请在下载后24小时内删除。感谢你的支持。"
#     },
#     "content":{
#         "THE START OF IT":{
#             "CHAPTER1: GOOD START!":['this is a good start!','as we can see!','%img%92951741%/img%THIS iS IMAGE NOT EXIST'],
#             "CHAPTER2: GODNESS FULIN!":['this is a good Fulin!','as we can see!','THIS IS PNG 1 %img%7f1d9e7580b061f8d28f3f144b7fdd41.png%/img%']

#         },
#         "TIME TO KILL THAT STUPID":{
#             "CHAPTER1: GOOD KILL!":['this is%img%92951741_p0.jpg%/img% a good kill!','as we can%img%90615135_p0.jpg%/img% see!']
#         }
#     }
# }


class EpuBuild():
    def __init__(self, book:dict):
        super(EpuBuild, self).__init__()

        self.template = {
            'mimetype':{
                'src':r'/mimetype',
                'content':''
            },
            'container.xml':{
                'src':r'/META-INF/container.xml',
                'content':''
                },
            'content.opf':{
                'src':r'/OEBPS/content.opf',
                'content':''
            },
            'copyright.xhtml':{
                'src':r'/OEBPS/copyright.xhtml',
                'content':''
            },
            'cover.xhtml':{
                'src':r'/OEBPS/cover.xhtml',
                'content':''
            },
            'intro.xhtml':{
                'src':r'/OEBPS/intro.xhtml',
                'content':''
            },
            'page-template.xpgt':{
                'src':r'/OEBPS/page-template.xpgt',
                'content':''
            },
            'stylesheet.css':{
                'src':r'/OEBPS/stylesheet.css',
                'content':''
            },
            'title_page.xhtml':{
                'src':r'/OEBPS/title_page.xhtml',
                'content':''
            },
            'toc.ncx':{
                'src':r'/OEBPS/toc.ncx',
                'content':''
            },
            'toc.xhtml':{
                'src':r'/OEBPS/toc.xhtml',
                'content':''
            },
        }


        ##meta 元数据
        self.meta = book['meta']

        ##给ID和lang添加默认
        if 'ID' not in  book['meta'].keys():
            self.meta['ID'] = "FULINISTHEGODNESSOFMACARON_" + str(math.ceil(time()))
        if 'lang' not in  book['meta'].keys():
            self.meta['lang'] = 'zh-CN'
        if 'subtitle' not in self.meta.keys():
            self.meta['subtitle'] = ''

        ##简介
        self.syno = book['syno']

        ##基本信息
        self.info = book['info']

        ##本文
        self.content = book['content']

        ##目录
        self.index = {}
        self.chapters = []
        for _series in self.content.keys():
            self.index[_series] = self.content[_series].keys()
            self.chapters.extend(self.content[_series].keys())

        ##image
        self.images = []
        self.imagesrc = ''
        self.cover = r'./templateFiles/default_cover.jpg'
        self.coverSize = ()

        self.chapternum_ForPrint = 0
    def setImagedir(self, src:str=r'./images'):
        self.images = os.listdir(src)
        self.imagesrc = src + r'/'

    def setCover(self, src:str=r'./cover.jpg'):
        self.cover = src

    def booktoTemp(self):
        book = self.template
        book['mimetype']['content'] = self.Prase('mimetype',{})
        book['container.xml']['content'] = self.Prase('container.xml',{})
        book['copyright.xhtml']['content'] = self.Prase('copyright.xhtml',{
            'copyright':self.copyRight()
        })
        book['content.opf']['content'] = self.Prase('content.opf',{
            'title':self.meta['title'],
            'creater':self.meta['author'],
            'publisher':self.meta['publisher'],
            'ID':self.meta['ID'],
            'lang':self.meta['lang'],
            'manifest:chap': self.manifestChap(),
            'spine:chap': self.spineChap(),
            'manifest:img': self.manifestImg(),
        })
        book['cover.xhtml']['content'] = self.Prase('cover.xhtml',{
            'title':self.meta['title'],
        })
        book['intro.xhtml']['content'] = self.Prase('intro.xhtml',{
            'syno' : self.arr2p(self.syno)
        })
        book['page-template.xpgt']['content'] = self.Prase('page-template.xpgt',{})
        book['stylesheet.css']['content'] = self.Prase('stylesheet.css',{})
        book['title_page.xhtml']['content'] = self.Prase('title_page.xhtml',{
            'title':self.meta['title'],
            'author':self.meta['title'],
            'subtitle':self.meta['author'],
            'subtitle':self.meta['subtitle']
        })
        book['toc.xhtml']['content'] = self.Prase('toc.xhtml',{
            'toc' : self.tocXHTML()
        })
        book['toc.ncx']['content'] = self.Prase('toc.ncx',{
            'toc' : self.tocNCX()
        })
        chapnum = 0
        for series in self.index:
            for chap in self.index[series]:
                book['chap' + str(chapnum) + '.xhtml'] = {
                    'src':'',
                    'content':''
                }
                book['chap' + str(chapnum) + '.xhtml']['src'] = '/OEBPS/'+ 'chap' + str(chapnum) + '.xhtml'
                book['chap' + str(chapnum) + '.xhtml']['content'] = self.Prase('chap.xhtml',{
                    'title' : chap,
                    'content': self.arr2p(self.content[series][chap]),
                })
                chapnum += 1
        return book

    def Build(self, src:str=r'./output'):
        print('>> EpuBuilder程序启动！', flush=True)
        book = self.booktoTemp()

        localaddress = r'./output'
        META_Path = localaddress + r'/catch/EPUB/META-INF'
        Image_Path = localaddress + r"/catch/EPUB/OEBPS/images"

        os.makedirs(META_Path,exist_ok = True)
        os.makedirs(Image_Path + r'/cover',exist_ok = True)
        printernum = 1
        ##print('创建XHTML文件中')
        for file in book:
            self.print33_creat(printernum, len(book), book[file]['src'])
            self.creatFile(book[file]['content'], book[file]['src'])
            printernum += 1
        print('\r'.ljust(200), flush=True, end='')
        print('\r>> 文件创建完成 |#################################| 100.0% | - ', flush=True, end='')
        self.creatImg(Image_Path)

        ##print('创建封面预览文件中')
        print('\n\n>> 正在创建封面预览', flush=True)
        coverguide = self.Prase('coverguide.xhtml', {
            'width': str(self.coverSize[0]),
            'height' : str(self.coverSize[1])
        })
        self.creatFile(coverguide, r'/OEBPS/coverguide.xhtml')

        ##print('正在打包EPUB')
        print('>> 正在导出为ePub', flush=True)
        shutil.make_archive(localaddress + r'/output_catch','zip', localaddress + r'/catch/EPUB')
        shutil.move(localaddress + r'/output_catch.zip',src + r'/' + self.meta['title'] + '.epub')
        shutil.rmtree(localaddress + r'/catch/EPUB')
        print('>> ePub制作完成！')

    def creatImg(self, outputdir:str=r'./output/catch/EPUB/OEBPS/images'):
        ##print('正在转换图片')
        for imagename in self.images:
            img = Image.open(self.imagesrc + imagename, mode='r')
            img.save(outputdir + r'/' + self.renameToJpg(imagename), 'jpeg')
        cover = Image.open(self.cover, mode='r')
        cover.save(outputdir + r'/cover/cover.jpg', 'jpeg')

        ##限定封面大小
        (coverwidth,coverheight) = cover.size
        coverratio = min(min(1200/coverwidth,1200/coverheight),1)
        self.coverSize = (math.floor(coverwidth*coverratio),math.floor(coverheight*coverratio))


        _404 = Image.open(r'./templateFiles/error_404.jpg',mode='r')
        _404.save(outputdir + r'/error_404.jpg','jpeg')


    def creatFile(self,txt: str, src: str, outputdir:str=r'./output'):
        try:
            with open( outputdir + r'/catch/EPUB' + src,'w',encoding='utf-8') as F:
                F.write(txt)
        except Exception as e:
            print(e)

    def Prase(self,src:str, object:dict):  #obj模板渲染替换
        _f = ''
        # _object = {};
        with open(r'./templateFiles/' + src, 'r', encoding='utf-8') as f:
            _f = f.read()
            for keys in object.keys():
                _f = _f.replace('{%'+keys+'%}', object[keys])
        return _f


    def copyRight(self):
        text = ''
        for key in self.info.keys():
            text += '<p>'+ key + '：' + self.info[key] +'</p>\n'
        return text


    def manifestChap(self):
        chapnum = 0
        text = ''
        for chap in self.chapters:
            text += '<item id="chapter' + str(chapnum) + '" href="chap' + str(chapnum) +'.xhtml" media-type="application/xhtml+xml"/>'
            chapnum += 1
        return text

    def manifestImg(self):
        text = ''
        for img in self.images:
            text += '<item id="'+ img +'" href="images/'+img+'" media-type="image/jpeg"/>'
        return text

    def spineChap(self):
        chapnum = 0
        text = ''
        for chap in self.chapters:
            text += '<itemref idref="chapter' + str(chapnum) +'"/>'
            chapnum+=1
        return text


    def tocXHTML(self):
        chaplist = self.index
        ##{'s1':[chap1,chap2],'s2':[chap1,chap2]}
        chapnum = 0
        text = ''
        for series in chaplist.keys():
            text += '<h4>' + series + '</h4>\n'
            for chap in chaplist[series]:
                text += '<p><a href="chap'+str(chapnum)+'.xhtml">'+ chap +'</a></p>\n'
                chapnum += 1
        return text

    def tocNCX(self):
        chaplist = self.index
        text = ''
        chapnum = 0
        playOrder = 6
        for series in chaplist.keys():
            text += '''
                    <navPoint id="chapter'''+ str(chapnum)+'''" playOrder="'''+ str(playOrder) +'''">
                        <navLabel>
                            <text>'''+series+'''</text>
                        </navLabel>
                    <content src="chap'''+ str(chapnum) +'''.xhtml"/>
                    '''
            playOrder+=1;
            for chap in chaplist[series]:
                text += '''
                        <navPoint id="chapter'''+ str(chapnum) +'''" playOrder="'''+ str(playOrder) +'''">
                            <navLabel>
                                <text>''' + chap + '''</text>
                            </navLabel>
                        <content src="chap'''+ str(chapnum) +'''.xhtml"/>
                        </navPoint>
                        '''
                playOrder += 1;
                chapnum += 1
            text += '</navPoint>'
        return text

    def renameToJpg(self, filename:str):
        split = filename.split('.')
        filetype = split[-1]
        filename = '.'.join(split[:-1])
        if filename == '':
            return 'error_404.jpg'
        elif not filetype == 'jpg' or not filetype == 'JPG':
            return filename+ '.jpg'
        else:return filename

    def arr2p(self,arr):
        text = ''
        for p in arr:
            text += '<p>' + p + '</p>\n'
        re_images = re.findall(r"(?<=%img%)(.*?)(?=%\/img%)", text)
        for image in re_images:
            if image not in self.images:
                text = text.replace('%img%'+ image +'%/img%', '%img%error_404.jpg%/img%')
            text = text.replace('%img%'+ image +'%/img%', '%img%' + self.renameToJpg(image) + '%/img%')
        text = text.replace('%img%','</p><br/>\n<img alt="image" src="images/').replace('%/img%','" />\n<br/><p>')
        return text

    def print33_creat(self, indexnow, indextotal, title):  # 进度条
        A_count = math.floor(indexnow/indextotal*33)
        A = '#'*A_count
        B = '-'*(33-A_count)
        C = math.floor(indexnow/indextotal*1000)/10
        if 'chap' in title:
            chapname = self.chapters[self.chapternum_ForPrint]
            if len(chapname) > 66:
                chapname = chapname[:66]+'...'
            title = title + ' | ' + chapname
            self.chapternum_ForPrint +=1
        print('\r>> 正在创建 |' + A + B + '| ' + str(C) + '% | ' + title, flush=True, end='')

# B = EpuBuild(BOOK)
# B.setCover('97311980_p0.png')
# # B.setImagedir()
# B.Build('D:/Game')
