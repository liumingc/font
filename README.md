### 文件说明
subfont2bdf.c 用于将plan9port中的lucm字体subfont转成通用的bdf格式。
font.py则是读取font文件，用ascii字符显示图形的工具。

### 如何安装字体

1. bdftopcf xx.bdf > xx.pcf
2. gzip xx.pcf
3. sudo cp xx.pcf /usr/share/fonts/X11/misc
4. cd /usr/share/fonts/X11/misc
5. sudo mkfontdir
6. xset fp rehash
7. xfd -fn -xx

