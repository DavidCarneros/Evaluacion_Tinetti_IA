import numpy as np
import pandas as pd
from InputProcessing.helpers import savitzky_golay,peak_detection
import InputProcessing.constants as C

class GaitParameters:

    def __init__(self,jointAngles, segmentPosition, centerOfMass, events):
        """
        
        :param jointAngles:
        :param segmentPosition:
        :param centerOfMass:
        :param events:
        """
        self._events = events

        self._data_angles = jointAngles
        self._center_of_mass = centerOfMass

        self._sacro_x = np.array(segmentPosition["Pelvis x"].tolist())
        self._right_foot_x = np.array(segmentPosition["Right Foot x"].tolist())
        self._right_foot_y = np.array(segmentPosition["Right Foot y"].tolist())
        self._right_foot_z = np.array(segmentPosition["Right Foot z"].tolist())
        self._left_foot_x = np.array(segmentPosition["Left Foot x"].tolist())
        self._left_foot_y = np.array(segmentPosition["Left Foot y"].tolist())
        self._left_foot_z = np.array(segmentPosition["Left Foot z"].tolist())

        self._orientation = None

        self.gait = None

    def get_params(self):
        """

        :return:
        """
        self._orientation = savitzky_golay(self._sacro_x, C.WINDOW_SIZE,C.ORDER)
        turns = self._get_and_filter_turns(threshold=C.TURNS_THRESHOLD)

        right = self._get_strides("Right",turns)
        left = self._get_strides("Left",turns)

        local_spatiotemporal = self._get_general_spatiotemporal(turns)

        strides = {}
        strides["steps"] = local_spatiotemporal["steps"]
        strides["cadence"] = local_spatiotemporal["cadence"]
        strides["velocity"] = 0
        strides["right"] = {}
        strides["right"]["spaciotemporal"] = self._get_global_spatiotemporal(right)
        strides["right"]["spaciotemporal"]["steps"] = local_spatiotemporal["steps_right"]
        strides["right"]["spaciotemporal"]["steps_length"] = local_spatiotemporal["steps_length_right"]
        strides["right"]["spaciotemporal"]["steps_duration"] = local_spatiotemporal["steps_duration_right"]
        strides["right"]["spaciotemporal"]["ankle_height"] = (max(self._right_foot_z) - min(self._right_foot_z)) * 1000
        strides["total_right"] = len(right)
        strides["right"]["strides"] = right
        strides["left"] = {}
        strides["left"]["spaciotemporal"] = self._get_global_spatiotemporal(left)
        strides["left"]["spaciotemporal"]["steps"] = local_spatiotemporal["steps_left"]
        strides["left"]["spaciotemporal"]["steps_length"] = local_spatiotemporal["steps_length_left"]
        strides["left"]["spaciotemporal"]["steps_duration"] = local_spatiotemporal["steps_duration_left"]
        strides["left"]["spaciotemporal"]["ankle_height"] = (max(self._left_foot_z) - min(self._right_foot_z)) * 1000
        strides["total_left"] = len(left)
        strides["left"]["strides"] = left
        strides["velocity"] = ((((strides["left"]["spaciotemporal"]["stride_length"] +
                                  strides["right"]["spaciotemporal"]["stride_length"]) / 2) / 1000)
                               * strides["cadence"] / 120)

        self.gait = strides

    def _get_global_spatiotemporal(self,strides):
        """

        :param strides:
        :return:
        """
        spatiotemporal = {}

        duration = 0
        support_duration = 0
        swing_duration = 0
        stride_length = 0

        for stride in strides:
            duration += stride["spatiotemporal"]["duration"]
            support_duration += stride["spatiotemporal"]["support_duration"]
            swing_duration += stride["spatiotemporal"]["swing_duration"]
            stride_length += stride["spatiotemporal"]["stride_length"]

        spatiotemporal["duration"] = duration / len(strides)
        spatiotemporal["support_duration"] = support_duration / len(strides)
        spatiotemporal["support_percentage"] = (spatiotemporal["support_duration"] * 100) / spatiotemporal["duration"]
        spatiotemporal["swing_duration"] = swing_duration / len(strides)
        spatiotemporal["swing_percentage"] = (spatiotemporal["swing_duration"] * 100) / spatiotemporal["duration"]
        spatiotemporal["stride_length"] = stride_length / len(strides)

        return spatiotemporal

    def _get_general_spatiotemporal(self, turns, turn_offset=30):
        """

        :param turns:
        :param turn_offset:
        :return:
        """
        legs = ["Right","Left"]

        total_frames = []
        support_width = 0

        result = self._define_result_dict()
        for leg in legs:

            if leg == "Right":
                ICs = self._events[self._events["event"] == "EVENT_RIGHT_FOOT_INITIAL_CONTACT"]
            else:
                ICs = self._events[self._events["event"] == "EVENT_LEFT_FOOT_INITIAL_CONTACT"]

            strides_auxiliar = []
            for i in range(0, len(ICs) - 1):
                IC_init = ICs.iloc[i]["frame"]
                IC_end = ICs.iloc[i + 1]["frame"]

                is_turn = False
                for turn in turns:
                    is_turn = is_turn | ((turn >= (IC_init - turn_offset)) and (turn <= (IC_end + turn_offset)))

                is_valid = self._check_valid_stride(leg, IC_init, IC_end)

                strides_auxiliar.append({
                    "IC_init": IC_init,
                    "IC_end": IC_end,
                    "diference": IC_end - IC_init,
                    "isTurn": is_turn,
                    "isValid": is_valid
                })

            steps_leg_count = 0
            steps_leg_duration = 0
            steps_leg_length = 0

            for stride in strides_auxiliar:

                if stride["isTurn"] == False and stride["isValid"] == True:
                    step_IC_init = stride["IC_init"]
                    IC_event_search = "EVENT_LEFT_FOOT_INITIAL_CONTACT" if leg == "Right" else "EVENT_RIGHT_FOOT_INITIAL_CONTACT"
                    step_IC_end = \
                        self._get_event_between_frames(stride["IC_init"], stride["IC_end"], IC_event_search)

                    steps_leg_count += 1
                    total_frames.append(stride["IC_end"])
                    total_frames.append(stride["IC_init"])
                    # total_frames += stride["IC_end"] - stride["IC_init"] + 1

                    if leg == "Right":
                        foot1_x = self._right_foot_x
                        foot2_x = self._left_foot_x
                        foot1_y = self._right_foot_y
                        foot2_y = self._left_foot_y
                    else:
                        foot2_x = self._right_foot_x
                        foot1_x = self._left_foot_x
                        foot2_y = self._right_foot_y
                        foot1_y = self._left_foot_y

                    steps_leg_length += self._distance_foot(step_IC_init, step_IC_end, foot1_x, foot2_x) * 1000
                    steps_leg_duration += (float(step_IC_end) - float(step_IC_init)) / 100
                    support_width += self._distance_width(step_IC_init, step_IC_end, foot1_y, foot2_y)

            result[f"steps_{leg.lower()}"] = steps_leg_count
            result[f"steps_length_{leg.lower()}"] = steps_leg_length / steps_leg_count
            result[f"steps_duration_{leg.lower()}"] = steps_leg_duration / steps_leg_count
            result[f"steps_{leg.lower()}"] = steps_leg_count

        total_frames.sort()
        total_frames_count = 0
        for i in range(0, len(total_frames) - 1):
            total_frames_count += total_frames[i + 1] - total_frames[i] + 1

        result["steps"] = result["steps_right"] + result["steps_left"]
        result["frames"] = total_frames_count
        result["cadence"] = result["steps"] / (total_frames_count / 100) * 60
        result["support_width"] = support_width / result["steps"] * 1000

        return result

    def _get_strides(self,leg,turns,turn_offset=30):
        """

        :param leg:
        :param turns:
        :param turn_offset:
        :return:
        """
        strides_auxiliar = []

        if leg == "Right":
            ICs = self._events[self._events["event"] == "EVENT_RIGHT_FOOT_INITIAL_CONTACT"]
            foot_position = self._right_foot_x
        else:
            ICs = self._events[self._events["event"] == "EVENT_LEFT_FOOT_INITIAL_CONTACT"]
            foot_position = self._left_foot_x

        for i in range(0, len(ICs) - 1):
            IC_init = ICs.iloc[i]["frame"]
            IC_end = ICs.iloc[i + 1]["frame"]

            is_turn = False
            for turn in turns:
                is_turn = is_turn | ((turn >= (IC_init - turn_offset)) and (turn <= (IC_end + turn_offset)))

            if leg == "Right":
                is_valid = self._check_valid_stride(leg, IC_init, IC_end)
            else:
                is_valid = self._check_valid_stride(leg, IC_init, IC_end)

            strides_auxiliar.append({
                "IC_init": IC_init,
                "IC_end": IC_end,
                "diference": IC_end - IC_init,
                "isTurn": is_turn,
                "isValid": is_valid
            })

        strides = []
        index = 0
        for stride_aux in strides_auxiliar:
            if stride_aux["isTurn"] == False and stride_aux["isValid"] == True:
                index += 1
                TO_event_text = "EVENT_RIGHT_FOOT_TOE_OFF" if leg == "Right" else "EVENT_LEFT_FOOT_TOE_OFF"
                IC_init = stride_aux["IC_init"]
                IC_end = stride_aux["IC_end"]
                TO_event = self._get_event_between_frames(IC_init, IC_end, TO_event_text)

                stride = {"index": index, "spatiotemporal": {}, "kinematics": {}}
                stride_spatiotemporal = {}
                stride_spatiotemporal["duration"] = float(int(IC_end) - int(IC_init)) / 100
                stride_spatiotemporal["init_frame"] = int(IC_init)
                stride_spatiotemporal["end_frame"] = int(IC_end)
                stride_spatiotemporal["support_duration"] = float(int(TO_event) - int(IC_init)) / 100
                stride_spatiotemporal["support_percentage"] = (stride_spatiotemporal["support_duration"] * 100) / \
                                                              stride_spatiotemporal["duration"]
                stride_spatiotemporal["swing_duration"] = float(int(IC_end) - int(TO_event)) / 100
                stride_spatiotemporal["swing_percentage"] = (stride_spatiotemporal["swing_duration"] * 100) / \
                                                            stride_spatiotemporal["duration"]
                stride_spatiotemporal["stride_length"] = self._calculate_distance(IC_init, IC_end, foot_position)
                stride["spatiotemporal"] = stride_spatiotemporal

                for kine in C.KINEMATICS_PARAMETERS:
                    kine_text = f"{leg} {kine}"
                    kine_data = self._data_angles[kine_text]

                    save_values_aux, save_values_count = self._scale_kinematic_stride(kine_text, IC_init, IC_end)
                    try:
                        stride_normalized = [save_values_aux[k] / save_values_count[k] for k in
                                             range(0, len(save_values_aux))]
                        stride["kinematics"][kine] = stride_normalized
                    except:
                        pass

                kine_text = "CoM y"
                kine_data = self._center_of_mass[kine_text]
                save_values_aux, save_values_count = self._scale_kinematic_stride(kine_text, IC_init, IC_end)
                try:
                    stride_normalized = [save_values_aux[k] / save_values_count[k] for k in
                                         range(0, len(save_values_aux))]
                    stride["kinematics"]["CoM y"] = stride_normalized
                except:
                    pass

                strides.append(stride)

        return strides

    def _scale_kinematic_stride(self, kine_text, IC_init, IC_end):
        """

        :param kine_text:
        :param IC_init:
        :param IC_end:
        :return:
        """
        stride_data = self._data_angles.iloc[IC_init:IC_end].reset_index()
        min_frame = min(stride_data["index"])
        max_frame = max(stride_data["index"])
        stride_data["n_index"] = stride_data["index"] - min_frame
        max_n = max(stride_data["n_index"])
        stride_data["per"] = (stride_data["n_index"] * 100) / max_n

        save_values_aux = [0] * 101
        save_values_count = [0] * 101

        for j in stride_data.index:
            per = stride_data["per"].iloc[j]
            per_int = int(per)
            value = stride_data[kine_text].iloc[j]
            save_values_aux[per_int] += value
            save_values_count[per_int] += 1

        if 0 in save_values_count:
            for z in range(0, len(save_values_count)):
                if save_values_count[z] == 0:
                    save_values_aux[z] = (save_values_aux[z - 1] + save_values_aux[z + 1]) / 2
                    save_values_count[z] += 1

        return save_values_aux, save_values_count

    def _calculate_distance(self, fr1, fr2, orientation):
        """

        :param fr1:
        :param fr2:
        :param orientation:
        :return:
        """
        d1 = abs(orientation[fr1])
        d2 = abs(orientation[fr2])
        return abs(d1 - d2) * 1000 if d1 > d2 else abs(d2 - d1) * 1000

    def _distance_foot(self, fr1, fr2, foot1, foot2):
        """

        :param fr1:
        :param fr2:
        :param foot1:
        :param foot2:
        :return:
        """
        return abs(foot2[fr2] - foot1[fr1]) if foot2[fr2] > foot1[fr1] else abs(foot1[fr1] - foot2[fr2])

    def _distance_width(self, fr1, fr2, foot1, foot2):
        """

        :param fr1:
        :param fr2:
        :param foot1:
        :param foot2:
        :return:
        """
        return abs(foot2[fr2] - foot1[fr1]) if foot2[fr2] > foot1[fr1] else abs(foot1[fr1] - foot2[fr2])

    def _get_event_between_frames(self,init, end, event):
        """

        :param init:
        :param end:
        :param event:
        :return:
        """
        events_between = self._events[self._events["frame"] > init].reset_index()
        events_between = events_between[events_between["frame"] < end].reset_index()

        return events_between[events_between["event"] == event]["frame"].tolist()[0]

    def _check_valid_stride(self,leg,IC_init, IC_end):
        """

        :param leg:
        :param IC_init:
        :param IC_end:
        :return:
        """
        events_between = self._events[self._events["frame"] > IC_init].reset_index()
        events_between = events_between[events_between["frame"] < IC_end].reset_index()

        if leg == "Right":
            return self._check_valid_stride_right(events_between)
        else:
            return self._check_valid_stride_left(events_between)


    def _check_valid_stride_right(self, events_between):
        """

        :param events_between:
        :return:
        """
        is_left_to_ok = len(events_between[events_between["event"] == "EVENT_LEFT_FOOT_TOE_OFF"]) == 1
        is_left_hs_ok = len(events_between[events_between["event"] == "EVENT_LEFT_FOOT_INITIAL_CONTACT"]) == 1
        is_right_to_ok = len(events_between[events_between["event"] == "EVENT_RIGHT_FOOT_TOE_OFF"]) == 1

        return is_left_hs_ok and is_left_to_ok and is_right_to_ok

    def _check_valid_stride_left(self, events_between):
        """

        :param events_between:
        :return:
        """
        isLeftTO_OK = len(events_between[events_between["event"] == "EVENT_LEFT_FOOT_TOE_OFF"]) == 1
        isRightHS_OK = len(events_between[events_between["event"] == "EVENT_RIGHT_FOOT_INITIAL_CONTACT"]) == 1
        isRightTO_OK = len(events_between[events_between["event"] == "EVENT_RIGHT_FOOT_TOE_OFF"]) == 1

    def _get_and_filter_turns(self, threshold=0.9):
        """

        :param sacro_x:
        :param threshold:
        :return:
        """
        turns = []

        kneedle_max = peak_detection(self._sacro_x, s=C.PEAK_SENSIBILITY, max=True)
        kneedle_min = peak_detection(self._sacro_x, s=C.PEAK_SENSIBILITY, max=False)

        turns_not_processed = (list(kneedle_max) + list(kneedle_min))
        turns_not_processed.sort()

        turns_filter = []
        for turn in turns_not_processed:
            if turn > 100:
                turns_filter.append(turn)
        for i in range(0, len(turns_filter)):
            if i == 0:
                back = True
            else:
                back = abs(self._sacro_x[turns_filter[i - 1]] - self._sacro_x[turns_filter[i]]) > threshold
            if i == (len(turns_filter) - 1):
                forward = True
            else:
                forward = abs(self._sacro_x[turns_filter[i + 1]] - self._sacro_x[turns_filter[i]]) > threshold

            if back and forward:
                turns.append(turns_filter[i])

        return turns

    def _define_result_dict(self):
        """

        :return:
        """
        return {
            "steps": None,
            'frames': None,
            'cadence': None,
            'steps_right': None,
            'steps_length_right': None,
            'steps_duration_right': None,
            'steps_left': None,
            'steps_length_left': None,
            'steps_duration_left': None,
            'support_width': None
        }