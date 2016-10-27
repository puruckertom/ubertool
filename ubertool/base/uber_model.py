import importlib
import pandas as pd
import logging


class UberModel(object):
    """
    Collection of static methods used across all the ubertool models.
    """

    def __init__(self):
        """Main utility class for building Ubertool model classes for model execution."""
        super(UberModel, self).__init__()
        self.name = self.__class__.__name__
        self.pd_obj = None
        self.pd_obj_exp = None
        self.pd_obj_out = None

    def populate_inputs(self, pd_obj, model_obj):
        """
        Validate and assign user-provided model inputs to their respective class attributes
        :param pd_obj: Pandas DataFrame object of model input parameters
        :param model_obj:
        """
        try:
            # Import the model's input class (e.g. TerrplantInputs) to compare user supplied inputs to
            mod_name = model_obj.name.lower() + '.' + model_obj.name.lower() + '_exe'
            module = importlib.import_module(mod_name)
            model_inputs = getattr(module, model_obj.name + "Inputs")
            model_inputs_obj = model_inputs()
        except ValueError as err:
            logging.info(mod_name)
            logging.info(err.args)

        # Create temporary DataFrame where each column name is the same as ModelInputs attributes
        df = pd.DataFrame()
        for input_param in model_inputs_obj.__dict__:
            df[input_param] = getattr(self, input_param)

        # Compare column names of temporary DataFrame (created above) to user-supply DataFrame from JSON
        if df.columns.sort_values().equals(pd_obj.columns.sort_values()):
            # If the user-supplied DataFrame has the same column names as required by TRexInputs...
            # set each Series in the DataFrame to the corresponding TRexInputs attribute (member variable)
            for column in pd_obj.columns:
                setattr(model_obj, column, pd_obj[column])
        else:
            msg_err1 = "Inputs parameters do not have all required inputs. Please see API documentation.\n"
            keys_a = set(df.keys())
            keys_b = set(pd_obj.keys())
            msg_err2 = "Expected: " + str(df.columns.sort_values()) + "\n"
            msg_err3 = "Received: " + str(pd_obj.columns.sort_values()) + "\n"
            missing = [item for item in keys_a if item not in keys_b]
            msg_missing = "missing the following field(s):" + missing + "\n"
            extras = [item for item in keys_b if item not in keys_a]
            msg_extras = "the following extra field(s) were found:" + extras + "\n"
            raise ValueError(msg_err1 + msg_err2 + msg_err3 + msg_missing + msg_extras)

    def populate_outputs(self, model_obj):
        # Create temporary DataFrame where each column name is the same as TRexOutputs attributes
        """
        Create and return Model Output DataFrame where each column name is a model output parameter
        :param model: string, name of the model as referred to in class names (e.g. terrplant, sip, stir, etc..)
        :param model_obj: class instance, instance of the model class for which the
        :return:
        """
        # Import the model's output class (e.g. TerrplantOutputs) to create a DF to store the model outputs in
        mod_name = model_obj.name.lower() + '.' + model_obj.name.lower() + '_exe'
        module = importlib.import_module(mod_name)
        model_outputs = getattr(module, model_obj.name + "Outputs")
        model_outputs_obj = model_outputs()
        df = pd.DataFrame()
        for input_param in model_outputs_obj.__dict__:
            df[input_param] = getattr(self, input_param)
            setattr(model_obj, input_param, df[input_param])
        return df

    def fill_output_dataframe(self, model_obj):
        """ Combine all output properties into numpy pandas dataframe """
        for column in model_obj.pd_obj_out:
            try:
                model_obj.pd_obj_out[column] = getattr(model_obj, column)
            except:
                print("output dataframe error on " + column)

    @staticmethod
    def get_dict_rep(model_obj):
        """
        Convert DataFrames to dictionary, returning a tuple (inputs, outputs, exp_out)
        :param model_obj: model instance
        :return: (dict(input DataFrame), dict(outputs DataFrame), dict(expected outputs DataFrame))
        """
        try:
            return model_obj.pd_obj.to_dict(), model_obj.pd_obj_out.to_dict(), model_obj.pd_obj_exp.to_dict()
        except AttributeError:
            return model_obj.pd_obj.to_dict(), model_obj.pd_obj_out.to_dict(), {}


class ModelSharedInputs(object):
    def __init__(self):
        """
        Container for the shared model inputs amongst most models (e.g. version, chemical name, & PC Code)
        """
        super(ModelSharedInputs, self).__init__()
        self.version = pd.Series([], dtype="object")
        self.chemical_name = pd.Series([], dtype="object")
        self.pc_code = pd.Series([], dtype="object")
