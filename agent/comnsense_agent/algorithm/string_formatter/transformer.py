"""

This is a simple example of string transformer
that you can teach by one example.

>>> transformer = StringTransformer()
>>> transformer.train_by_example('Joel, 1949, piano', '{name: \'Joel\', instrument: \'piano\'}')  # noqa
>>> print transformer.transform('Lennon, 1940, guitar')
{name: 'Lennon', instrument: 'guitar'}

"""

import re
from itertools import izip


# We disassemble strings into 'groups' of letters/numbers
def get_groups(string):
    return [x for x, y, z in re.findall(r'((\d+)|([a-zA-Z]+))', string)]

# Assume the groups of the output examples are
#   'transformations' of input groups
# Some transformations


def transform_equality(before):
    return before


def transform_upper_case(before):
    return before.upper()


def transform_lower_case(before):
    return before.lower()


def transform_reverse_string(before):
    return before[::-1]

# Rank transformations by what we can be more sure in

transformations = [
    transform_equality,
    transform_upper_case,
    transform_lower_case,
    transform_reverse_string,
]


class StringTransformer(object):
    """
    >>> transformer = StringTransformer()
    >>> transformer.train_by_example('2015-12-07T09:15:17-05:00AA', '07/12/2015 at 09h15aa')  # noqa
    >>> transformer.transform('1998-11-05T08:15:21-05:00BB')
    '05/11/1998 at 08h15bb'
    """
    def __init__(self):
        # We store the transformation method we learned
        self.transform_from_pairs = None
        self.template_after = None

    def train_by_example(self, before, after):
        # Let us identify groups of numeric or alphabetic characters
        groups_before = get_groups(before)
        groups_after = get_groups(after)

        # Save this example for simplicity
        self.groups_before = groups_before
        self.groups_after = groups_after

        # We need to be able to assemble an instance of 'after' from this list
        # Substitute groups with placeholders

        if '%s' in after:
            raise ValueError('We cannot work with strings that contain \'%s\'')

        template_after = after
        for group in groups_after:
            template_after = template_after.replace(group, "%s", 1)
        self.template_after = template_after

        # For every after group we find from what
        #   transformation and index it comes from

        transform_from_pairs = [None] * len(groups_after)

        for t in transformations:
            for after_group_idx, after_group in enumerate(groups_after):
                # Do we already have a source for this group?
                if transform_from_pairs[after_group_idx] is not None:
                    continue
                groups_before_transformed = [t(g) for g in groups_before]
                if after_group in groups_before_transformed:
                    # In how many places the after_group could be found?
                    indexes = [i for i, g in enumerate(groups_before_transformed)  # noqa
                               if g == after_group]
                    if len(indexes) > 1:
                        # Can't figure out where exactly the group comes from
                        pass
                    else:
                        index_before, = indexes
                        transform_from_pairs[after_group_idx] = (t, index_before)  # noqa

        self.transform_from_pairs = transform_from_pairs

    def transform(self, before_new):
        groups_before_new = get_groups(before_new)
        if len(groups_before_new) != len(self.groups_before):
            raise ValueError('New string differs from an example in pattern')

        # By default we take the known example as a transformation
        groups_after_new = self.groups_after
        # Then we use the known transformations
        for idx, t_from_idx in enumerate(self.transform_from_pairs):
            if t_from_idx is not None:
                t, from_idx = t_from_idx
                groups_after_new[idx] = t(groups_before_new[from_idx])

        return self.template_after % tuple(groups_after_new)
