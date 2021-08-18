import argparse
import numpy as np
import pandas as pd
from InputProcessing import events,gaitParameters
from AI import evaluator

def run(filename, name="No name"):

    segment_position = pd.read_excel(filename, sheet_name="Segment Position", engine="openpyxl")
    joints_angles = pd.read_excel(filename, sheet_name="Joint Angles ZXY",engine="openpyxl")
    center_of_mass = pd.read_excel(filename, sheet_name="Center of Mass", engine="openpyxl")

    events_parser = events.Events(segment_position)
    events_parser.get_events()

    gait_parser = gaitParameters.GaitParameters(joints_angles, segment_position, center_of_mass, events_parser.events)
    gait_parser.get_params()

    gait_evaluator = evaluator.GaitEvaluator(gait_parser.gait)
    gait_evaluator.predict_all()

    print(gait_evaluator.evaluation)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Gait Evaluation")
    parser.add_argument("-f", "--file", type=str, help="Xsens export file", required=True)
    parser.add_argument("-n", "--name", type=str, help="Patient name", default="No name", required=False)
    args = parser.parse_args()

    filename = args.file
    name = args.name

    run(filename, name)
