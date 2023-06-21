#!/usr/bin/env python3

import sys
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np

date1 = '2021-07-01'
date2 = '2022-06-01'

# labels = ['Secure 1K', 'Secure 10K', 'Secure 100K', '__Host- 1K', '__Host- 10K', '__Host- 100K', 'Nameless 1K', 'Nameless 10K', 'Nameless 100K']
labels = ['1K', '10K', '100K', '1K', '10K', '100K', '1K', '10K', '100K']
data_21 = [round(x, 2) for x in [
    # secure
    (558*100)/751,
    (3953*100)/6172,
    (33151*100)/59198,

    # host
    (7*100)/751,
    (11*100)/6172,
    (59*100)/59198,

    # nameless
    (1*100)/751,
    (6*100)/6172,
    (88*100)/59198
]]
data_22 = [round(x, 2) for x in [
    # secure
    (537*100)/732,
    (4005*100)/5952,
    (35098*100)/58068,

    # host
    (6*100)/732,
    (14*100)/5952,
    (113*100)/58068,

    # nameless
    (1*100)/732,
    (6*100)/5952,
    (86*100)/58068,
]]

x = np.arange(len(labels))  # the label locations

width = 0.40  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2 - 0.03, data_21, width, label=date1, color=(0.729, 0.929, 0.949), edgecolor='black',hatch='....')
rects2 = ax.bar(x + width/2 + 0.03, data_22, width, label=date2, color=(0.192, 0.627, 0.847), edgecolor='black', hatch='////')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_xlabel('')
ax.set_ylabel('')
ax.set_xticks(x, labels)
ax.set_xticklabels(labels, rotation=0, ha='center')

ax.set_yscale('log')
plt.ylim(-2, 250)
ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f%%'))
ax.legend()

ax.bar_label(rects1, padding=3, rotation=90, fontsize=10)
ax.bar_label(rects2, padding=3, rotation=90, fontsize=10)

fig.tight_layout()

plt.show()