import argparse
import numpy as np
import pandas as pd
from src.InputProcessing import events,gaitParameters
from src.AI import evaluator
from src.ReportGenerator import report

OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

def run(filename, name, surname, age, report_bool, output):

    print(f"{OKBLUE}Evaluación de la marcha{ENDC}")
    print(f"{WARNING}Este proceso puede durar varios minutos{ENDC}")

    segment_position = pd.read_excel(filename, sheet_name="Segment Position", engine="openpyxl")
    joints_angles = pd.read_excel(filename, sheet_name="Joint Angles ZXY",engine="openpyxl")
    center_of_mass = pd.read_excel(filename, sheet_name="Center of Mass", engine="openpyxl")

    events_parser = events.Events(segment_position)
    events_parser.get_events()

    gait_parser = gaitParameters.GaitParameters(joints_angles, segment_position, center_of_mass, events_parser.events)
    gait_parser.get_params()

    gait_evaluator = evaluator.GaitEvaluator(gait_parser.gait)
    gait_evaluator.predict_all()

    if report_bool:
        report_generator = report.Report(name,surname,age,output,gait_parser.gait,gait_evaluator.evaluation)
        report_generator.generate_report()

    print(pd.DataFrame(gait_evaluator.evaluation).T)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluacion de la marcha")
    parser.add_argument("-f", "--file", type=str, help="archivo exportado de xsens de la grabación", required=True)
    parser.add_argument("-n", "--name", type=str, help="nombre del paciente", default="No name", required=False)
    parser.add_argument("-s", "--surname",type=str, help="apellido del paciente",default="No surname",required=False)
    parser.add_argument("-a", "--age",type=str, help="edad del paciente", default="No age", required=False)
    parser.add_argument("-r", "--report",type=bool, help="generar informe", default=True, required=False)
    parser.add_argument("-o", "--output",type=str, help="nombre del archivo generado",default="report",required=False)
    args = parser.parse_args()

    filename = args.file
    name = args.name
    surname = args.surname
    age = args.age
    report_bool = args.report
    output = args.output

    run(filename, name, surname, age, report_bool,output)
