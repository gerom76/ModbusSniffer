"""Test common."""
# from unittest.mock import Mock, patch
from collections import OrderedDict

import pytest

# @pytest.mark.parametrize("data", [(b"", {}), (b"abcd", {"fcode": 98, "unit": 97})])
def test_dictionary():  # pylint: disable=redefined-outer-name
    """Test dictionary."""
    sut = OrderedDict([("A", 1), ("B", 2), ("C", 3)])
    dict2 = OrderedDict([("A", 3), ("C", -1)])
    dict3 = OrderedDict([("D", 7), ("E", 5)])
    dict4 = OrderedDict([("A", 4), ("E", 5)])
    sut.update(dict2)
    sut.update(dict3)
    sut.update(dict4)
    assert sut["A"] == 4
    assert sut["E"] == 5
