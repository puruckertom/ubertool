from __future__ import division
import logging
import numpy as np
import os
import pandas as pd
import scipy.interpolate as interp
from scipy import integrate
from scipy.optimize import curve_fit
# import sqlalchemy_utils as sqlu
import sys
import csv


#find parent directory and import model
# parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# sys.path.append(parentddir)

from base.uber_model import UberModel, ModelSharedInputs
from .agdrift_functions import AgdriftFunctions

class AgdriftInputs(ModelSharedInputs):
    """
    Input class for Agdrift.
    """

    def __init__(self):
        """Class representing the inputs for Agdrift"""
        super(AgdriftInputs, self).__init__()
        self.application_rate = pd.Series([], dtype="float")
        self.application_method = pd.Series([], dtype="object")
        self.drop_size_aerial = pd.Series([], dtype="object")
        self.drop_size_ground = pd.Series([], dtype="object")
        self.ecosystem_type = pd.Series([], dtype="object")
        self.boom_height = pd.Series([], dtype="object")
        self.airblast_type = pd.Series([], dtype="object")
        self.aquatic_body_type = pd.Series([], dtype="object")
        self.terrestrial_field_type = pd.Series([], dtype="object")
        self.user_pond_width = pd.Series([], dtype="float")
        self.user_pond_depth = pd.Series([], dtype="float")
        self.user_wetland_width = pd.Series([], dtype="float")
        self.user_wetland_depth = pd.Series([], dtype="float")
        self.user_terrestrial_width = pd.Series([], dtype="float")
        self.downwind_distance = pd.Series([], dtype="float")
        self.calculation_input = pd.Series([], dtype="object")
        self.user_frac_applied = pd.Series([], dtype="float")
        self.user_avg_dep_gha = pd.Series([], dtype="float")
        self.user_avg_dep_lbac = pd.Series([], dtype="float")
        self.user_avg_conc_ngl = pd.Series([], dtype="float")
        self.user_avg_dep_mgcm2 = pd.Series([], dtype="float")


class AgdriftOutputs(object):
    """
    Output class for Agdrift.
    """

    def __init__(self):
        """Class representing the outputs for Agdrift"""
        super(AgdriftOutputs, self).__init__()
        #self.out_nasae = pd.Series(name="out_nasae").astype("int")
        self.out_sim_scenario_chk = pd.Series(name="out_sim_scenario_chk", dtype="object")
        self.out_sim_scenario_id = pd.Series(name="out_sim_scenario_id", dtype="object")
        #self.out_express_y = pd.Series(name="out_express_y", dtype="object")
        self.out_distance_downwind = pd.Series(name="out_distance_downwind", dtype="float")
        self.out_avg_dep_foa = pd.Series(name="out_avg_dep_foa", dtype="float")
        self.out_avg_dep_lbac = pd.Series(name="out_avg_dep_lbac", dtype="float")
        self.out_avg_dep_gha = pd.Series(name="out_avg_dep_gha", dtype="float")
        self.out_avg_waterconc_ngl = pd.Series(name="out_avg_waterconc_ngl", dtype="float")
        self.out_avg_field_dep_mgcm2 = pd.Series(name="out_avg_field_dep_mgcm2", dtype="float")
        self.out_area_width = pd.Series(name="out_default_width", dtype="float")
        self.out_area_length = pd.Series(name="out_default_length", dtype="float")
        self.out_area_depth = pd.Series(name="out_default_pond_depth", dtype="float")
        self.out_range_chk = pd.Series(name="out_range_chk", dtype="object")

