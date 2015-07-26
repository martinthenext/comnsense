import re
from collections import defaultdict

# TODO: some features, like frequency, require all the rows
#        therefore this needs to accept the whole table


class ColumnAnalyzer(object):
    ''' extract patterns from a column
    '''

    N_LEVELS = 4

    def __init__(self, column, level=0):
        # for italian maybe include \' to re_words
        self.re_word = re.compile(r'[^\d\s\.\,\-\_\/]+', re.U)
        self.re_number = re.compile(r'\d+', re.U)
        self.re_white = re.compile(r'\s+', re.U)
        # TODO ask Dmitry about it
        self.re_punctuation = re.compile(r'[\.\,\-\_\/]+', re.U)

        self.patterns_dict = defaultdict(int)
        for value in column:
            pattern = self.get_pattern(value, level)
            self.patterns_dict[pattern] += 1

    def get_pattern(self, value, level=0):
        if level == 0:
            if len(value.strip()) > 0:
                return 'non-empty'
            else:
                return 'empty'
        elif level == 1:
            has_words = len(self.re_word.findall(value)) > 0
            has_numbers = len(self.re_number.findall(value)) > 0
            if has_words and has_numbers:
                return 'both words and numbers'
            elif has_words:
                return 'words, no numbers'
            elif has_numbers:
                return 'numbers, no words'
        elif level == 2:
            value = self.re_word.sub('w', value)
            value = self.re_number.sub('0', value)
            return '%d words %d numbers' % (
                        len(re.findall('w', value)),
                        len(re.findall('0', value)))
        elif level == 3:
            value = self.re_word.sub('w', value)
            value = self.re_number.sub('0', value)
            value = self.re_white.sub(' ', value)
            value = self.re_punctuation.sub('.', value)
            return value

    def get_rows_with_pattern(self, column, level, pattern):
        checker = (lambda v: self.get_pattern(v, level) == pattern)
        return map(checker, column)
