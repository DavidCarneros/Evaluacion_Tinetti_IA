from docxtpl import DocxTemplate, InlineImage, RichText
import matplotlib.pyplot as plt
from docx.shared import Cm
import seaborn as sns
import pandas as pd
import numpy as np
import io
import ReportGenerator.constants as C
from datetime import date
import base64

class Report:

    def __init__(self, name, surname, age, output, gait, evaluation):

        self._template = DocxTemplate(C.TEMPLATE_PATH)
        self._gait = gait
        self._name = name
        self._surname = surname
        self._age = age
        self._output = output
        self._evaluation = evaluation
        self._normal_kinematics = pd.read_hdf(C.NORMAL_KINEMATICS_PATH)

    def generate_report(self):

        print(f"Generando eventos de la marcha ", end="")

        context = {}
        context["name"] = self._name
        context["surname"] = self._surname
        context["age"] = self._age
        context["date"] = date.today().strftime("%d/%m/%Y")
        self._print_process()

        ## Spatiotemporal
        context["n_str_r"] = self._gait["total_right"]
        context["n_str_l"] = self._gait["total_left"]
        context["n_ste_r"] = self._gait["right"]["spaciotemporal"]["steps"]
        context["n_ste_l"] = self._gait["left"]["spaciotemporal"]["steps"]
        self._print_process()

        context["pad_d"] = round(self._gait["right"]["spaciotemporal"]["support_duration"],2)
        context["pad_p"] = round(self._gait["right"]["spaciotemporal"]["support_percentage"],2)
        context["pbd_d"] = round(self._gait["right"]["spaciotemporal"]["swing_duration"],2)
        context["pbd_p"] = round(self._gait["right"]["spaciotemporal"]["swing_percentage"],2)
        context["pai_d"] = round(self._gait["left"]["spaciotemporal"]["support_duration"], 2)
        context["pai_p"] = round(self._gait["left"]["spaciotemporal"]["support_percentage"], 2)
        context["pbi_d"] = round(self._gait["left"]["spaciotemporal"]["swing_duration"], 2)
        context["pbi_p"] = round(self._gait["left"]["spaciotemporal"]["swing_percentage"], 2)
        self._print_process()

        context["max_tal_r"] = round(self._gait["right"]["spaciotemporal"]["ankle_height"],2)
        context["max_tal_l"] = round(self._gait["left"]["spaciotemporal"]["ankle_height"],2)
        context["cadence"] = round(self._gait["cadence"],2)
        context["velocity"] = round(self._gait["velocity"],2)
        context["width"] = round(self._gait["support_width"],2)
        self._print_process()

        input = {"Der": round(self._gait["right"]["spaciotemporal"]["duration"], 2),
                 "Med": 0,
                 "Izq": round(self._gait["left"]["spaciotemporal"]["duration"], 2)}
        input["Med"] = round((input["Der"] + input["Izq"]) / 2, 2)
        spatiotemporal_fig_3 = self._create_img(13, self._spatiotemporal_figure_duration(input))
        context['stride_duration_1'] = spatiotemporal_fig_3
        self._print_process()

        input = {"Der": round(self._gait["right"]["spaciotemporal"]["stride_length"],2),
                 "Med":0,
                 "Izq": round(self._gait["left"]["spaciotemporal"]["stride_length"],2)}
        input["Med"] = round((input["Der"]+input["Izq"])/2,2)
        spatiotemporal_fig_1 = self._create_img(13,self._spatiotemporal_figure_length(input))
        context['stride_length'] =  spatiotemporal_fig_1
        self._print_process()

        input = {"Der": round(self._gait["right"]["spaciotemporal"]["steps_length"], 2),
                 "Med": 0,
                 "Izq": round(self._gait["left"]["spaciotemporal"]["steps_length"], 2)}
        input["Med"] = round((input["Der"] + input["Izq"]) / 2, 2)
        spatiotemporal_fig_2 = self._create_img(13, self._spatiotemporal_figure_length(input))
        context['steps_length'] =  spatiotemporal_fig_2
        self._print_process()

        input = {"Der": round(self._gait["right"]["spaciotemporal"]["steps_duration"], 3),
                 "Med": 0,
                 "Izq": round(self._gait["left"]["spaciotemporal"]["steps_duration"], 3)}
        input["Med"] = round((input["Der"] + input["Izq"]) / 2, 3)
        spatiotemporal_fig_4 = self._create_img(13, self._spatiotemporal_figure_duration(input))
        context['steps_duration'] =  spatiotemporal_fig_4
        self._print_process()

        ## Kinematics

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Abduction/Adduction","right")
        context["hip_abd_adu_der_min"] = round(np.array(data_min).min(),2)
        context["hip_abd_adu_der_max"] = round(np.array(data_max).max(),2)
        context["hip_abd_adu_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_abd_adu_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,kine_text="Hip Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Abduction/Adduction", "left")
        context["hip_abd_adu_izq_min"] = round(np.array(data_min).min(), 2)
        context["hip_abd_adu_izq_max"] = round(np.array(data_max).max(), 2)
        context["hip_abd_adu_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_abd_adu_izq"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Hip Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Flexion/Extension", "right")
        context["hip_flex_ext_der_min"] = round(np.array(data_min).min(), 2)
        context["hip_flex_ext_der_max"] = round(np.array(data_max).max(), 2)
        context["hip_flex_ext_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_flex_ext_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Hip Flexion/Extension"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Flexion/Extension", "left")
        context["hip_flex_ext_izq_min"] = round(np.array(data_min).min(), 2)
        context["hip_flex_ext_izq_max"] = round(np.array(data_max).max(), 2)
        context["hip_flex_ext_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_flex_ext_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Hip Flexion/Extension"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Internal/External Rotation", "right")
        context["hip_rot_der_min"] = round(np.array(data_min).min(), 2)
        context["hip_rot_der_max"] = round(np.array(data_max).max(), 2)
        context["hip_rot_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_rot_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Hip Internal/External Rotation"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Hip Internal/External Rotation", "left")
        context["hip_rot_izq_min"] = round(np.array(data_min).min(), 2)
        context["hip_rot_izq_max"] = round(np.array(data_max).max(), 2)
        context["hip_rot_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["hip_rot_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Hip Internal/External Rotation"))
        self._print_process()

        ## knee

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Abduction/Adduction", "right")
        context["knee_abd_adu_der_min"] = round(np.array(data_min).min(), 2)
        context["knee_abd_adu_der_max"] = round(np.array(data_max).max(), 2)
        context["knee_abd_adu_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_abd_adu_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Knee Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Abduction/Adduction", "left")
        context["knee_abd_adu_izq_min"] = round(np.array(data_min).min(), 2)
        context["knee_abd_adu_izq_max"] = round(np.array(data_max).max(), 2)
        context["knee_abd_adu_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_abd_adu_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Knee Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Flexion/Extension", "right")
        context["knee_flex_ext_der_min"] = round(np.array(data_min).min(), 2)
        context["knee_flex_ext_der_max"] = round(np.array(data_max).max(), 2)
        context["knee_flex_ext_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_flex_ext_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Knee Flexion/Extension"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Flexion/Extension", "left")
        context["knee_flex_ext_izq_min"] = round(np.array(data_min).min(), 2)
        context["knee_flex_ext_izq_max"] = round(np.array(data_max).max(), 2)
        context["knee_flex_ext_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_flex_ext_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Knee Flexion/Extension"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Internal/External Rotation", "right")
        context["knee_rot_der_min"] = round(np.array(data_min).min(), 2)
        context["knee_rot_der_max"] = round(np.array(data_max).max(), 2)
        context["knee_rot_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_rot_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Knee Internal/External Rotation"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Knee Internal/External Rotation", "left")
        context["knee_rot_izq_min"] = round(np.array(data_min).min(), 2)
        context["knee_rot_izq_max"] = round(np.array(data_max).max(), 2)
        context["knee_rot_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["knee_rot_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Knee Internal/External Rotation"))
        self._print_process()

        ## ankle
        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Abduction/Adduction", "right")
        context["ankle_abd_adu_der_min"] = round(np.array(data_min).min(), 2)
        context["ankle_abd_adu_der_max"] = round(np.array(data_max).max(), 2)
        context["ankle_abd_adu_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_abd_adu_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Ankle Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Abduction/Adduction", "left")
        context["ankle_abd_adu_izq_min"] = round(np.array(data_min).min(), 2)
        context["ankle_abd_adu_izq_max"] = round(np.array(data_max).max(), 2)
        context["ankle_abd_adu_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_abd_adu_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Ankle Abduction/Adduction"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Dorsiflexion/Plantarflexion", "right")
        context["ankle_flex_ext_der_min"] = round(np.array(data_min).min(), 2)
        context["ankle_flex_ext_der_max"] = round(np.array(data_max).max(), 2)
        context["ankle_flex_ext_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_flex_ext_der"] = self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Ankle Dorsiflexion/Plantarflexion"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Dorsiflexion/Plantarflexion", "left")
        context["ankle_flex_ext_izq_min"] = round(np.array(data_min).min(), 2)
        context["ankle_flex_ext_izq_max"] = round(np.array(data_max).max(), 2)
        context["ankle_flex_ext_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_flex_ext_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Ankle Dorsiflexion/Plantarflexion"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Internal/External Rotation", "right")
        context["ankle_rot_der_min"] = round(np.array(data_min).min(), 2)
        context["ankle_rot_der_max"] = round(np.array(data_max).max(), 2)
        context["ankle_rot_der_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_rot_der"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="right",kine_text="Ankle Internal/External Rotation"))
        self._print_process()

        data_kine, data_max, data_min = self._get_kinematics_parameters("Ankle Internal/External Rotation", "left")
        context["ankle_rot_izq_min"] = round(np.array(data_min).min(), 2)
        context["ankle_rot_izq_max"] = round(np.array(data_max).max(), 2)
        context["ankle_rot_izq_range"] = self._get_joint_range(np.array(data_max).max(),np.array(data_min).min())
        context["ankle_rot_izq"] =  self._create_img(9,self._generate_kinematic_graph(data_kine,leg="left",kine_text="Ankle Internal/External Rotation"))
        self._print_process()

        ## Tinetti

        cp0 = f"0 ({round(self._evaluation['DC']['prob'][0] * 100, 2)})"
        cp1 = f"1 ({round(self._evaluation['DC']['prob'][1] * 100, 2)})"
        rtcp0 = RichText()
        rtcp1 = RichText()
        rtcp0.add(cp0, bold=self._evaluation["DC"]["result"] == 0)
        rtcp1.add(cp1, bold=self._evaluation["DC"]["result"] == 1)
        context['cp0'] = rtcp0
        context['cp1'] = rtcp1
        self._print_process()

        lap10 = f"0 ({round(self._evaluation['LAP1']['prob'][0] * 100, 2)})"
        lap11 = f"1 ({round(self._evaluation['LAP1']['prob'][1] * 100, 2)})"
        rtlap10 = RichText()
        rtlap11 = RichText()
        rtlap10.add(lap10, bold=self._evaluation["LAP1"]["result"] == 0)
        rtlap11.add(lap11, bold=self._evaluation["LAP1"]["result"] == 1)
        context['lap10'] = rtlap10
        context['lap11'] = rtlap11
        self._print_process()

        lap20 = f"0 ({round(self._evaluation['LAP2']['prob'][0] * 100, 2)})"
        lap21 = f"1 ({round(self._evaluation['LAP2']['prob'][1] * 100, 2)})"
        rtlap20 = RichText()
        rtlap21 = RichText()
        rtlap20.add(lap20, bold=self._evaluation["LAP2"]["result"] == 0)
        rtlap21.add(lap21, bold=self._evaluation["LAP2"]["result"] == 1)
        context['lap20'] = rtlap20
        context['lap21'] = rtlap21
        self._print_process()

        lap30 = f"0 ({round(self._evaluation['LAP3']['prob'][0] * 100, 2)})"
        lap31 = f"1 ({round(self._evaluation['LAP3']['prob'][1] * 100, 2)})"
        rtlap30 = RichText()
        rtlap31 = RichText()
        rtlap30.add(lap30, bold=self._evaluation["LAP3"]["result"] == 0)
        rtlap31.add(lap31, bold=self._evaluation["LAP3"]["result"] == 1)
        context['lap30'] = rtlap30
        context['lap31'] = rtlap31
        self._print_process()

        lap40 = f"0 ({round(self._evaluation['LAP4']['prob'][0] * 100, 2)})"
        lap41 = f"1 ({round(self._evaluation['LAP4']['prob'][1] * 100, 2)})"
        rtlap40 = RichText()
        rtlap41 = RichText()
        rtlap40.add(lap40, bold=self._evaluation["LAP4"]["result"] == 0)
        rtlap41.add(lap41, bold=self._evaluation["LAP4"]["result"] == 1)
        context['lap40'] = rtlap40
        context['lap41'] = rtlap41
        self._print_process()

        pm0 = f"0 ({round(self._evaluation['PM']['prob'][0] * 100, 2)})"
        pm1 = f"1 ({round(self._evaluation['PM']['prob'][1] * 100, 2)})"
        rtpm0 = RichText()
        rtpm1 = RichText()
        rtpm0.add(pm0, bold=self._evaluation["PM"]["result"] == 0)
        rtpm1.add(pm1, bold=self._evaluation["PM"]["result"] == 1)
        context['pm0'] = rtpm0
        context['pm1'] = rtpm1
        self._print_process()

        dt0 = f"0 ({round(self._evaluation['DT']['prob'][0] * 100, 2)})"
        dt1 = f"1 ({round(self._evaluation['DT']['prob'][1] * 100, 2)})"
        dt2 = f"2 ({round(self._evaluation['DT']['prob'][2] * 100, 2)})"
        rtdt0 = RichText()
        rtdt1 = RichText()
        rtdt2 = RichText()
        rtdt0.add(dt0, bold=self._evaluation["DT"]["result"] == 0)
        rtdt1.add(dt1, bold=self._evaluation["DT"]["result"] == 1)
        rtdt2.add(dt2, bold=self._evaluation["DT"]["result"] == 2)
        context['dt0'] = rtdt0
        context['dt1'] = rtdt1
        context['dt2'] = rtdt2
        self._print_process()

        total = 0
        for pat in self._evaluation:
            total += self._evaluation[pat]["result"]

        total += self._evaluation["DC"]["result"]

        context["tinetti_total"] = total

        self._print_process()
        self._template.render(context)
        self._template.save("generated_doc.docx")

        self._print_finish()

    def _create_img(self,size,buf):
        img_size = Cm(size)  # sets the size of the image
        img = InlineImage(self._template, buf, img_size)
        return img

    def _get_joint_range(self, a, b):
        if a > b:
            return round(abs(b-a),2)
        else:
            return round(abs(a-b),2)

    def _get_kinematics_parameters(self,kine_text,leg):
        data_kine = []
        data_min = []
        data_max = []
        for stride in self._gait[leg]["strides"]:
            data_kine.append(stride["kinematics"][kine_text])
            data_min.append(np.array(stride["kinematics"][kine_text]).min())
            data_max.append(np.array(stride["kinematics"][kine_text]).max())

        #return data_kine, data_min, data_max
        return data_kine, data_max, data_min

    def _generate_kinematic_graph(self,input,kine_text="",leg="right"):
        fig, ax = plt.subplots(figsize=(10, 7))

        data = []
        for i in range(0, len(input)):
            for j in range(0,len(input[i])):
                stride_data = {"per": j, "kine": input[i][j]}
                data.append(stride_data)
        data = pd.DataFrame(data)

        normal = self._normal_kinematics[self._normal_kinematics["kine_text"] == kine_text]
        normal = normal[normal["leg"] == leg]

        color = "lightblue" if leg == "right" else "red"

        sns.set_color_codes("pastel")

        sns.lineplot(data=normal, x="per",y="kine",ls="",color="gray",ax=ax,legend=False,ci="sd")
        #sns.lineplot(data=df, x="per", y="kine", hue="Pierna", ci=100, palette=["b", "r"], ax=ax)
        #for line in input:
        sns.lineplot(data=data,x="per",y="kine",ls="-",color=color,ax=ax,legend=False)

        ax.set_xlabel("Ciclo marcha (%)", fontsize=14, labelpad=10)
        ax.set_ylabel("Ángulo (º)", fontsize=14, labelpad=10)

        ax.axvline(60, ls=':', c="lightgray")
        buf = io.BytesIO()
        plt.savefig(buf, dpi=150)
        plt.close()
        return buf

    def _spatiotemporal_figure_duration(self,input):
        sns.set_theme(style="whitegrid")

        f, ax = plt.subplots(figsize=(6, 2.5))
        data = pd.DataFrame([input])

        sns.set_color_codes("pastel")
        g = sns.barplot(data=data,
                        label="Total", palette=["r", "lightgray", "b"], orient="h", dodge=False)

        ax.set(xlim=(0, 2), ylabel="")#, xlabel="Longitud de zancada")

        g.text(0.35, 0.07, f"{data['Der'][0]} s", color='black', ha="center")
        g.text(0.35, 1.07, f"{data['Med'][0]} s", color='black', ha="center")
        g.text(0.35, 2.07, f"{data['Izq'][0]} s", color='black', ha="center")

        self._change_width(ax, .7)

        buf = io.BytesIO()
        plt.savefig(buf,dpi=150)
        plt.close()
        #buf.seek(0)
        #return base64.b64encode(buf.read())
        return buf

    def _spatiotemporal_figure_length(self, input):

        ## Input -- {"Der": 1109, "Med": (1123 + 1109) / 2, "Izq": 1123}
        sns.set_theme(style="whitegrid")
        f, ax = plt.subplots(figsize=(6, 2.5))
        data = pd.DataFrame([input])

        sns.set_color_codes("pastel")
        g = sns.barplot(data=data,
                        label="Total", palette=["r", "lightgray", "b"], orient="h", dodge=False)

        ax.set(xlim=(0, 1200), ylabel="")#, xlabel="Longitud de zancada")

        g.text(200, 0.07, f"{data['Der'][0]} mm", color='black', ha="center")
        g.text(200, 1.07, f"{data['Med'][0]} mm", color='black', ha="center")
        g.text(200, 2.07, f"{data['Izq'][0]} mm", color='black', ha="center")

        self._change_width(ax, .7)
        buf = io.BytesIO()
        plt.savefig(buf,dpi=150)
        plt.close()
        #buf.seek(0)

        #return base64.b64encode(buf.read())
        return buf

    def _change_width(self,ax,new_value):
        for patch in ax.patches:
            current_width = patch.get_height()
            diff = current_width - new_value

            # we change the bar width
            patch.set_height(new_value)

            # we recenter the bar
            patch.set_x(patch.get_x() + diff * .5)

    def _print_process(self):
        print(".", end="")

    def _print_finish(self):
        print(f"{C.Colorama.OKGREEN} Hecho!{C.Colorama.ENDC}")