import allure
import pytest
from hamcrest import *

from zmq.eventloop import ioloop

from ..fixtures.agent import agent, agent_port, agent_host
from ..fixtures.addin import addin
from ..fixtures.excel import workbook as workbook_id
from ..workbook.workbook import Workbook
from ..workbook.scenario import Scenario


@pytest.yield_fixture
def workbook(workbook_id):
    wb = Workbook(workbook_id, """
         A         |       B      |      C
    ----------------------------------------------
    Account Number | Client Name  | Phone Number
    9283871273     | John Smith	  | 078-922-11-55
    2391293821	   | Lisa Dough	  | 077-828-12-33
    1203912323	   | Phil Downey  | 044-282-28-25
    1231234123	   | Sam Smith    | 033-248-99-22
    1231215135     | George Bush  | 011-238-58-23
    3573675663     | Alex Black	  | 076-296-88-44
    9348949834	   | Tim Cook	  | 044-383-48-23
    2938422342	   | Kate Bishop  | 055-293-23-21
    3064358384	   | Sew Greene   | 028-238-28-95
    9465793845	   | Jake Thomas  | 044-293-68-43
    1293123232	   | George Smith |	038-281-23-28
    2130129312	   | Nick Rudolf  | 054-664-34-97
    1293123823	   | Cris Norris  | 076-384-96-44
    2393123123	   | Colin Stocks | 088-384-34-23
    1231475623	   | Bob Brown    | 086-934-67-54
    4441241624	   | Peter Parker | 054-384-38-39
    2394023234	   | Steven Wood  | 043-483-53-35
    1231238273	   | Laura White  | 023-583-23-23
    9391023192	   | Jane Brown	  | 044-287-73-09
    8484827323	   | Jack Green   | 065-502-28-71
    ==============================================
    Clients
                  """)
    allure.attach("initial", wb.serialize("Clients"))
    yield wb


@pytest.yield_fixture
def expected(workbook_id):
    wb = Workbook(workbook_id, """
         A         |           B         |      C
    -----------------------------------------------------
    Account Number | Client Name         | Phone Number
    9283871273     | John Smith          | 078 922 11 55
    2391293821	   | Lisa Dough	         | 077 828 12 33
    1203912323	   | Phil Downey         | 044 282 28 25
    1231234123	   | Sam Smith           | 033 248 99 22
    1231215135     | George Bush         | 011 238 58 23
    3573675663     | Alex Black	         | 076 296 88 44
    9348949834	   | Tim Cook	         | 044 383 48 23
    2938422342	   | Kate Bishop         | 055 293 23 21
    3064358384	   | Sew Greene          | 028 238 28 95
    9465793845	   | Jake Thomas         | 044 293 68 43
    1293123232	   | George Smith        | 038 281 23 28
    2130129312	   | Nick Rudolf         | 054 664 34 97
    1293123823	   | Cris Norris         | 076 384 96 44
    2393123123	   | Colin Stocks        | 088 384 34 23
    1231475623	   | Bob Brown           | 086 934 67 54
    4441241624	   | Peter Parker        | 054 384 38 39
    2394023234	   | Steven Wood         | 043 483 53 35
    1231238273	   | Laura White         | 023 583 23 23
    9391023192	   | Jane Brown	         | 044 287 73 09
    8484827323	   | Jack Green          | 065 502 28 71
    Dart:color::3  | Dart Vader:color::0 |
    =====================================================
    Clients
                  """)
    allure.attach("expected", wb.serialize("Clients"))
    yield wb


@pytest.yield_fixture
def scenario(workbook):
    sheet = workbook.sheets()[0]
    sc = Scenario(workbook)
    sc.open(comment="open workbook")
    sc.change(sheet, "$C$2", "078 922 11 55", comment="change first number")
    sc.change(sheet, "$C$3", "077 828 12 33", comment="change next number")
    sc.change(sheet, "$A$22", "Dart", comment="add incorrect account")
    sc.change(sheet, "$B$22", "Vader", comment="add incorrect name")
    sc.change(sheet, "$B$22", "Dart Vader", comment="correct name")
    sc.close(comment="close workbook")
    yield sc


@allure.feature("Blackbox")
@allure.story("First Demo Day")
@pytest.mark.parametrize("interval", [pytest.mark.xfail(300),
                                      pytest.mark.xfail(500),
                                      1000])
@pytest.mark.timeout(20)
def test_system_first_demo_day(agent, addin, interval, expected):
    loop = ioloop.IOLoop()
    addin.run(loop, interval)
    with allure.step("compare with expected"):
        for sheet in expected.sheets():
            allure.attach("expected.%s" % sheet,
                          expected.serialize(sheet))
        for sheet in addin.scenario.workbook.sheets():
            allure.attach("actual.%s" % sheet,
                          addin.scenario.workbook.serialize(sheet))
        assert_that(addin.scenario.workbook, equal_to(expected))
