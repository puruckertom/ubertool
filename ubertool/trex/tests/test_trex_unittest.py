import unittest
import os.path
import sys
import numpy.testing as npt
import pandas as pd

#find parent directory and import model
parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from trex_exe import TRex

# create empty pandas dataframes to create empty object for testing
df_empty = pd.DataFrame()
# create an empty trex object
trex_empty = TRex(df_empty, df_empty)

test = {}

class TestTrex(unittest.TestCase):

    def setUp(self):
        """
        Setup routine for trex unit tests.
        :return:
        """
        pass
        # setup the test as needed
        # e.g. pandas to open trex qaqc csv
        #  Read qaqc csv and create pandas DataFrames for inputs and expected outputs

    def tearDown(self):
        """
        Teardown routine for trex unit tests.
        :return:
        """
        pass
        # teardown called after each test
        # e.g. maybe write test results to some text file


    def test_app_rate_parsing(self):
        """
        unittest for function app_rate_testing:
        method extracts 1st and maximum from each list in a series of lists of app rates
        """
        expected_results = pd.Series([], dtype="object")
        result = pd.Series([], dtype="object")
        expected_results = [[0.34, 0.78, 2.34], [0.34, 3.54, 2.34]]
        try:
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 3.54], [2.34, 1.384, 2.22]], dtype='object')
            #trex_empty.app_rates = ([[0.34], [0.78, 3.54], [2.34, 1.384, 2.22]])
            # parse app_rates Series of lists
            trex_empty.app_rate_parsing()
            result = [trex_empty.first_app_rate, trex_empty.max_app_rate]
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_conc_initial(self):
        """
        unittest for function conc_initial:
        conc_0 = (app_rate * self.frac_act_ing * food_multiplier)
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [12.7160, 9.8280, 11.2320]
        try:
                # specify an app_rates Series (that is a series of lists, each list representing
                # a set of application rates for 'a' model simulation)
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                              [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            for i in range(len(trex_empty.frac_act_ing)):
                result[i] = trex_empty.conc_initial(i, trex_empty.app_rates[i][0], trex_empty.food_multiplier_init_sg[i])
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_conc_timestep(self):
        """
        unittest for function conc_timestep:
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [6.25e-5, 0.039685, 7.8886e-30]
        try:
            trex_empty.foliar_diss_hlife = pd.Series([.25, 0.75, 0.01], dtype='float')
            conc_0 = pd.Series([0.001, 0.1, 10.0])
            for i in range(len(conc_0)):
                result[i] = trex_empty.conc_timestep(i, conc_0[i])
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_percent_to_frac(self):
        """
        unittest for function percent_to_frac:
        """
        expected_results = [.04556, .1034, .9389]
        try:
            trex_empty.percent_incorp = pd.Series([4.556, 10.34, 93.89], dtype='float')
            result = trex_empty.percent_to_frac(trex_empty.percent_incorp)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_inches_to_feet(self):
        """
        unittest for function inches_to_feet:
        """
        expected_results = [0.37966, 0.86166, 7.82416]
        try:
            trex_empty.bandwidth = pd.Series([4.556, 10.34, 93.89], dtype='float')
            result = trex_empty.inches_to_feet(trex_empty.bandwidth)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_at_bird(self):
        """
        unittest for function at_bird:
        adjusted_toxicity = self.ld50_bird * (aw_bird / self.tw_bird_ld50) ** (self.mineau_sca_fact - 1)
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [69.17640, 146.8274, 56.00997]
        try:
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            # following variable is unique to at_bird and is thus sent via arg list
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')
            for i in range(len(trex_empty.aw_bird_sm)):
                result[i] = trex_empty.at_bird(i, trex_empty.aw_bird_sm[i])
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_at_bird1(self):
        """
        unittest for function at_bird1; alternative approach using more vectorization:
        adjusted_toxicity = self.ld50_bird * (aw_bird / self.tw_bird_ld50) ** (self.mineau_sca_fact - 1)
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [69.17640, 146.8274, 56.00997]
        try:
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')
            # for i in range(len(trex_empty.aw_bird_sm)):
            #     result[i] = trex_empty.at_bird(i, trex_empty.aw_bird_sm[i])
            result = trex_empty.at_bird1(trex_empty.aw_bird_sm)

            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_fi_bird(self):
        """
        unittest for function fi_bird:
        food_intake = (0.648 * (aw_bird ** 0.651)) / (1 - mf_w_bird)
        """
        expected_results = [4.19728, 22.7780, 59.31724]
        try:
