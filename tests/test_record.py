from mock import patch

from dta.records.record import DTARecord


@patch('dta.records.header.DTAHeader.validate')
def test_validate_header(mocker):
    record = DTARecord()
    assert not mocker.called
    record.validate()
    assert mocker.call

