"""Unit tests for whole project are placed here"""

import unittest
import requests

import main as m

from unittest.mock import patch, MagicMock
from main import round_and_adds

class MainTestCase(unittest.TestCase):
    """Class for testing functions of main.py"""

    def setUp(self):
        return super().setUp()

    @patch("tkinter.messagebox.showinfo")
    @patch("requests.post")
    def test_create_table_success(self, mock_response, mock_showinfo):
        app = m.Application()

        mock_response.return_value.status_code = 200
        mock_response.return_value.text = "Table test created"

        wnt = m.WindowNewTable(app)
        wnt.entry = MagicMock()
        wnt.entry.get.return_value = "test"
        wnt.create_table()

        mock_showinfo.assert_called_once_with(message="Table test created")

        app.destroy()
    
    @patch("tkinter.messagebox.showerror")
    @patch("requests.post")
    def test_create_table_fail(self, mock_response, mock_showerror):
        app = m.Application()

        mock_response.return_value.status_code = 1
        mock_response.return_value.text = f"Error code {mock_response.return_value.status_code}, round not created"

        wnt = m.WindowNewTable(app)
        wnt.entry = MagicMock()
        wnt.entry.get.return_value = "test"
        wnt.create_table()

        mock_showerror.assert_called_once()

        app.destroy()
    
    @patch("tkinter.messagebox.showinfo")
    @patch("requests.post")
    def test_insert_address_success(self, mock_response, mock_showinfo):
        app = m.Application()

        wia = m.WindowInsertAddress(app)
        wia.roundchosen = MagicMock()
        wia.entry_street = MagicMock()
        wia.entry_postcode = MagicMock()

        wia.roundchosen.get.return_value = "A01"
        wia.entry_street.get.return_value = "1 House St"
        wia.entry_postcode.get.return_value = "A01 1BC"

        output = (f"Inserted values ({wia.entry_street.get.return_value}, "
        f"{wia.entry_postcode.get.return_value}) into "
        f"{wia.roundchosen.get.return_value}")

        mock_response.return_value.status_code = 200
        mock_response.return_value.text = output

        wia.insert_address()

        mock_showinfo.assert_called_once_with(message=mock_response.return_value.text)

        app.destroy()
    
    @patch("tkinter.messagebox.showerror")
    @patch("requests.post")
    def test_insert_address_fail(self, mock_response, mock_showerror):
        app = m.Application()

        wia = m.WindowInsertAddress(app)
        wia.roundchosen = MagicMock()
        wia.entry_street = MagicMock()
        wia.entry_postcode = MagicMock()

        wia.roundchosen.get.return_value = "A01"
        wia.entry_street.get.return_value = "1 House St"
        wia.entry_postcode.get.return_value = "A01 1BC"

        mock_response.return_value.status_code = 1
        mock_response.return_value.text = f"Error code {mock_response.return_value.status_code}, address not inserted"

        wia.insert_address()

        mock_showerror.assert_called_once()

        app.destroy()
    
    @patch("main.round_and_adds", {"A01": [("1 House St", "A01 XXX")]})
    @patch("tkinter.messagebox.showinfo")
    @patch("tkinter.messagebox.askyesno", return_value=True)
    @patch("requests.post")
    def test_delete_address_success(self, mock_response, mock_yesno, mock_showinfo):
        app = m.Application()

        wda = m.WindowDeleteAddress(app)
        wda.roundchosen = MagicMock()
        wda.addchosen = MagicMock()

        wda.roundchosen.get.return_value = "A01"
        wda.addchosen.get.return_value = ("1 House St", "A01 XXX")

        output = (f"Deleted values ({wda.addchosen.get.return_value}) from "
                  f"{wda.roundchosen.get.return_value}")

        mock_response.return_value.status_code = 200
        mock_response.return_value.text = output

        wda.delete_address()

        mock_yesno.assert_called_once()
        mock_showinfo.assert_called_once_with(message=mock_response.return_value.text)

        app.destroy()
    
    @patch("main.round_and_adds", {"A01": [("1 House St", "A01 XXX")]})
    @patch("tkinter.messagebox.showerror")
    @patch("tkinter.messagebox.askyesno", return_value=True)
    @patch("requests.post")
    def test_delete_address_fail(self, mock_response, mock_yesno, mock_showerror):
        app = m.Application()

        wda = m.WindowDeleteAddress(app)
        wda.roundchosen = MagicMock()
        wda.addchosen = MagicMock()

        wda.roundchosen.get.return_value = "A01"
        wda.addchosen.get.return_value = ("1 House St", "A01 XXX")

        mock_response.return_value.status_code = 1

        wda.delete_address()

        mock_yesno.assert_called_once()
        mock_showerror.assert_called_once()

    def tearDown(self):
        return super().tearDown()

if __name__ == "__main__":
    unittest.main()
