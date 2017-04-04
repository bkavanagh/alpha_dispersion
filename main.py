from alpha import AlphaExperiment
from matplotlib import pyplot as plt


a = AlphaExperiment('/home/brendan/PycharmProjects/alpha_dispersion/alfa 31.3.2017.txt',
                    media_end_time='11:40:54',
                    grouping=[(1,2,3), (4,5), (6,7,8,9), (15, 14, 13)],
                    strict_grouping=True)


media_means = a.media_means

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.set_xscale('log')

ms = sorted(media_means)
mc = [media_means.get(x) for x in ms]
ax.plot(list(ms), list(mc))

plt.xlabel('Frequency kHz')
plt.ylabel('Capacitance mF')

for m in a.means:
    s = sorted(m)
    c = [m.get(x) for x in s]
    ax.plot(list(s), list(c))

plt.show()
