import numpy as np

# Fileprivate
def _clean_vgrps(me):
    vgrps = me.vertex_groups
    for _ in range(len(vgrps)):
        vgrps.remove(vgrps[0])

# Import functions
def extract_weight(me):
    verts = me.data.vertices
    vgrps = me.vertex_groups

    weight = np.zeros((len(verts), len(vgrps)))
    mask = np.zeros(weight.shape, dtype=int)
    vgrp_label = vgrps.keys()

    for i, vert in enumerate(verts):
        for g in vert.groups:
            j = g.group
            weight[i, j] = g.weight
            mask[i, j] = 1

    return weight, vgrp_label, mask

def load_weight(me, label, weight):
    _clean_vgrps(me)
    verts = me.data.vertices
    vgrps = me.vertex_groups

    for name in label:
        vgrps.new(name=name)

    for j in range(weight.shape[1]):
        idx = vgrps.find(label[j])
        if idx == -1:
            continue
        for i in range(weight.shape[0]):
            vgrps[idx].add([i], weight[i, j], 'REPLACE')
