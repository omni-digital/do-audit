# -*- coding: utf-8 -*-
"""
do-audit py.test config
"""
from __future__ import unicode_literals

import pytest


@pytest.fixture
def vcr_config():
    """
    Custom vcr.py config
    """
    return {
        'filter_headers': ['authorization'],
        'decode_compressed_response': True,
    }


@pytest.fixture
def vcr_cassette_name(request):
    """
    Override pytest-vcr `vcr_cassette_name` fixture and use one cassete per test class
    """
    f = request.function

    if hasattr(f, '__self__'):
        return f.__self__.__class__.__name__

    return request.node.name
