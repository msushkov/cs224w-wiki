#
# Out-degree Distribution of 60k-node Wikipedia subgraph. G(63887, 3250827). 8975 (0.1405) nodes with out-deg > avg deg (101.8), 1598 (0.0250) with >2*avg.deg (Tue Dec  9 19:19:56 2014)
#

set title "Out-degree Distribution of 60k-node Wikipedia subgraph. G(63887, 3250827). 8975 (0.1405) nodes with out-deg > avg deg (101.8), 1598 (0.0250) with >2*avg.deg"
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
set output 'outDeg.wiki_small.png'
plot 	"outDeg.wiki_small.tab" using 1:2 title "" with linespoints pt 6
