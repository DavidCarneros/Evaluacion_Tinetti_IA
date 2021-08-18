import numpy as np
import pandas as pd
import pickle
from AI import constants as C

class GaitEvaluator:

    def __init__(self,input):

        self._lap1_model = None
        self._lap1_scaler = None

        self._lap2_model = None
        self._lap2_scaler = None

        self._lap3_model = None
        self._lap3_scaler = None

        self._lap4_model = None
        self._lap4_scaler = None

        self._dc_model = None
        self._dc_scaler = None

        self._pm_model = None
        self._pm_scaler = None

        self._dt_model = None
        self._dt_scaler = None

        self._load_models()

        self._input = self._parse_input(input)
        self.evaluation = None

    def predict_all(self):
        """

        :return:
        """

        predict_functions = [self._predict_lap1,self._predict_lap2,
                             self._predict_lap3,self._predict_lap4,
                             self._predict_dc, self._predict_pm,
                             self._predict_dt]

        predict_text = ["LAP1","LAP2","LAP3","LAP4","DC","PM","DT"]

        evaluation = []
        for i in range(0,len(predict_functions)):
            predict = {}
            result, prob = predict_functions[i]()
            predict[predict_text[i]] = {}
            predict[predict_text[i]]["result"] = result[0]
            predict[predict_text[i]]["prob"] = prob[0]
            evaluation.append(predict)

        self.evaluation = evaluation

    def _predict_lap1(self):
        X = self._lap1_scaler.transform(self._input)
        return self._lap1_model.predict(X), self._lap1_model.predict_proba(X)

    def _predict_lap2(self):
        X = self._lap2_scaler.transform(self._input)
        return self._lap2_model.predict(X), self._lap2_model.predict_proba(X)

    def _predict_lap3(self):
        X = self._lap3_scaler.transform(self._input)
        return self._lap3_model.predict(X), self._lap3_model.predict_proba(X)

    def _predict_lap4(self):
        X = self._lap4_scaler.transform(self._input)
        return self._lap4_model.predict(X), self._lap4_model.predict_proba(X)

    def _predict_pm(self):
        X = self._pm_scaler.transform(self._input)
        return self._pm_model.predict(X), self._pm_model.predict_proba(X)

    def _predict_dc(self):
        X = self._dc_scaler.transform(self._input)
        return self._dc_model.predict(X), self._dc_model.predict_proba(X)

    def _predict_dt(self):
        X = self._dt_scaler.transform(self._input)
        return self._dt_model.predict(X), self._dt_model.predict_proba(X)


    def _load_models(self):
        """

        :return:
        """
        with open(C.LAP1_MODELS_FIlENAME, 'rb') as handle:
            self._lap1_model = pickle.load(handle)

        with open(C.LAP1_SCALER_FILENAME, 'rb') as handle:
            self._lap1_scaler = pickle.load(handle)

        with open(C.LAP2_MODELS_FIlENAME, 'rb') as handle:
            self._lap2_model = pickle.load(handle)

        with open(C.LAP2_SCALER_FILENAME, 'rb') as handle:
            self._lap2_scaler = pickle.load(handle)

        with open(C.LAP3_MODELS_FIlENAME, 'rb') as handle:
            self._lap3_model = pickle.load(handle)

        with open(C.LAP3_SCALER_FILENAME, 'rb') as handle:
            self._lap3_scaler = pickle.load(handle)

        with open(C.LAP4_MODELS_FIlENAME, 'rb') as handle:
            self._lap4_model = pickle.load(handle)

        with open(C.LAP4_SCALER_FILENAME, 'rb') as handle:
            self._lap4_scaler = pickle.load(handle)

        with open(C.PM_MODELS_FIlENAME, 'rb') as handle:
            self._pm_model = pickle.load(handle)

        with open(C.PM_SCALER_FILENAME, 'rb') as handle:
            self._pm_scaler = pickle.load(handle)

        with open(C.DC_MODELS_FIlENAME, 'rb') as handle:
            self._dc_model = pickle.load(handle)

        with open(C.DC_SCALER_FILENAME, 'rb') as handle:
            self._dc_scaler = pickle.load(handle)

        with open(C.DT_MODELS_FIlENAME, 'rb') as handle:
            self._dt_model = pickle.load(handle)

        with open(C.DT_SCALER_FILENAME, 'rb') as handle:
            self._dt_scaler = pickle.load(handle)


    def _parse_input(self,input):
        """

        :param input:
        :return:
        """
        data = {}
        data["cadence"] = input["cadence"]
        data["velocity"] = input["velocity"]
        for leg in ["right", "left"]:
            data[f"stride_duration_{leg}"] = input[leg]["spaciotemporal"]["duration"]
            data[f"support_duration_{leg}"] = input[leg]["spaciotemporal"]["support_duration"]
            data[f"support_percentage_{leg}"] = input[leg]["spaciotemporal"]["support_percentage"]
            data[f"swing_duration_{leg}"] = input[leg]["spaciotemporal"]["swing_duration"]
            data[f"swing_percentage_{leg}"] = input[leg]["spaciotemporal"]["swing_percentage"]
            data[f"stride_length_{leg}"] = input[leg]["spaciotemporal"]["stride_length"]
            data[f"steps_length_{leg}"] = input[leg]["spaciotemporal"]["steps_length"]
            data[f"steps_duration_{leg}"] = input[leg]["spaciotemporal"]["steps_duration"]
            data[f"ankle_height_{leg}"] = input[leg]["spaciotemporal"]["ankle_height"]

        for leg in ["right", "left"]:
            for kinematics in C.KINEMATICS:
                min_val = []
                max_val = []
                mean_val = []
                mean_0 = []
                mean_10 = []
                mean_20 = []
                mean_30 = []
                mean_40 = []
                mean_50 = []
                mean_60 = []
                mean_70 = []
                mean_80 = []
                mean_90 = []
                mean_100 = []
                count = 0

                for stride in input[leg]["strides"]:
                    count += 1
                    min_val.append(np.array(stride["kinematics"][kinematics]).min())
                    max_val.append(np.array(stride["kinematics"][kinematics]).max())
                    mean_val.append(np.array(stride["kinematics"][kinematics]).mean())
                    mean_0.append(np.array(stride["kinematics"][kinematics])[0])
                    mean_10.append(np.array(stride["kinematics"][kinematics])[10])
                    mean_20.append(np.array(stride["kinematics"][kinematics])[20])
                    mean_30.append(np.array(stride["kinematics"][kinematics])[30])
                    mean_40.append(np.array(stride["kinematics"][kinematics])[40])
                    mean_50.append(np.array(stride["kinematics"][kinematics])[50])
                    mean_60.append(np.array(stride["kinematics"][kinematics])[60])
                    mean_70.append(np.array(stride["kinematics"][kinematics])[70])
                    mean_80.append(np.array(stride["kinematics"][kinematics])[80])
                    mean_90.append(np.array(stride["kinematics"][kinematics])[90])
                    mean_100.append(np.array(stride["kinematics"][kinematics])[100])

                data[f"{leg} {kinematics} MIN"] = np.array(min_val).min()
                data[f"{leg} {kinematics} MAX"] = np.array(min_val).max()
                data[f"{leg} {kinematics} MEAN"] = np.array(min_val).mean()
                data[f"{leg} {kinematics} 0%"] = np.array(mean_0).mean()
                data[f"{leg} {kinematics} 10%"] = np.array(mean_10).mean()
                data[f"{leg} {kinematics} 20%"] = np.array(mean_20).mean()
                data[f"{leg} {kinematics} 30%"] = np.array(mean_30).mean()
                data[f"{leg} {kinematics} 40%"] = np.array(mean_40).mean()
                data[f"{leg} {kinematics} 50%"] = np.array(mean_50).mean()
                data[f"{leg} {kinematics} 60%"] = np.array(mean_60).mean()
                data[f"{leg} {kinematics} 70%"] = np.array(mean_70).mean()
                data[f"{leg} {kinematics} 80%"] = np.array(mean_80).mean()
                data[f"{leg} {kinematics} 90%"] = np.array(mean_90).mean()
                data[f"{leg} {kinematics} 100%"] = np.array(mean_100).mean()

        return pd.DataFrame([data])