#?? 'mf_w_bird_1' is a constant (i.e., not an input whose value changes per model simulation run); thus it should
#?? be specified here as a constant and not a pd.series -- if this is correct then go ahead and change next line
            trex_empty.mf_w_bird_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')
            result = trex_empty.fi_bird(trex_empty.aw_bird_sm, trex_empty.mf_w_bird_1)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sc_bird(self):
        """
        unittest for function sc_bird:
        m_s_a_r = ((self.app_rate * self.frac_act_ing) / 128) * self.density * 10000  # maximum seed application rate=application rate*10000
        risk_quotient = m_s_a_r / self.noaec_bird
        """

        expected_results = [6.637969, 77.805, 34.96289]
        try:
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.frac_act_ing = pd.Series([0.15, 0.20, 0.34], dtype='float')
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')
            trex_empty.noaec_bird = pd.Series([5., 1.25, 12.], dtype='float')
            result = trex_empty.sc_bird()
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sa_bird_1(self):
        """
        # unit test for function sa_bird_1
        """
        result_sm = pd.Series([], dtype = 'float')
        result_md = pd.Series([], dtype = 'float')
        result_lg = pd.Series([], dtype = 'float')

        expected_results_sm = pd.Series([0.228229, 0.704098, 0.145205], dtype = 'float')
        expected_results_md = pd.Series([0.126646, 0.540822, 0.052285], dtype = 'float')
        expected_results_lg = pd.Series([0.037707, 0.269804, 0.01199], dtype = 'float')

        try:
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')

            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.aw_bird_md = pd.Series([115., 120., 130.], dtype='float')
            trex_empty.aw_bird_lg = pd.Series([1015., 1020., 1030.], dtype='float')

            #reitierate constants here (they have been set in 'trex_inputs'; repeated here for clarity)
            trex_empty.mf_w_bird_1 = 0.1
            trex_empty.nagy_bird_coef_sm = 0.02
            trex_empty.nagy_bird_coef_md = 0.1
            trex_empty.nagy_bird_coef_lg = 1.0

            result_sm = trex_empty.sa_bird_1("small")
            npt.assert_allclose(result_sm,expected_results_sm,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_md = trex_empty.sa_bird_1("medium")
            npt.assert_allclose(result_md,expected_results_md,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_lg = trex_empty.sa_bird_1("large")
            npt.assert_allclose(result_lg,expected_results_lg,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sa_bird_2(self):
        """
        # unit test for function sa_bird_2
        """
        result_sm = pd.Series([], dtype = 'float')
        result_md = pd.Series([], dtype = 'float')
        result_lg = pd.Series([], dtype = 'float')

        expected_results_sm =pd.Series([0.018832, 0.029030, 0.010483], dtype = 'float')
        expected_results_md = pd.Series([2.774856e-3, 6.945353e-3, 1.453192e-3], dtype = 'float')
        expected_results_lg =pd.Series([2.001591e-4, 8.602729e-4, 8.66163e-5], dtype = 'float')

        try:
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')
            trex_empty.max_seed_rate = pd.Series([33.19, 20.0, 45.6])

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')

            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.aw_bird_md = pd.Series([115., 120., 130.], dtype='float')
            trex_empty.aw_bird_lg = pd.Series([1015., 1020., 1030.], dtype='float')

            #reitierate constants here (they have been set in 'trex_inputs'; repeated here for clarity)
            trex_empty.nagy_bird_coef_sm = 0.02
            trex_empty.nagy_bird_coef_md = 0.1
            trex_empty.nagy_bird_coef_lg = 1.0

            result_sm = trex_empty.sa_bird_2("small")
            npt.assert_allclose(result_sm,expected_results_sm,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_md = trex_empty.sa_bird_2("medium")
            npt.assert_allclose(result_md,expected_results_md,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_lg = trex_empty.sa_bird_2("large")
            npt.assert_allclose(result_lg,expected_results_lg,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sa_mamm_1(self):
        """
        # unit test for function sa_mamm_1
        """
        result_sm = pd.Series([], dtype = 'float')
        result_md = pd.Series([], dtype = 'float')
        result_lg = pd.Series([], dtype = 'float')

        expected_results_sm =pd.Series([0.022593, 0.555799, 0.010178], dtype = 'float')
        expected_results_md = pd.Series([0.019298, 0.460911, 0.00376], dtype = 'float')
        expected_results_lg =pd.Series([0.010471, 0.204631, 0.002715], dtype = 'float')

        try:
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.tw_mamm = pd.Series([350., 225., 390.], dtype='float')
            trex_empty.ld50_mamm = pd.Series([321., 100., 400.], dtype='float')

            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.aw_mamm_md = pd.Series([35., 45., 25.], dtype='float')
            trex_empty.aw_mamm_lg = pd.Series([1015., 1020., 1030.], dtype='float')

            #reitierate constants here (they have been set in 'trex_inputs'; repeated here for clarity)
            trex_empty.mf_w_mamm_1 = 0.1
            trex_empty.nagy_mamm_coef_sm = 0.015
            trex_empty.nagy_mamm_coef_md = 0.035
            trex_empty.nagy_mamm_coef_lg = 1.0

            result_sm = trex_empty.sa_mamm_1("small")
            npt.assert_allclose(result_sm,expected_results_sm,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_md = trex_empty.sa_mamm_1("medium")
            npt.assert_allclose(result_md,expected_results_md,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_lg = trex_empty.sa_mamm_1("large")
            npt.assert_allclose(result_lg,expected_results_lg,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sa_mamm_2(self):
        """
        # unit test for function sa_mamm_2
        """
        result_sm = pd.Series([], dtype = 'float')
        result_md = pd.Series([], dtype = 'float')
        result_lg = pd.Series([], dtype = 'float')

        expected_results_sm =pd.Series([2.46206e-3, 3.103179e-2, 1.03076e-3], dtype = 'float')
        expected_results_md = pd.Series([1.304116e-3, 1.628829e-2, 4.220702e-4], dtype = 'float')
        expected_results_lg =pd.Series([1.0592147e-4, 1.24391489e-3, 3.74263186e-5], dtype = 'float')

        try:
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.tw_mamm = pd.Series([350., 225., 390.], dtype='float')
            trex_empty.ld50_mamm = pd.Series([321., 100., 400.], dtype='float')

            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.aw_mamm_md = pd.Series([35., 45., 25.], dtype='float')
            trex_empty.aw_mamm_lg = pd.Series([1015., 1020., 1030.], dtype='float')

            #reitierate constants here (they have been set in 'trex_inputs'; repeated here for clarity)
            trex_empty.mf_w_mamm_1 = 0.1
            trex_empty.nagy_mamm_coef_sm = 0.015
            trex_empty.nagy_mamm_coef_md = 0.035
            trex_empty.nagy_mamm_coef_lg = 1.0

            result_sm = trex_empty.sa_mamm_2("small")
            npt.assert_allclose(result_sm,expected_results_sm,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_md = trex_empty.sa_mamm_2("medium")
            npt.assert_allclose(result_md,expected_results_md,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_lg = trex_empty.sa_mamm_2("large")
            npt.assert_allclose(result_lg,expected_results_lg,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_sc_mamm(self):
        """
        # unit test for function sc_mamm
        """
        result_sm = pd.Series([], dtype = 'float')
        result_md = pd.Series([], dtype = 'float')
        result_lg = pd.Series([], dtype = 'float')

        expected_results_sm =pd.Series([2.90089, 15.87995, 8.142130], dtype = 'float')
        expected_results_md = pd.Series([2.477926, 13.16889, 3.008207], dtype = 'float')
        expected_results_lg =pd.Series([1.344461, 5.846592, 2.172211], dtype = 'float')

        try:
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'first_app_rate' per model simulation run
            trex_empty.density = pd.Series([8.33, 7.98, 6.75], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.tw_mamm = pd.Series([350., 225., 390.], dtype='float')
            trex_empty.noael_mamm = pd.Series([2.5, 3.5, 0.5], dtype='float')

            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.aw_mamm_md = pd.Series([35., 45., 25.], dtype='float')
            trex_empty.aw_mamm_lg = pd.Series([1015., 1020., 1030.], dtype='float')

            #reitierate constants here (they have been set in 'trex_inputs'; repeated here for clarity)
            trex_empty.mf_w_mamm_1 = 0.1
            trex_empty.nagy_mamm_coef_sm = 0.015
            trex_empty.nagy_mamm_coef_md = 0.035
            trex_empty.nagy_mamm_coef_lg = 1.0

            result_sm = trex_empty.sc_mamm("small")
            npt.assert_allclose(result_sm,expected_results_sm,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_md = trex_empty.sc_mamm("medium")
            npt.assert_allclose(result_md,expected_results_md,rtol=1e-4, atol=0, err_msg='', verbose=True)

            result_lg = trex_empty.sc_mamm("large")
            npt.assert_allclose(result_lg,expected_results_lg,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_rg_bird(self):
        """
        # unit test for function ld50_rg_bird (LD50ft-2 for Row/Band/In-furrow granular birds)
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [346.4856, 25.94132, 0.0]
        try:
            # following parameter values are unique for ld50_bg_bird
            trex_empty.application_type = pd.Series(['Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Liquid'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'max app rate' per model simulation run
            trex_empty.frac_incorp = pd.Series([0.25, 0.76, 0.05], dtype= 'float')
            trex_empty.bandwidth = pd.Series([2., 10., 30.], dtype = 'float')
            trex_empty.row_spacing = pd.Series([20., 32., 50.], dtype = 'float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_rg_bird(trex_empty.aw_bird_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_rg_bird1(self):
        """
        # unit test for function ld50_rg_bird1 (LD50ft-2 for Row/Band/In-furrow granular birds)

        this is a duplicate of the 'test_ld50_rg_bird' method using a more vectorized approach to the
        calculations; if desired other routines could be modified similarly
        --comparing this method with 'test_ld50_rg_bird' it appears (for this test) that both run in the same time
        --but I don't think this would be the case when 100's of model simulation runs are executed (and only a small
        --number of the application_types apply to this method; thus I conclude we continue to use the non-vectorized
        --approach  -- should be revisited when we have a large run to execute
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [346.4856, 25.94132, 0.0]
        try:
            # following parameter values are unique for ld50_bg_bird
            trex_empty.application_type = pd.Series(['Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Liquid'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.app_rate_parsing()  #get 'max app rate' per model simulation run
            trex_empty.frac_incorp = pd.Series([0.25, 0.76, 0.05], dtype= 'float')
            trex_empty.bandwidth = pd.Series([2., 10., 30.], dtype = 'float')
            trex_empty.row_spacing = pd.Series([20., 32., 50.], dtype = 'float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_rg_bird1(trex_empty.aw_bird_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_bl_bird(self):
        """
        # unit test for function ld50_bl_bird (LD50ft-2 for broadcast liquid birds)
        """
        expected_results = [46.19808, 33.77777, 0.]
        try:
            # following parameter values are unique for ld50_bl_bird
            trex_empty.application_type = pd.Series(['Broadcast-Liquid', 'Broadcast-Liquid',
                                                     'Non-Broadcast'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_bl_bird(trex_empty.aw_bird_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_bg_bird(self):
        """
        # unit test for function ld50_bg_bird (LD50ft-2 for broadcast granular)
        """
        expected_results = [46.19808, 0., 0.4214033]
        try:
            # following parameter values are unique for ld50_bg_bird
            trex_empty.application_type = pd.Series(['Broadcast-Granular', 'Broadcast-Liquid',
                                                     'Broadcast-Granular'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_bg_bird(trex_empty.aw_bird_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_rl_bird(self):
        """
        # unit test for function ld50_rl_bird (LD50ft-2 for Row/Band/In-furrow liquid birds)
        """
        expected_results = [0., 2.20701, 0.0363297]
        try:
            # following parameter values are unique for ld50_bg_bird
            trex_empty.application_type = pd.Series(['Broadcast-Granular', 'Row/Band/In-furrow-Liquid',
                                                     'Row/Band/In-furrow-Liquid'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.frac_incorp = pd.Series([0.25, 0.76, 0.05], dtype= 'float')
            trex_empty.bandwidth = pd.Series([2., 10., 30.], dtype = 'float')

            # following parameter values are needed for internal call to "test_at_bird"
            # results from "test_at_bird"  test using these values are [69.17640, 146.8274, 56.00997]
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_rl_bird(trex_empty.aw_bird_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_at_mamm(self):
        """
        unittest for function at_mamm:
        adjusted_toxicity = self.ld50_mamm * ((self.tw_mamm / aw_mamm) ** 0.25)
        """
        result = pd.Series([], dtype = 'float')
        expected_results = [705.5036, 529.5517, 830.6143]
        try:
            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            for i in range(len(trex_empty.ld50_mamm)):
                result[i] = trex_empty.at_mamm(i, trex_empty.aw_mamm_sm[i])
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_anoael_mamm(self):
        """
        unittest for function anoael_mamm:
        adjusted_toxicity = self.noael_mamm * ((self.tw_mamm / aw_mamm) ** 0.25)
        """
        expected_results = [5.49457, 9.62821, 2.403398]
        try:
            trex_empty.noael_mamm = pd.Series([2.5, 5.0, 1.25], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            result = trex_empty.anoael_mamm(trex_empty.aw_mamm_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_fi_mamm(self):
        """
        unittest for function fi_mamm:
        food_intake = (0.621 * (aw_mamm ** 0.564)) / (1 - mf_w_mamm)
        """
        expected_results = [3.17807, 16.8206, 42.28516]
        try:
            trex_empty.mf_w_mamm_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            result = trex_empty.fi_mamm(trex_empty.aw_mamm_sm, trex_empty.mf_w_mamm_1)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_bl_mamm(self):
        """
        # unit test for function ld50_bl_mamm (LD50ft-2 for broadcast liquid)
        """
        expected_results = [4.52983, 9.36547, 0.]
        try:
            # following parameter values are unique for ld50_bl_mamm
            trex_empty.application_type = pd.Series(['Broadcast-Liquid', 'Broadcast-Liquid',
                                                     'Non-Broadcast'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')

            # following parameter values are needed for internal call to "test_at_mamm"
            # results from "test_at_mamm"  test using these values are [705.5036, 529.5517, 830.6143]
            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_bl_mamm(trex_empty.aw_mamm_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_bg_mamm(self):
        """
        # unit test for function ld50_bg_mamm (LD50ft-2 for broadcast granular)
        """
        expected_results = [4.52983, 9.36547, 0.]
        try:
            # following parameter values are unique for ld50_bl_mamm
            trex_empty.application_type = pd.Series(['Broadcast-Granular', 'Broadcast-Granular',
                                                     'Broadcast-Liquid'], dtype='object')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')

            # following parameter values are needed for internal call to "at_mamm"
            # results from "test_at_mamm"  test using these values are [705.5036, 529.5517, 830.6143]
            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_bg_mamm(trex_empty.aw_mamm_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_rl_mamm(self):
        """
        # unit test for function ld50_rl_mamm (LD50ft-2 for Row/Band/In-furrow liquid mammals)
        """
        expected_results = [0., 0.6119317, 0.0024497]
        try:
            # following parameter values are unique for ld50_bl_mamm
            trex_empty.application_type = pd.Series(['Broadcast-Granular',
                                                     'Row/Band/In-furrow-Liquid',
                                                     'Row/Band/In-furrow-Liquid',], dtype='object')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.frac_incorp = pd.Series([0.25, 0.76, 0.05], dtype= 'float')

            # following parameter values are needed for internal call to "at_mamm"
            # results from "test_at_mamm"  test using these values are [705.5036, 529.5517, 830.6143]
            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')
            trex_empty.bandwidth = pd.Series([2., 10., 30.], dtype = 'float')

            result = trex_empty.ld50_rl_mamm(trex_empty.aw_mamm_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_ld50_rg_mamm(self):
        """
        # unit test for function ld50_rg_mamm
        """
        expected_results = [33.9737, 7.192681, 0.0]
        try:
            # following parameter values are unique for ld50_bl_mamm
            trex_empty.application_type = pd.Series(['Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Granular',
                                                     'Row/Band/In-furrow-Liquid',], dtype='object')
            trex_empty.app_rates = pd.Series([[0.34, 1.384, 13.54], [0.78, 11.34, 3.54],
                                          [2.34, 1.384, 3.4]], dtype='float')
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02], dtype='float')
            trex_empty.frac_incorp = pd.Series([0.25, 0.76, 0.05], dtype= 'float')
            trex_empty.bandwidth = pd.Series([2., 10., 30.], dtype = 'float')
            trex_empty.row_spacing = pd.Series([20., 32., 50.], dtype = 'float')

            # following parameter values are needed for internal call to "at_mamm"
            # results from "test_at_mamm"  test using these values are [705.5036, 529.5517, 830.6143]
            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.ld50_rg_mamm(trex_empty.aw_mamm_sm)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_eec_diet_max(self):
        """
        combined unit test for methods eec_diet_max & eec_diet_timeseries;

        * this test calls eec_diet_max, which in turn calls eec_diet_timeseries (which produces
          concentration timeseries), which in turn calls conc_initial and conc_timestep
        * eec_diet_max processes the timeseries and extracts the maximum values

        * this test tests both eec_diet_max & eec_diet_timeseries together (ok, so this violates the exact definition
        * of 'unittest', get over it)
        * the assertion check is that the maximum values from the timeseries match expectations
        * this assumes that for the maximums to be 'as expected' then the timeseries are as well
        * note: the 1st application day ('day_out') for the 2nd model simulation run is set to 0 here
        * to make sure the timeseries processing works when an application occurs on 1st day of year
        """

        expected_results = [12.716, 145.3409, 11.232]
        num_app_days = pd.Series([], dtype='int')
        try:
            #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [0, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'series of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            result = trex_empty.eec_diet_max(trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_eec_dose_bird(self):
        """
        unit test for function eec_dose_bird;
        internal call to 'eec_diet_max' --> 'eed_diet_timeseries' --> conc_initial' and 'conc_timestep' are included;
        internal call  to 'fi_bird' included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'eec_dose_bird' are correctly implemented
        * methods called inside of 'eec_dose_bird' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [3.55817, 168.32712, 22.20837]
        num_app_days = pd.Series([], dtype='int')
        try:
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            # variables for 'fi_bird'  (values reflect unittest for 'at_bird'
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            trex_empty.mf_w_bird_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')

            result = trex_empty.eec_dose_bird(trex_empty.aw_bird_sm, trex_empty.mf_w_bird_1,
                                              trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_arq_dose_bird(self):
        """
        unit test for function arq_dose_bird;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'arq_dose_bird' are correctly implemented
        * methods called inside of 'arq_dose_bird' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [0.051436, 1.146429, 0.396508]
        num_app_days = pd.Series([], dtype='int')
        try:
            #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            # variables for 'at_bird'  (values reflect unittest for 'fi_bird'
            trex_empty.ld50_bird = pd.Series([100., 125., 90.], dtype='float')
            trex_empty.tw_bird_ld50 = pd.Series([175., 100., 200.], dtype='float')
            trex_empty.mineau_sca_fact = pd.Series([1.15, 0.9, 1.25], dtype='float')
            trex_empty.aw_bird_sm = pd.Series([15., 20., 30.], dtype='float')

            trex_empty.mf_w_bird_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')

            result = trex_empty.arq_dose_bird(trex_empty.aw_bird_sm, trex_empty.mf_w_bird_1,
                                              trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_arq_diet_bird(self):
        """
        unit test for function arq_diet_bird;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'arq_diet_bird' are correctly implemented
        * methods called inside of 'arq_diet_bird' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [0.019563, 0.205847, 0.010192]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.lc50_bird = pd.Series([650., 718., 1102.])

            result = trex_empty.arq_diet_bird(trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_crq_diet_bird(self):
        """
        unit test for function crq_diet_bird;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'crq_diet_bird' are correctly implemented
        * methods called inside of 'crq_diet_bird' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [2.5432, 8.211, 0.110118]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.noaec_bird = pd.Series([5., 18., 102.])

            result = trex_empty.crq_diet_bird(trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_eec_dose_mamm(self):
        """
        unit test for function eec_dose_mamm;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'eec_dose_mamm' are correctly implemented
        * methods called inside of 'eec_dose_mamm' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
       """
        expected_results = [2.69416, 124.3028, 15.8315]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.mf_w_mamm_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            result = trex_empty.eec_dose_mamm(trex_empty.aw_mamm_sm, trex_empty.mf_w_mamm_1,
                                              trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_arq_dose_mamm(self):
        """
        unit test for function arq_dose_mamm;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'arq_dose_mamm' are correctly implemented
        * methods called inside of 'arq_dose_mamm' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [0.003819, 0.234732, 0.01906]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.noael_mamm = pd.Series([2.5, 5.0, 1.25], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')

            trex_empty.mf_w_mamm_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')

            result = trex_empty.arq_dose_mamm(trex_empty.aw_mamm_sm, trex_empty.mf_w_mamm_1,
                                              trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_crq_dose_mamm(self):
        """
        unit test for function crq_dose_mamm;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'crq_dose_mamm' are correctly implemented
        * methods called inside of 'crq_dose_mamm' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [0.49033, 12.91027, 6.587159]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.ld50_mamm = pd.Series([321., 275., 432.], dtype='float')
            trex_empty.tw_mamm = pd.Series([350., 275., 410.], dtype='float')
            trex_empty.aw_mamm_sm = pd.Series([15., 20., 30.], dtype='float')

            trex_empty.mf_w_mamm_1 = pd.Series([0.1, 0.8, 0.9], dtype='float')

            result = trex_empty.crq_dose_mamm(trex_empty.aw_mamm_sm, trex_empty.mf_w_mamm_1,
                                              trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_arq_diet_mamm(self):
        """
        unit test for function arq_diet_mamm;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'arq_diet_mamm' are correctly implemented
        * methods called inside of 'arq_diet_mamm' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)

        """
        expected_results = [0.195631, 20.81662, 0.110118]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.lc50_mamm = pd.Series([65., 7.1, 102.])

            result = trex_empty.arq_diet_mamm(trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

    def test_crq_diet_mamm(self):
        """
        unit test for function crq_diet_mamm;
        internal calls to 'eec_diet_max'  --> 'eec_diet_timeseries' --> 'conc_initial' and 'conc_timestep' are included

        unit tests of this routine include the following approach:
        * this test verifies that the logic & calculations performed within the 'crq_diet_mamm' are correctly implemented
        * methods called inside of 'crq_diet_mamm' are not retested/recalculated
        * only the correct passing of variables/values is verified (calculations having been verified in previous unittests)
        """
        expected_results = [0.195631, 2.95596, 0.110118]
        num_app_days = pd.Series([], dtype='int')
        try:
             #specifying 3 different application scenarios of 1, 4, and 2 applications
            trex_empty.app_rates = pd.Series([[0.34], [0.78, 11.34, 3.54, 1.54], [2.34, 1.384]], dtype='object')
            trex_empty.day_out = pd.Series([[5], [5, 10, 20, 50], [150, 250]], dtype='object')
            for i in range(len(trex_empty.app_rates)):
                trex_empty.num_apps[i] = len(trex_empty.app_rates[i])
                num_app_days[i] = len(trex_empty.day_out[i])
                assert (trex_empty.num_apps[i] == num_app_days[i]), 'list of app-rates and app_days do not match'
            trex_empty.frac_act_ing = pd.Series([0.34, 0.84, 0.02])
            trex_empty.food_multiplier_init_sg = pd.Series([110., 15., 240.], dtype='float')
            trex_empty.foliar_diss_hlife = pd.Series([25., 5., 45.])

            trex_empty.noaec_mamm = pd.Series([65., 50., 102.])

            result = trex_empty.crq_diet_mamm(trex_empty.food_multiplier_init_sg)
            npt.assert_allclose(result,expected_results,rtol=1e-4, atol=0, err_msg='', verbose=True)
        finally:
            pass
        return

# unittest will
# 1) call the setup method,
# 2) then call every method starting with "test",
# 3) then the teardown method
if __name__ == '__main__':
    unittest.main()
    #pass