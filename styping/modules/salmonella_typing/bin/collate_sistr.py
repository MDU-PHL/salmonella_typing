#!/usr/bin/env python3
import pandas,sys

sistrs = []
for i in sys.argv[2:]:
    l = i.strip('[,]')
    # print(l)
    sistrs.append(l)

combined_tab = pandas.concat(
    [pandas.read_csv(f, engine='python', sep=None) for f in sistrs])
combined_tab.to_csv('sistr.csv', index=False)