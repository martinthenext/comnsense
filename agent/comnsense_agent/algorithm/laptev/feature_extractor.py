import numpy as np
import re
from collections import defaultdict

# todo: some features, like frequency, require all the rows
#        therefore this needs to accept the whole table
# todo: column_type can be only 'str'
#        it can be computed automatically if the whole table is known


class feature_extractor(object):
    ''' class for extracting features
    '''

    def __init__(self, row, column_types=[]):
        ''' computes all the features given a row of a table
            here <row> is a list of strings
        '''
        self.row = row

        self.column_types = column_types
        if self.column_types == []:
            self.column_types = ['str']*len(row)

        # features from individual columns
        self.features = np.array([])
        for i in range(len(self.row)):
            if self.column_types[i] == 'str':
                temp = self.features_str(self.row[i])
            self.features = np.hstack((self.features, temp))

        # features from concatenated columns
        if len(self.row) > 1:
            temp = self.features_str('~'.join(self.row))
            self.features = np.hstack((self.features, temp))

    def features_str(self, value):
        ''' extracts features from a general string
        '''
        features = np.zeros(5)
        # length of a string
        features[0] = len(value)
        # number of characters
        features[1] = len(re.findall(r'[a-zA-Z]', value))
        # number of character sequences
        features[2] = len(re.findall(r'[a-zA-Z]+', value))
        # number of digits
        features[3] = len(re.findall(r'\d', value))
        # number of digit sequences
        features[4] = len(re.findall(r'\d+', value))
        return features

    def feature_vector(self, features=[]):
        ''' returns features concatenated to a vector
        '''
        if features == []:
            # return all the features
            return self.features
        else:
            # return listed features
            # todo: need a mapping from feature names to indices
            pass

class column_analyzer(object):
    ''' extract patterns from a column
    '''
    def __init__(self, column, level=0):
        # for italian maybe include \' to re_words
        self.re_word = re.compile(r'[a-zA-Z]+')
        self.re_number = re.compile(r'\d+')
        self.re_white = re.compile(r'\s+')
        self.re_punctuation = re.compile(r'[\.\,\-\_\/]+') # todo

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
            else:
                return 'no words and numbers'
        elif level == 2:
            value = self.re_word.sub('w', value)
            value = self.re_number.sub('0', value)
            return '%d words %d numbers' % (
                        len(re.findall('w', value)),
                        len(re.findall('0', value)) )
        elif level == 3:
            value = self.re_word.sub('w', value)
            value = self.re_number.sub('0', value)
            value = self.re_white.sub(' ', value)
            value = self.re_punctuation.sub('.', value)
            return value

    def get_rows_with_pattern(self, column, level, pattern):
        checker = lambda v: self.get_pattern(v, level) == pattern
        return map(checker, column)
