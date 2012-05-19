#!/usr/bin/ksh
# calculates bounding box for pdftotext, ommitting any headers/footers.

bindir=$(realpath ${0%%/*})
pdf=$(realpath $1)
dir=$(basename ${1%%.pdf})
mkdir -p "$dir"
cd "$dir"
i=1
while true; do
    python ${bindir}/split.py "$pdf" $i $i.pdf || break
    convert -monochrome -transparent white $i.pdf $i.png
    print "processing page $i"
    [[ ! -f $i.png ]] && break
    dim=$(file $i.png 2>/dev/null | cut -d, -f2 | tr -d ' ')
    [[ -r ${dim}.png ]] &&
        convert ${dim}.png $i.png -flatten -define png:bit-depth=8 ${dim%%.files}.png ||
        #else
        convert $i.png -flatten -define png:bit-depth=8 ${dim%%.files}.png
    rm $i.pdf
    i=$((i+1))
done
for dim in *x*.png; do
    ${bindir}/bbox.py ${dim} && mv out.png ${dim%%.png}_bbox.png
done
feh *x*_bbox.png
cd -
