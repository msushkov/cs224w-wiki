#
# Out-degree Distribution of Largest SCC of the Wikipedia Network. G(1028864, 35699906). 124456 (0.1210) nodes with out-deg > avg deg (69.4), 44911 (0.0437) with >2*avg.deg (Sun Dec  7 23:25:40 2014)
#

set title "Out-degree Distribution of Largest SCC of the Wikipedia Network. G(1028864, 35699906). 124456 (0.1210) nodes with out-deg > avg deg (69.4), 44911 (0.0437) with >2*avg.deg"
set key bottom right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "Out-degree"
set ylabel "Count"
set tics scale 2
set terminal png size 1000,800
set output 'outDeg.wiki-maxscc.png'
plot 	"outDeg.wiki-maxscc.tab" using 1:2 title "" with linespoints pt 6
