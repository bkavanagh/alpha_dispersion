from alpha import AlphaExperiment

a = AlphaExperiment('/home/brendan/PycharmProjects/alpha_dispersion/alfa 31.3.2017.txt',
                    media_end_time='11:40:54',
                    grouping=[(1,2,3), (4,5), (6,7,8,9)],
                    strict_grouping=True)

for g in a.groups:
    print g.means()

print len(a.media_group.runs)