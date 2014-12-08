#
# In-degree Distribution of Largest SCC of the Wikipedia Network. G(1028864, 35699906). 110509 (0.1074) nodes with in-deg > avg deg (69.4), 45061 (0.0438) with >2*avg.deg (Sun Dec  7 23:24:46 2014)
#

set title "In-degree Distribution of Largest SCC of the Wikipedia Network. G(1028864, 35699906). 110509 (0.1074) nodes with in-deg > avg deg (69.4), 45061 (0.0438) with >2*avg.deg"
set key bottom right
set logscale xy 10
set format x "10^{%L}"
set mxtics 10
set format y "10^{%L}"
set mytics 10
set grid
set xlabel "In-degree"
set ylabel "Count"
set tics scale 2
set terminal png size 1000,800
set output 'inDeg.wiki-maxscc.png'
plot 	"inDeg.wiki-maxscc.tab" using 1:2 title "" with linespoints pt 6
