import numpy as np
import json
import matplotlib.pyplot as plt
import sys

fname = sys.argv[1] #'example.json'

json_unit = 'weeks'
bar_unit = 'months'
unit_conv = {'working_days':0.2, 'days':1/7.0, 'weeks':1, 'months':4.33, 'years':52}
unit_fac = unit_conv[bar_unit] / unit_conv[json_unit]

with open(fname, 'r') as f: D = json.load(f)

title = list(D.keys())[0]
stages = list(D[title].keys())

def flatten_nested_list(l):
    fl = []
    if not isinstance(l, list): fl.append(l)
    else:
        for li in l: fl.extend(flatten_nested_list(li))
    return fl

def get_TS(d):
    if not isinstance(d, dict): return d[0]
    else: return np.sum([get_TS(d[key]) for key in d.keys()])

def get_TS_list(d):
    if not isinstance(d, dict): return d[0]
    else: return [get_TS_list(d[key]) for key in d.keys()]

def get_ETC(d):
    if not isinstance(d, dict): return d[1]
    else: return np.sum([get_ETC(d[key]) for key in d.keys()])

def get_ETC_list(d):
    if not isinstance(d, dict): return d[1]
    else: return [get_ETC_list(d[key]) for key in d.keys()]

TS = get_TS(D[title])
ETC = get_ETC(D[title])
TS_list = get_TS_list(D[title])
ETC_list = get_ETC_list(D[title])

'''
print(TS, ETC)
print(TS_list)
print(ETC_list)
'''

from matplotlib import rc, rcParams
rc_params = {'axes.labelsize': 12,
             'axes.titlesize': 12,
             'font.size': 12,
             'lines.linewidth' : 3,
             'legend.fontsize': 12,
             'xtick.labelsize': 12,
             'ytick.labelsize': 12,
             'text.usetex' : True,
            }
rcParams.update(rc_params)

rc('text.latex', preamble='\\usepackage{txfonts}')
rc('text', usetex=True)
rc('font', family='serif')
rc('font', serif='times')
rc('mathtext', default='sf')
rc("lines", markeredgewidth=1)
rc("lines", linewidth=2)

colors = {0:'crimson', 0.2:'orange', 0.4:'gold', 0.6:'cyan', 0.8:'dodgerblue', 1.0:'lawngreen'}
txt_colors = {0:'k', 0.2:'k', 0.4:'k', 0.6:'k', 0.8:'k', 1.0:'k'}
def get_status(ts, etc):
    return np.round(ts / etc * 5) / 5.0

plt.figure(figsize=(8,1.6))
plt.plot([0,1],[0,1],alpha=0)
plt.yticks([])
plt.xticks([ETC / unit_fac], ['%.0f %s' % (ETC / unit_fac, bar_unit)])
if 'stuck' in D['Current'].lower(): plt.text(0,-0.03,'Current status: ' + D['Current'], va='top', color='crimson', weight='heavy')
else: plt.text(0,-0.03,'Current status: ' + D['Current'], va='top')
plt.text(0,1.03,title,va='bottom', weight='heavy',fontsize=14)

##### Enter data here #####

ts_lv1 = [np.sum(flatten_nested_list(l)) for l in TS_list]
etc_lv2 = []
for l in ETC_list:
    etc_lv2.extend([np.sum(flatten_nested_list(l1)) for l1 in l])
etc_lv1 = [np.sum(flatten_nested_list(l)) for l in ETC_list]
begs = np.cumsum([0] + etc_lv1) / unit_fac

for i in range(len(etc_lv1)):
    status = get_status(ts_lv1[i], etc_lv1[i])
    beg = begs[i]
    end = begs[i] + ts_lv1[i] / unit_fac
    plt.fill_between([beg, end], [0,0], [1,1], color=colors[status])
    plt.text(0.5 * (begs[i] + begs[i+1]), 0.5, stages[i], color=txt_colors[status], ha='center', va='center')

#plt.vlines(x = np.cumsum([0] + etc_lv2) / unit_fac, ymin=0, ymax=1, color='darkgray', lw=1)
plt.vlines(x = np.cumsum([0] + etc_lv1) / unit_fac, ymin=0, ymax=1, color='k', lw=3)

#####

plt.ylim([0,1])
plt.xlim([0,ETC / unit_fac])
plt.twiny()
plt.xticks([1],['100\%'])
#plt.subplots_adjust(top=0.9, bottom=0.1, hspace=0.)
plt.tight_layout()
plt.savefig('%s.png' % (fname.split('.')[0]))
plt.show()
