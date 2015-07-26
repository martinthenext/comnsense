# coding=utf-8
import pytest
import string
import random

RUSSIAN_LETTERS = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
LETTERS_UPPERCASE = string.ascii_uppercase + RUSSIAN_LETTERS.upper()
LETTERS_LOWERCASE = string.ascii_lowercase + RUSSIAN_LETTERS
LETTERS = LETTERS_UPPERCASE + LETTERS_LOWERCASE


@pytest.yield_fixture
def random_word(min_length=10, max_length=100):
    length = random.randint(min_length, max_length)
    yield u"".join([random.choice(LETTERS) for _ in range(length)])


@pytest.yield_fixture
def random_lower_word(min_length=10, max_length=100):
    length = random.randint(min_length, max_length)
    yield u"".join([random.choice(LETTERS_LOWERCASE) for _ in range(length)])


@pytest.yield_fixture
def random_upper_word(min_length=10, max_length=100):
    length = random.randint(min_length, max_length)
    yield u"".join([random.choice(LETTERS_UPPERCASE) for _ in range(length)])


@pytest.yield_fixture
def random_title_word(min_length=10, max_length=100):
    yield next(random_lower_word(min_length, max_length)).title()


@pytest.yield_fixture
def random_string(min_count=1, max_count=10,
                  word_min_length=10, word_max_length=100):
    count = random.randint(min_count, max_count)
    words = [next(random_word(word_min_length, word_max_length))
             for _ in range(count)]
    yield u" ".join(words)


@pytest.yield_fixture
def random_lower_string(min_count=1, max_count=10,
                        word_min_length=10, word_max_length=100):
    count = random.randint(min_count, max_count)
    words = [next(random_lower_word(word_min_length, word_max_length))
             for _ in range(count)]
    yield u" ".join(words)


@pytest.yield_fixture
def random_upper_string(min_count=1, max_count=10,
                        word_min_length=10, word_max_length=100):
    count = random.randint(min_count, max_count)
    words = [next(random_upper_word(word_min_length, word_max_length))
             for _ in range(count)]
    yield u" ".join(words)


@pytest.yield_fixture
def random_title_string(min_count=1, max_count=10,
                        word_min_length=10, word_max_length=100):
    count = random.randint(min_count, max_count)
    words = [next(random_title_word(word_min_length, word_max_length))
             for _ in range(count)]
    yield u" ".join(words)


@pytest.yield_fixture
def random_first_last_name():
    yield next(random_title_string(2, 2, 5, 20))


@pytest.yield_fixture
def random_address():
    zip_code = random.randint(10000, 999999)
    city = next(random_title_word())
    street = next(random_title_string(1, 2))
    house = random.randint(1, 100)
    letter = next(random_lower_word(1, 1))
    yield u"%d, %d%s, %s, %s" % (zip_code, house, letter, street, city)


@pytest.yield_fixture
def random_number(min_count=3, max_count=9):
    count = random.randint(min_count, max_count)
    min_value = 10 ** count
    max_value = (10 ** (count + 1)) - 1
    yield str(random.randint(min_value, max_value))
