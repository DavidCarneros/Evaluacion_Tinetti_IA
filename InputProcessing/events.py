import numpy as np
import pandas as pd
from InputProcessing.helpers import savitzky_golay,peak_detection
import InputProcessing.constants as C

class Events:

    def __init__(self, data, drop_turns=False):

        pelvis_x, left_foot_x, right_foot_x, \
            left_toe_x, right_toe_x = self._getDataFromRawDataframe(data)

        self._pelvis_x = pelvis_x
        self._left_foot_x = left_foot_x
        self._left_toe_x = left_toe_x
        self._right_foot_x = right_foot_x
        self._right_toe_x = right_toe_x

        self._sacro_x = None
        self.events = None
        self._drop_turns = drop_turns

    def get_events(self):
        """

        :return:
        """

        self._sacro_x = savitzky_golay(self._pelvis_x, C.WINDOW_SIZE, C.ORDER)

        turns = self._get_and_filter_turns(threshold=C.TURNS_THRESHOLD)
        self._process_turns(turns)

        # Get Heel Strike Events
        X_HS_l = self._left_foot_x - self._sacro_x
        X_HS_r = self._right_foot_x - self._sacro_x

        frames_HS_l = self._get_events_frames(X_HS_l, turns, "HS", C.PEAK_SENSIBILITY, self._drop_turns)
        frames_HS_r = self._get_events_frames(X_HS_r, turns, "HS", C.PEAK_SENSIBILITY, self._drop_turns)

        # Get Toe Off Events
        X_TO_l = self._left_toe_x - self._sacro_x
        X_TO_r = self._right_toe_x - self._sacro_x

        frames_TO_l = self._get_events_frames(X_TO_l, turns, "TO", C.PEAK_SENSIBILITY,self._drop_turns)
        frames_TO_r = self._get_events_frames(X_TO_r, turns, "TO", C.PEAK_SENSIBILITY, self._drop_turns)

        events = []
        for frame in frames_HS_l:
            event = {}
            event["event"] = "EVENT_LEFT_FOOT_INITIAL_CONTACT"
            event["frame"] = frame
            event["time"] = frame/100
            events.append(event)
            #events[frame] = "EVENT_LEFT_FOOT_INITIAL_CONTACT"

        for frame in frames_HS_r:
            #events[frame] = "EVENT_RIGHT_FOOT_INITIAL_CONTACT"
            event = {}
            event["event"] = "EVENT_RIGHT_FOOT_INITIAL_CONTACT"
            event["frame"] = frame
            event["time"] = frame / 100
            events.append(event)

        for frame in frames_TO_r:
            #events[frame] = "EVENT_RIGHT_FOOT_TOE_OFF"
            event = {}
            event["event"] = "EVENT_RIGHT_FOOT_TOE_OFF"
            event["frame"] = frame
            event["time"] = frame / 100
            events.append(event)

        for frame in frames_TO_l:
            #events[frame] = "EVENT_LEFT_FOOT_TOE_OFF"
            event = {}
            event["event"] = "EVENT_LEFT_FOOT_TOE_OFF"
            event["frame"] = frame
            event["time"] = frame / 100
            events.append(event)


        # sort and save
        events_sort = sorted(events, key=lambda k: k['frame'])

        ## Test
        events = {}
        for frame in frames_HS_l:
            events[frame] = "EVENT_LEFT_FOOT_INITIAL_CONTACT"

        for frame in frames_HS_r:
            events[frame] = "EVENT_RIGHT_FOOT_INITIAL_CONTACT"

        for frame in frames_TO_r:
            events[frame] = "EVENT_RIGHT_FOOT_TOE_OFF"

        for frame in frames_TO_l:
            events[frame] = "EVENT_LEFT_FOOT_TOE_OFF"

        frames = list(events.keys())
        frames.sort()

        with open("test_events.txt", 'w') as f:
            for i, frame in enumerate(frames):
                f.write(f"{i}\t{events[frame]}\t{frame}\t{frame / 100}\n")

        ####

        self.events = pd.DataFrame(events_sort)

    def _get_events_frames(self,data,turns, event="HS", s=20, drop_turns=False):
        """

        :param data:
        :param turns:
        :param event:
        :param s:
        :param drop_turns:
        :return:
        """
        frames = []

        max = True if event == "HS" else False
        peaks = peak_detection(data,s,max)

        for peak in peaks:
            not_valid = False
            if drop_turns:
                for cd in turns:
                    not_valid = not_valid | ((cd - 50) < peak and (cd + 50) > peak)
            for actualPeaks in frames:
                not_valid = not_valid | ((peak - actualPeaks) < 50)
            if not not_valid:
                frames.append(peak)

        return frames

    def _process_turns(self,turns):
        """

        :param turns:
        :return:
        """
        if len(turns) != 0:
            if len(turns) == 1:
                self._sacro_x[turns[0]:] *= -1
                self._left_foot_x[turns[0]:] *= -1
                self._left_toe_x[turns[0]:] *= -1
                self._right_foot_x[turns[0]:] *= -1
                self._right_toe_x[turns[0]:] *= -1
            else:
                for i in range(0, len(turns)//2):
                    j = i * 2
                    k = (i * 2) + 1
                    self._sacro_x[turns[j]:turns[k]] *= -1
                    self._left_foot_x[turns[j]:turns[k]] *= -1
                    self._left_toe_x[turns[j]:turns[k]] *= -1
                    self._right_foot_x[turns[j]:turns[k]] *= -1
                    self._right_toe_x[turns[j]:turns[k]] *= -1

    def _get_and_filter_turns(self, threshold=0.9):
        """

        :param sacro_x:
        :param threshold:
        :return:
        """

        kneedle_max = peak_detection(self._sacro_x, s=C.PEAK_SENSIBILITY,max=True)
        kneedle_min = peak_detection(self._sacro_x, s=C.PEAK_SENSIBILITY,max=False)

        turns_not_processed = (list(kneedle_max) + list(kneedle_min))
        turns_not_processed.sort()

        turns_filter = []
        for turn in turns_not_processed:
            if turn > 100:
                turns_filter.append(turn)

        turns = []
        for i in range(0, len(turns_filter)):
            if i == 0:
                back = True
            else:
                back = abs(self._sacro_x[turns_filter[i-1]] - self._sacro_x[turns_filter[i]]) > threshold
            if i == (len(turns_filter)-1):
                forward = True
            else:
                forward = abs(self._sacro_x[turns_filter[i + 1]] - self._sacro_x[turns_filter[i]]) > threshold

            if back and forward:
                turns.append(turns_filter[i])

        return turns

    def _getDataFromRawDataframe(self,data):
        """

        :param data:
        :return:
        """
        return (
            np.array(data["Pelvis x"].tolist()),
            np.array(data["Left Foot x"].tolist()),
            np.array(data["Right Foot x"].tolist()),
            np.array(data["Left Toe x"].tolist()),
            np.array(data["Right Toe x"].tolist())
        )


