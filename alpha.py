from datetime import datetime
import csv
from collections import namedtuple
from collections import defaultdict
import copy


class AlphaGroup(object):

    def __init__(self, runs=None):
        self.runs = runs or []

    def add(self, run):
        self.runs.append(run)

    @property
    def size(self):
        return len(self.runs)

    def means(self):
        means = defaultdict(list)
        for run in self.runs[:-1]:
            for row in run.means_adjusted_rows:
                means[row.freq].append(row.cap)
        return {x: sum(y)/float(len(y)) for x, y in means.iteritems()}


class AlphaRun(object):

    def __init__(self, media_cutoff_time=datetime.now(), media_means_adjustment=None):
        self.media_means_adjustment = media_means_adjustment
        self.media_cutoff_time = media_cutoff_time
        self._rows = []

    def add(self, row):
        self._rows.append(row)

    @property
    def means_adjusted_rows(self):
        if self.media_means_adjustment and not self.is_media:
            for row in self.rows:
                if self.media_means_adjustment and not self.is_media:
                    subtract_value = self.media_means_adjustment.get(row.freq, 0)
                    adjusted_capacitance = row.cap - subtract_value
                    yield row._replace(cap=adjusted_capacitance)
        else:
            for row in self.rows:
                yield row

    @property
    def rows(self):
        return self._rows

    @property
    def start_datetime(self):

        return min([x.time for x in self.rows])

    @property
    def is_media(self):
        return self.start_datetime < self.media_cutoff_time


class AlphaExperiment(object):

    lower_frequency_bound = 0.22

    def __init__(self, filepath, media_end_time='00:00:00', grouping=1, strict_grouping=False):
        
        if isinstance(filepath, basestring):
            self.csv_reader = csv.reader(open(filepath, 'r'), skipinitialspace=True)
        else:
            self.csv_reader = csv.reader(filepath, skipinitialspace=True)

        self._media_end_datetime = None
        self._str_media_end_time = media_end_time
        self._exp_datetime = None

        self.meta = self.next_not_empty(self.csv_reader).next()

        self.headers_raw = self.next_not_empty(self.csv_reader).next()
        self._headers = None

        self.row_tuple = namedtuple('Row', self.headers)

        self.grouping = grouping
        self.strict_grouping = strict_grouping
        self._groups = []

        self._runs = []

    @classmethod
    def next_not_empty(cls, iterator):
        while True:
            try:
                row = iterator.next()
                if row:
                    yield row
            except StopIteration as ex:
                break

    def absolute_time(self, time_string):
        return datetime.combine(self.exp_date, datetime.strptime(time_string, '%H:%M:%S').time())

    def parse_row(self, row):
        return self.row_tuple(self.absolute_time(row[0]), float(row[1]), float(row[2]), float(row[3]))

    @property
    def headers(self):
        if not self._headers:
            self._headers = [x.lower().strip() for x in self.headers_raw]
        return self._headers

    @property
    def media_end_datetime(self):
        if not self._media_end_datetime:
            self._media_end_datetime = datetime.combine(self.exp_date, datetime.strptime(self._str_media_end_time, '%H:%M:%S').time())
        return self._media_end_datetime

    @property
    def exp_datetime(self):
        if not self._exp_datetime:
            self._exp_datetime = datetime.strptime(','.join(self.meta), 'Start Time %H:%M:%S   %b %d,%Y')
        return self._exp_datetime

    @property
    def exp_date(self):
        return self.exp_datetime.date()

    @property
    def exp_time(self):
        return self.exp_datetime.time()

    @property
    def groups(self):
        if not self._runs:
            self.parse()
        return self.itergroups()

    @property
    def runs(self):
        if not self._runs:
            self.parse()
        return self._runs

    @property
    def media_runs(self):
        return [run for run in self.runs if run and run.is_media]

    @property
    def media_group(self):
        return AlphaGroup(self.media_runs)

    @property
    def media_means(self):
        return self.media_group.means()

    @property
    def data_runs(self):
        return [run for run in self.runs if run and not run.is_media]

    @property
    def means(self):
        for group in self.groups:
            yield group.means()

    def itergroups(self):
        # if self.strict_grouping an exception will be thrown if num groups is not evenly divisible by group_size
        if hasattr(self.grouping, '__iter__'):
            for group in self.grouping:
                alpha_group = AlphaGroup()
                for index in group:
                    alpha_group.add(self.data_runs[index])
                yield alpha_group
        elif isinstance(self.grouping, int):
            if self.strict_grouping and len(self.data_runs) % self.grouping:
                raise Exception('{} runs cant be evenly grouped into groups of {}'.format(len(self.data_runs), self.grouping))
            for i in range(0, len(self.data_runs), self.grouping):
                yield AlphaGroup(self.data_runs[i:i + self.grouping])
        else:
            raise Exception('Grouping must be of type int or iterable')

    def parse(self):
        current_run = None
        for row in map(self.parse_row, self.next_not_empty(self.csv_reader)):
            if float(row[1]) <= self.lower_frequency_bound:
                if current_run:
                    self._runs.append(copy.deepcopy(current_run))
                current_run = AlphaRun(media_cutoff_time=self.media_end_datetime, media_means_adjustment=self.media_means)
            current_run.add(row)
        self._runs.append(copy.deepcopy(current_run))


if __name__ == '__main__':
    a = AlphaExperiment('/home/brendan/PycharmProjects/alpha_dispersion/alfa 31.3.2017.txt',
                        media_end_time='11:40:54',
                        grouping=[(1, 2, 3), (4, 5), (6, 7, 8, 9), (15, 14, 13)],
                        strict_grouping=True)
    print a.media_means

