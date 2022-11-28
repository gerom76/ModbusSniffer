"""Test common."""
# from unittest.mock import Mock, patch
from collections import OrderedDict

import pytest

# @pytest.mark.parametrize("data", [(b"", {}), (b"abcd", {"fcode": 98, "unit": 97})])
def test_dictionary():  # pylint: disable=redefined-outer-name
    """Test dictionary."""
    sut = OrderedDict([("A", 1), ("B", 2), ("C", 3)])
    dict2 = OrderedDict([("A", 3), ("C", -1)])
    sut.update(dict2)
    assert sut["A"] == 3