class Agdrift(UberModel, AgdriftInputs, AgdriftOutputs, AgdriftFunctions):
    """
    Agdrift class to implement tier 1 air drift screening models.
    """

    def __init__(self, pd_obj, pd_obj_exp):
        """Class representing the Agdrift model and containing all its methods"""
        super(Agdrift, self).__init__()
        self.pd_obj = pd_obj
        self.pd_obj_exp = pd_obj_exp
        self.pd_obj_out = None

    def execute_model(self):
        """
        Callable to execute the running of the model:
            1) Populate input parameters
            2) Create output DataFrame to hold the model outputs
            3) Run the model's methods to generate outputs
            4) Fill the output DataFrame with the generated model outputs
        """
        self.populate_inputs(self.pd_obj)
        self.pd_obj_out = self.populate_outputs()
        self.run_methods()
        self.fill_output_dataframe()
        logging.info(self.pd_obj_out)
        logging.info('executed agdrift')

    def run_methods(self):
        """
        Controller method that runs all subroutines in sequence.
        :return:
        """

        try:
            self.set_global_constants()
            self.create_additional_io_parameters()
            self.create_deposition_curve()
            self.determine_model_exe_direction()
        except:
            logging.info("Unexpected error:", sys.exc_info()[0])
            raise

    def determine_model_exe_direction(self):
        """
        :description decide per simulation which model direction to execute (forward or inverse calculation)
        :param
        :param
        :NOTE
        :return:
        """

        # loop through simulations calculating necessary interopolations/integrations and units conversions
        for i in range(self.num_simulations):
            if 'Invalid' not in self.out_sim_scenario_chk[i]:  # process only valid simulation scenarios

                # locate index of scenario that applies to this simulation
                for j in range(self.num_scenarios):
                    if self.out_sim_scenario_id[i] == self.scenario_name[j]:
                        scenario_index = j

                #for debugging purposes
                #self.write_arrays_to_csv(self.scenario_distance_data[scenario_index],
                #                    self.scenario_deposition_data[scenario_index], "dist_dep.csv")

                # determine area/length/depth of area of concern
                self.out_area_width[i], self.out_area_length[i], self.out_area_depth[i] = self.determine_area_dimensions(i)

                #initalize internal variables
                avg_dep_foa = avg_dep_lbac = avg_dep_gha = avg_field_dep_mgcm2 = \
                                  avg_waterconc_ngl = np.nan

                #choose and execute path through model (there are 5 inverse calculation paths and 1 forward calculation path)

                #inverse calculations
                if (self.calculation_input[i] == "fraction_of_applied"):

                    avg_dep_foa = self.user_frac_applied[i]  #from the user input

                    avg_dep_lbac = self.calc_avg_dep_lbac(avg_dep_foa, self.application_rate[i])
                    avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)

                    if (self.ecosystem_type[i] == "terrestrial_assessment"):
                        avg_field_dep_mgcm2 = self.calc_avg_fielddep_mgcm2(avg_dep_lbac)
                    else: #this is an Aquatic assessment, thus calculate the water concentration
                        avg_waterconc_ngl = self.calc_avg_waterconc_ngl(avg_dep_lbac, self.out_area_width[i],
                                                                        self.out_area_length[i], self.out_area_depth[i])
                    #set variables for inverse calculations
                    npts = len(self.scenario_distance_data[scenario_index])
                    x_in = self.scenario_distance_data[scenario_index]
                    y_in = self.scenario_deposition_data[scenario_index]
                    width = self.out_area_width[i]


                    #call inverse calculation method
                    if (self.ecosystem_type[i] == "aquatic_assessment" or
                                self.terrestrial_field_type[i] == "user_defined_terrestrial"):
                        x_out, y_out, npts_out, self.out_distance_downwind[i], self.out_range_chk[i]  = \
                            self.locate_integrated_avg(npts, x_in, y_in, width, avg_dep_foa)
                        #self.out_distance_downwind[i] = out_dist
                        #self.out_range_chk[i] = out_range
                    else:  #this is an EPA Defined Terrestrial (which calculates for a 'point' rather than an area)
                        self.out_distance_downwind[i], self.out_range_chk[i] = \
                            self.find_dep_pt_location(x_in, y_in, npts, avg_dep_foa)

                elif (self.calculation_input[i] == "initial_deposition_gha"):

                    avg_dep_gha = self.user_avg_dep_gha[i]    #from the user input

                    avg_dep_lbac = self.calc_avg_dep_lbac_from_gha(avg_dep_gha)
                    avg_dep_foa = self.calc_avg_dep_foa_from_lbac(avg_dep_lbac, self.application_rate[i])

                    if (self.ecosystem_type[i] == "terrestrial_assessment"):
                        avg_field_dep_mgcm2 = self.calc_avg_fielddep_mgcm2(avg_dep_lbac)
                    else: #this is an Aquatic assessment, thus calculate the water concentration
                        avg_waterconc_ngl = self.calc_avg_waterconc_ngl(avg_dep_lbac, self.out_area_width[i],
                                                                        self.out_area_length[i], self.out_area_depth[i])
                    #set variables for inverse calculations
                    npts = len(self.scenario_distance_data[scenario_index])
                    x_in = self.scenario_distance_data[scenario_index]
                    y_in = self.scenario_deposition_data[scenario_index]
                    width = self.out_area_width[i]

                    #call inverse calculation method
                    if (self.ecosystem_type[i] == "aquatic_assessment" or
                                self.terrestrial_field_type[i] == "user_defined_terrestrial"):
                        x_out, y_out, npts_out, self.out_distance_downwind[i], self.out_range_chk[i]  = \
                            self.locate_integrated_avg(npts, x_in, y_in, width, avg_dep_foa)
                        #self.out_distance_downwind[i] = out_dist
                        #self.out_range_chk[i] = out_range
                    else:  #this is an EPA Defined Terrestrial (which calculates for a 'point' rather than an area)
                        self.out_distance_downwind[i], self.out_range_chk[i] = \
                            self.find_dep_pt_location(x_in, y_in, npts, avg_dep_foa)

                elif (self.calculation_input[i] == "initial_deposition_lbac"):

                    avg_dep_lbac = self.user_avg_dep_lbac[i]

                    avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)
                    avg_dep_foa = self.calc_avg_dep_foa_from_lbac(avg_dep_lbac, self.application_rate[i])

                    if (self.ecosystem_type[i] == "terrestrial_assessment"):
                        avg_field_dep_mgcm2 = self.calc_avg_fielddep_mgcm2(avg_dep_lbac)
                    else:  #this is an Aquatic assessment, thus calculate the water concentration
                        avg_waterconc_ngl = self.calc_avg_waterconc_ngl(avg_dep_lbac, self.out_area_width[i],
                                                                        self.out_area_length[i], self.out_area_depth[i])
                    #set variables for inverse calculations
                    npts = len(self.scenario_distance_data[scenario_index])
                    x_in = self.scenario_distance_data[scenario_index]
                    y_in = self.scenario_deposition_data[scenario_index]
                    width = self.out_area_width[i]

                    #call inverse calculation method
                    if (self.ecosystem_type[i] == "aquatic_assessment" or
                                self.terrestrial_field_type[i] == "user_defined_terrestrial"):
                        x_out, y_out, npts_out, self.out_distance_downwind[i], self.out_range_chk[i]  = \
                            self.locate_integrated_avg(npts, x_in, y_in, width, avg_dep_foa)
                        #self.out_distance_downwind[i] = out_dist
                        #self.out_range_chk[i] = out_range
                    else:  #this is an EPA Defined Terrestrial (which calculates for a 'point' rather than an area)
                        self.out_distance_downwind[i], self.out_range_chk[i] = \
                            self.find_dep_pt_location(x_in, y_in, npts, avg_dep_foa)


                elif (self.calculation_input[i] == "initial_concentration_ngL"):

                    avg_waterconc_ngl = self.user_avg_conc_ngl[i]

                    avg_dep_lbac = self.calc_avg_dep_lbac_from_waterconc_ngl(avg_waterconc_ngl, self.out_area_width[i],
                                                                             self.out_area_length[i], self.out_area_depth[i])
                    avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)
                    avg_dep_foa = self.calc_avg_dep_foa_from_lbac(avg_dep_lbac, self.application_rate[i])

                    # call inverse calculation method
                    npts = len(self.scenario_distance_data[scenario_index])
                    x_in = self.scenario_distance_data[scenario_index]
                    y_in = self.scenario_deposition_data[scenario_index]
                    width = self.out_area_width[i]

                    x_out, y_out, npts_out, out_dist, out_range = self.locate_integrated_avg(npts, x_in, y_in, width,
                                                                                              avg_dep_foa)
                    self.out_distance_downwind[i] = out_dist
                    self.out_range_chk[i] = out_range


                elif (self.calculation_input[i] == "initial_deposition_mgcm2"):

                    avg_field_dep_mgcm2 = self.user_avg_dep_mgcm2[i]

                    avg_dep_lbac = self.calc_avg_dep_lbac_from_mgcm2(avg_field_dep_mgcm2)
                    avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)
                    avg_dep_foa = self.calc_avg_dep_foa_from_lbac(avg_dep_lbac, self.application_rate[i])

                    # call inverse calculation method
                    npts = len(self.scenario_distance_data[scenario_index])
                    x_in = self.scenario_distance_data[scenario_index]
                    y_in = self.scenario_deposition_data[scenario_index]
                    width = self.out_area_width[i]

                    if (self.terrestrial_field_type[i] == 'user_defined_terrestrial'):
                        #for User Defined Terrestrial we're looking for an average deposition over a field
                        x_out, y_out, npts_out, out_dist, out_range = self.locate_integrated_avg(npts, x_in, y_in,
                                                                                                  width, avg_dep_foa)
                        self.out_distance_downwind[i] = out_dist
                        self.out_range_chk[i] = out_range
                    else:  # EPA Defined Terrestrial: this option simply locates a point deposition distance rather than an area average
                        continuing = True
                        j = 0
                        while continuing:
                            if (x_in[j] <= self.max_distance):  #only allow point depositions within the max distance of the original deposition vs distance data
                                if (y_in[j] < avg_dep_foa):
                                    if (j > 0):
                                        fraction = (y_in[j-1] - avg_dep_foa) / (y_in[j-1] - y_in[j])
                                        out_dist = x_in[j-1] + fraction * (x_in[j] - x_in[j-1])

                                        # the following code represents OPP protocol to round up x_dist_of_interest to nearest x midpoint or boundary value
                                        # (except when x_dist_of_interest is in the range of the first 2 meters (i.e., 6.5616 ft)
                                        if (fraction <= 0.5 and out_dist > 3.2808):
                                            round_up_x_dist = 0.5 * (x_in[j] + x_in[j-1])
                                        elif (fraction > 0.5 and out_dist > 3.2808):
                                            round_up_x_dist = x_in[j]
                                        else:
                                            round_up_x_dist = 3.2808
                                        if (out_dist > 3.2808 and out_dist < 6.5616):
                                            round_up_x_dist = 6.5616
                                        self.out_distance_downwind[i] = round_up_x_dist  #i is simulation number
                                    else:
                                        self.out_distance_downwind[i] = 0.0
                                    continuing = False
                                j += 1
                            else:
                                self.out_distance_downwind[i] = np.nan
                                self.out_range_chk[i] = "out of range"
                                continuing = False

                elif (self.calculation_input[i] == "distance_to_point_or_area_ft"):  # forward calculation
                    avg_dep_foa, avg_dep_lbac, avg_dep_gha, avg_waterconc_ngl, avg_field_dep_mgcm2 = \
                        self.execute_interpolations_integrations(i, scenario_index)
                    self.out_distance_downwind[i] = self.downwind_distance[i] #just placing this in the output for clarity and consistency

                else:
                    sys.exit("Invalid choice of calculation method")

                if self.round:
                    self.round_model_outputs(avg_dep_foa, avg_dep_lbac, avg_dep_gha, avg_waterconc_ngl,
                                             avg_field_dep_mgcm2, i)
                else:
                    self.out_avg_dep_foa[i] = avg_dep_foa
                    self.out_avg_dep_lbac[i] = avg_dep_lbac
                    self.out_avg_dep_gha[i] = avg_dep_gha
                    self.out_avg_waterconc_ngl[i] = avg_waterconc_ngl
                    self.out_avg_field_dep_mgcm2[i] = avg_field_dep_mgcm2
        return

    def execute_interpolations_integrations(self,i, scenario_index):
        #for current simulation calculate necessary interopolations/integrations and units conversions

        #intialize internal variable datatypes and set as nan
        avg_dep_foa = avg_dep_lbac = avg_dep_gha = avg_waterconc_ngl = \
                            avg_field_dep_mgcm2 = np.nan #float('nan')

        # set distance from edge of application area to user specified initial point of interest
        distance_downwind_short = self.downwind_distance[i]

         # perform integration across areas and calculate relevant average water concentrations and aerial deposition rates
        if (self.ecosystem_type[i] == 'aquatic_assessment' or
                (self.ecosystem_type[i] == 'terrestrial_assessment' and
                         self.terrestrial_field_type[i] == 'user_defined_terrestrial')):

            # set distance value to downwind side of area for which  integration is needed
            distance_downwind_long = distance_downwind_short + self.out_area_width[i]

            # check if distance (from edge of application area) to upwind edge of waterbody is <= 997 and that
            # self.out_area_width[i] >= 6.56 & <= 997
            # if these conditions are not met then invalidate this simulation (997 is the furthest distance for which deposition data is available)
            if (distance_downwind_short <= self.max_distance and self.out_area_width[i] <= self.max_distance and
                        self.out_area_width[i] >= self.min_area_width):

                # integrate over distance from nearest to furthest downwind points of pond/wetland/field
                integration_result = integrate.romberg(self.scenario_interp_func[scenario_index],
                                                       distance_downwind_short, distance_downwind_long, divmax=15)

                # calculate output variables
                avg_dep_foa = self.calc_avg_dep_foa(integration_result, self.out_area_width[i])
                avg_dep_lbac = self.calc_avg_dep_lbac(avg_dep_foa, self.application_rate[i])
                avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)

                # calculate water concentration for waterbody or area avg deposition rate for terrestrial area
                if (self.ecosystem_type[i] == 'aquatic_assessment'):
                    avg_waterconc_ngl = self.calc_avg_waterconc_ngl(avg_dep_lbac,
                                        self.out_area_width[i], self.out_area_length[i], self.out_area_depth[i])
                elif (self.ecosystem_type[i] == 'terrestrial_assessment'):
                    avg_field_dep_mgcm2 = self.calc_avg_fielddep_mgcm2(avg_dep_lbac)

            else:
                # set simulation_check variable to invalid
                self.out_sim_scenario_chk[i] = self.out_sim_scenario_chk[i].replace('Valid', 'Invalid') + \
                                               ' Due to Distance Violation'

        elif (self.ecosystem_type[i] == 'terrestrial_assessment' and
                      self.terrestrial_field_type[i] == 'epa_defined_terrestrial'):

            # just interested in point deposition (no integration)

            # calculate output variables
            #call interpolation function for downwind distance short
            avg_dep_foa = self.scenario_interp_func[scenario_index](distance_downwind_short)  # simply the fraction of applied deposition value at the point of intesest
            avg_dep_lbac = self.calc_avg_dep_lbac(avg_dep_foa, self.application_rate[i])
            avg_dep_gha = self.calc_avg_dep_gha(avg_dep_lbac)
            avg_field_dep_mgcm2 = self.calc_avg_fielddep_mgcm2(avg_dep_lbac)

        return avg_dep_foa, avg_dep_lbac, avg_dep_gha, avg_waterconc_ngl, avg_field_dep_mgcm2

    def create_deposition_curve(self):
        # load, process/filter, and create interpolation function for deposition data for all deposition scenarios incluced
        # in this model simulation run
        for i in range(self.num_scenarios):
            if (self.num_scenario_sims[i] > 0):  # only get data if scenario is included in 1 or more simulations
                self.scenario_raw_data[i] = self.get_scenario_deposition_data(self.scenario_name[i], self.num_db_values)

                # process raw data to remove blank values from distance and deposition arrays
                self.scenario_distance_data[i], self.scenario_deposition_data[i] = self.filter_arrays(
                    self.distances_temp, self.scenario_raw_data[i])  # always send in the original distance_temp array

                # extend distance vs deposition curve data (done for all curves)

                x_values = self.scenario_distance_data[i]
                y_values = self.scenario_deposition_data[i]
                self.scenario_distance_data[i], self.scenario_deposition_data[i] = \
                    self.extend_curve_opp(x_values, y_values, self.max_distance, self.distance_inc, self.num_pts_extend,
                                      self.extend_ln_ln)

                #verify monotonicity and whether increasing/decreasing
                dep_series = np.asarray(self.scenario_deposition_data[i])
                if (np.all(dep_series[1:] >= dep_series[:-1])):
                    self.data_series_type[i] = 'monotonic-increasing'
                elif (np.all(dep_series[1:] <= dep_series[:-1])):
                    self.data_series_type[i] = 'monotonic-decreasing'
                else:
                    self.data_series_type[i] = 'non-monotonic'

                # establish functions for deposition curve to facilitate interpolation and integration
                self.scenario_interp_func[i] = interp.interp1d(self.scenario_distance_data[i],
                                                           self.scenario_deposition_data[i], kind=self.interpolator)
        return

    def create_additional_io_parameters(self):
        # determine if scenario description data combine to form a valid scenario (i.e., one for which deposition data exists)
        self.out_sim_scenario_chk = pd.Series([], dtype='object')
        self.validate_sim_scenarios()

        # pull column names from sql database ((these names reflect scenario types)
        self.column_names = self.get_column_names()  # distance and scenario names as identified as database columns

        # -1 is to avoid counting the distance column as a scenario type
        self.num_scenarios = len(self.column_names) - 1

        # assign column names to appropriate variables (i.e., the distance and scenario names)
        self.assign_column_names()

        # scan simulation input data and define scenario ids (to match column names from sql database)
        self.set_sim_scenario_id()

        # assign list of simulations per scenario
        # this is so we can execute the interpolator function generator once per scenario type
        self.num_scenario_sims, self.scenario_sim_indices = self.list_sims_per_scenario()

        # pull distance array values from sql database (we assume array applies to all scenarios)
        self.distances_temp = self.get_distances(self.num_db_values)

        # populate output variable arrays with default values
        self.out_area_width = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_area_length = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_area_depth = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_distance_downwind = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_avg_dep_foa = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_avg_dep_lbac = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_avg_dep_gha = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_avg_waterconc_ngl = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_avg_field_dep_mgcm2 = pd.Series(self.num_simulations * ['nan'], dtype='float')
        self.out_range_chk = pd.Series(self.num_simulations * ['in range'], dtype='object')
        # initialize internal variables
        self.scenario_raw_data = pd.Series(self.num_scenarios * [[]], dtype='float')
        self.scenario_distance_data = pd.Series(self.num_scenarios * [[]], dtype='float')
        self.scenario_deposition_data = pd.Series(self.num_scenarios * [[]], dtype='float')
        self.scenario_interp_func = pd.Series(self.num_scenarios * ['NoFunction'], dtype='object')
        self.data_series_type = pd.Series(self.num_scenarios * ['non-monotonic'], dtype='object')

        return

    def set_global_constants(self):

        #set scenario database name
        #we only want to set this if it hasn't been set from the outside (e.g., for integration tests)
        if hasattr(self, 'db_name'):
            pass
        else:
            dir_path = os.path.dirname(os.path.abspath(__file__))
            logging.info('current directory path is:')
            logging.info(dir_path)
            #self.db_name = '/Users/puruckertom/git/qed_ubertool/ubertool_ecorest/ubertool/ubertool/agdrift/sqlite_agdrift_distance.db'
            #self.db_name = '/Users/GLANIAK/qed_ubertool/ubertool_ecorest/ubertool/ubertool/agdrift/sqlite_agdrift_distance.db'
            #self.db_name = 'sqlite:///sqlite_agdrift_distance.db'
            #self.db_name='jdbc:sqlite:C:/Users/GLANIAK/qed_ubertool/ubertool_ecorest/ubertool/ubertool/agdrift\sqlite_agdrift_distance.db'
            #self.db_name = 'jdbc:sqlite:C:/Users/GLANIAK/qed_ubertool/ubertool_ecorest/ubertool/ubertool/agdrift\sqlite_agdrift_distance.db'
            #self.db_name = 'sqlite:///sqlite_agdrift_distance.db'
            location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            self.db_name = os.path.join(location, 'sqlite_agdrift_distance.db')
        #ag_db_exists = sqlu.database_exists(self.db_name)
        print('Agdrift database: ' + str(self.db_name))
        #' exists = ' + str(ag_db_exists))
        #if ag_db_exists:
        #    logging.info('found agdrift database')
        #else:
        #    logging.info('cannot find agdrift database')#

        # set database table name, and number of data points/rows (all scenarios have equal number of data points)
        self.db_table = 'output'
        self.num_db_values = 161

        #set interpolation method for runs
        self.interpolator = 'linear'
        #self.interpolator = 'quadratic'
        #self.interpolator = 'cubic'

        #set method for extending distance vs deposition curve (True: use ln ln transform; False: use relative ln ln transfrom)
        self.extend_ln_ln = False

        #set whether to round calculated distance to nearest 1/2 x point value
        self.find_nearest_x = True

        #set whether to round output values (rounding used when direct comparison with AGDRIFT model outputs as presented in user interface)
        self.round = True

        #set number of model run simulations to be performed (equal to the number of entries in any one of the input variables)
        #used throughout code to specify number of times a piece of code should be executed (e.g., for loops)
        self.num_simulations = len(self.application_rate)

        #set standard width and length for ponds/wetlands/terrestrial fields
        self.default_width = pd.Series([208.7],dtype='float')  #feet of width of EPA Defined Pond or Wetland
        self.default_length = pd.Series([515.8],dtype='float') #feet of length of EPA Defined Pond or Wetland

        #set standard depth for ponds and wetlands
        # 2.0 m = 6.56168 feet
        self.default_pond_depth = pd.Series([6.56],dtype='float')       #feet
        self.default_wetland_depth = pd.Series([0.4921],dtype='float')  #feet

        self.num_pts_extend = 16  #number of data points at end of x,y array to be used for extending curve
        self.max_distance = 997.3632   #feet (this applies to both area_width and downwind distance to leading edge of pond/wetland/terrestrial area
        self.distance_inc = 6.56   #feet

        #these values will be used in context of validating inputs
        self.min_area_width = 0.328084   #feet or 0.1 meters
        self.min_waterbody_depth = 0.0328084  #feet or 0.01 meters
        self.max_waterbody_depth = 328.084  #feet or 100 meters

        self.sqft_per_hectare = 107636.  #size of all water (ponds and wetlands) and fields (terrestrial) in square feet (user can modify width only)
        self.acres_per_hectare = 2.471
        self.sqft_per_acre = 43560.
        self.cm2_per_ft2 = 929.03
        self.gms_per_lb = 453.592
        self.mg_per_gram = 1.e3
        self.ng_per_gram = 1.e9
        self.liters_per_ft3 = 28.3168
        self.meters_per_ft = 0.3048
        return
