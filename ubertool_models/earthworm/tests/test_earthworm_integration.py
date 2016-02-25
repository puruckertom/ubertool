# -*- coding: utf-8 -*-
import os.path
import pandas as pd
import numpy.testing as npt
import unittest
import pkgutil
from StringIO import StringIO
from tabulate import tabulate
import sys

#find parent directory and import model
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from earthworm_exe import Earthworm

#sys.path.append('/Users/puruckertom/git/qed/ubertool_ecorest/ubertool')
#from ubertool_models.earthworm.earthworm_exe import Earthworm

print(sys.path)
print(os.path)

# load transposed qaqc data for inputs and expected outputs
# works for local nosetests from parent directory
# but not for travis container that calls nosetests:

# this works for both local nosetests and travis deploy
#input details
try:
    if __package__ is not None:
        csv_data = pkgutil.get_data(__package__, 'earthworm_qaqc_in_transpose.csv')
        data_inputs = StringIO(csv_data)
        pd_obj_inputs = pd.read_csv(data_inputs, index_col=0, engine='python')
    else:
        csv_transpose_path_in = "./earthworm_qaqc_in_transpose.csv"
        print(csv_transpose_path_in)
        pd_obj_inputs = pd.read_csv(csv_transpose_path_in, index_col=0, engine='python')
        #with open('./earthworm_qaqc_in_transpose.csv') as f:
            #csv_data = csv.reader(f)
finally:
    print('earthworm inputs')
    #print('earthworm input dimensions ' + str(pd_obj_inputs.shape))
    #print('earthworm input keys ' + str(pd_obj_inputs.columns.values.tolist()))
    #print(pd_obj_inputs)

# load transposed qaqc data for expected outputs
# works for local nosetests from parent directory
# but not for travis container that calls nosetests:
# csv_transpose_path_exp = "./terrplant_qaqc_exp_transpose.csv"
# pd_obj_exp_out = pd.read_csv(csv_transpose_path_exp, index_col=0, engine='python')
# print(pd_obj_exp_out)
# this works for both local nosetests and travis deploy
#expected output details
try:
    if __package__ is not None:
        data_exp_outputs = StringIO(pkgutil.get_data(__package__, 'earthworm_qaqc_exp_transpose.csv'))
        pd_obj_exp = pd.read_csv(data_exp_outputs, index_col=0, engine= 'python')
        print("earthworm expected outputs")
        print('earthworm expected output dimensions ' + str(pd_obj_exp.shape))
        print('earthworm expected output keys ' + str(pd_obj_exp.columns.values.tolist()))
    else:
        csv_transpose_path_exp = "./earthworm_qaqc_exp_transpose.csv"
        print(csv_transpose_path_exp)
        pd_obj_exp = pd.read_csv(csv_transpose_path_exp, index_col=0, engine='python')
finally:
    print('earthworm expected')

#output details
earthworm_calc = Earthworm(pd_obj_inputs, pd_obj_exp)
earthworm_calc.execute_model()
inputs_json, outputs_json, exp_out_json = earthworm_calc.get_dict_rep(earthworm_calc)
print("earthworm output")
print(inputs_json)

#print input tables
print(tabulate(pd_obj_inputs.iloc[:,0:5], headers='keys', tablefmt='fancy_grid'))
print(tabulate(pd_obj_inputs.iloc[:,6:11], headers='keys', tablefmt='fancy_grid'))
print(tabulate(pd_obj_inputs.iloc[:,12:17], headers='keys', tablefmt='fancy_grid'))

#print expected output tables
print(tabulate(pd_obj_exp.iloc[:,0:1], headers='keys', tablefmt='fancy_grid'))

test = {}


class TestEarthworm(unittest.TestCase):
    """
    Integration tests for earthworm model.
    """
    def setUp(self):
        """
        Test setup method.
        :return:
        """
        pass

    def tearDown(self):
        """
        Test teardown method.
        :return:
        """
        pass

    def test_earthworm_fugacity(self):
        """
        Integration test for earthworm.earthworm_fugacity
        """
        try:
            self.blackbox_method_int('earthworm_fugacity')
        finally:
            pass
        return

    def blackbox_method_int(self, output):
        """
        Helper method to reuse code for testing numpy array outputs from TerrPlant model
        :param output: String; Pandas Series name (e.g. column name) without '_out'
        :return:
        """
        pd.set_option('display.float_format','{:.4E}'.format) # display model output in scientific notation
        result = earthworm_calc.pd_obj_out["out_" + output]
        expected = earthworm_calc.pd_obj_exp["exp_" + output]
        tab = pd.concat([result,expected], axis=1)
        print(" ")
        print(tabulate(tab, headers='keys', tablefmt='fancy_grid'))
        #npt.assert_array_almost_equal(result, expected, 4, '', True)
        rtol = 1e-5
        npt.assert_allclose(result,expected,rtol,0,'',True)

# unittest will
# 1) call the setup method,
# 2) then call every method starting with "test",
# 3) then the teardown method
if __name__ == '__main__':
    unittest.main()