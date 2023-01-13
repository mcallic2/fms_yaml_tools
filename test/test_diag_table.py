import unittest
import tempfile
import os
import pathlib
from contextlib import contextmanager

from fms_yaml_tools.diag_table.diag_table_to_yaml import Diag
from fms_yaml_tools.diag_table.diag_table_to_yaml import DiagTable
from collections import OrderedDict

EXAMPLE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'examples'))


@contextmanager
def test_directory(path: pathlib.Path):
    """Set the cwd to the path

    Args:
        path (Path): The path to use

    Yields:
        None
    """

    origin = pathlib.Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


class TestDiagTable(unittest.TestCase):

    def test_DiagType(self):
        """Test that DiagYaml returns itself.
        """
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # Create empty diag_table file
                with open('diag_table', 'w'):
                    pass
                test_diag_yaml = DiagTable()
            self.assertIsInstance(test_diag_yaml, DiagTable)

    def test_DiagYaml_no_diag_table(self):
        """Test that the DiagYaml raises
           raises FileNotFoundError"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                # No data_table
                with self.assertRaises(FileNotFoundError):
                    DiagTable()

    def test_DiagYaml_path(self):
        """Thest the ability to give a path
           to a diag_table file"""
        # Path to example data
        DiagTable(os.path.join(EXAMPLE_DIR, 'diag_table'))

    def test_DiagYaml_output(self):
        """Test that DiagYaml outputs to a given filename/path"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                #Create empty diag_table file
                path = os.path.join(EXAMPLE_DIR, 'diag_table')
                dg_y = DiagTable(path)
                dg_y.main()
                dg_y.writeyaml(outname=os.path.join(testdir, 'output-test.yaml'))
    
    def test_DiagYaml_file_not_found(self):
        """Check if FileNotFoundError raised if given 
            a diag_table file that doesn't exist"""
        with self.assertRaises(FileNotFoundError):
            DiagTable('does_not_exist')

    def test_DiagYaml_conversion(self):
        """Test conversion of example file
            Checks for correct length of output yaml"""
        with tempfile.TemporaryDirectory() as testdir:
            with test_directory(testdir):
                path = os.path.join(EXAMPLE_DIR, 'diag_table')
                dg_y = DiagTable(path)
                dg_y.main()
                dg_y.writeyaml()
                with open(path+'.yaml', 'r') as fp:
                    lines = len(fp.readlines())
                    self.assertEqual(lines, 624)

    def test_DiagYaml_parse_table(self):
        """Test the reading of a field table"""
        with test_directory(testdir):
            with open('diag_table', 'w') as dg:
                dg.write("\"TRACER\", \"atmos_mod\", \"liq_wat\"\n")
                dg.write("\t\"longname\", \"cloud liquid specific humidity\"")
                dg.write("\t\"units\", \"kg/kg\" /")
            dg_y = DiagTable('diag_table')
            dg_y.main()
            ref_dict = {'diag_table': [OrderedDict([('field_type', 'tracer'),
                        ('modlist', [OrderedDict([('model_type', 'atmos_mod'),
                        ('varlist', [OrderedDict([('variable', 'liq_wat'),
                        ('longname', 'fm_yaml_null'), ('subparams0',
                        [OrderedDict([('cloud liquid specific humidityunits', 'kg/kg')])])])])])])])]}
                # Verify parse done correctly
            self.assertDictEqual(dg_y.lists_wh_yaml, ref_dict)

if __name__ == '__main__':
    unittest.main()
