### 如何安装字体

1. bdftopcf xx.bdf > xx.pcf
2. gzip xx.pcf
3. sudo cp xx.pcf /usr/share/fonts/X11/misc
4. cd /usr/share/fonts/X11/misc
5. sudo mkfontdir
6. xset fp rehash
7. xfd -fn -xx

