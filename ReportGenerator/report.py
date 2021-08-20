from docxtpl import DocxTemplate, InlineImage
import matplotlib.pyplot as plt
from docx.shared import Cm
import seaborn as sns
import pandas as pd
import io
import ReportGenerator.constants as C
from datetime import date
import base64

class Report:

    def __init__(self, name, surname, age, gait, evaluation):

        self._template = DocxTemplate(C.TEMPLATE_PATH)
        self._gait = gait
        self._name = name
        self._surname = surname
        self._age = age
        self._evaluation = evaluation

    def generate_report(self):
            context = {}
            context["name"] = self._name
            context["surname"] = self._surname
            context["age"] = self._age
            context["date"] = date.today().strftime("%d/%m/%Y")

            ## Spatiotemporal
            context["n_str_r"] = self._gait["total_right"]
            context["n_str_l"] = self._gait["total_left"]
            context["n_ste_r"] = self._gait["right"]["spaciotemporal"]["steps"]
            context["n_ste_l"] = self._gait["left"]["spaciotemporal"]["steps"]

            context["pad_d"] = round(self._gait["right"]["spaciotemporal"]["support_duration"],2)
            context["pad_p"] = round(self._gait["right"]["spaciotemporal"]["support_percentage"],2)
            context["pbd_d"] = round(self._gait["right"]["spaciotemporal"]["swing_duration"],2)
            context["pbd_p"] = round(self._gait["right"]["spaciotemporal"]["swing_percentage"],2)
            context["pai_d"] = round(self._gait["left"]["spaciotemporal"]["support_duration"], 2)
            context["pai_p"] = round(self._gait["left"]["spaciotemporal"]["support_percentage"], 2)
            context["pbi_d"] = round(self._gait["left"]["spaciotemporal"]["swing_duration"], 2)
            context["pbi_p"] = round(self._gait["left"]["spaciotemporal"]["swing_percentage"], 2)

            context["max_tal_r"] = round(self._gait["right"]["spaciotemporal"]["ankle_height"],2)
            context["max_tal_l"] = round(self._gait["left"]["spaciotemporal"]["ankle_height"],2)
            context["cadence"] = round(self._gait["cadence"],2)
            context["velocity"] = round(self._gait["velocity"],2)
            context["width"] = round(self._gait["support_width"],2)

            input = {"Der": round(self._gait["right"]["spaciotemporal"]["duration"], 2),
                     "Med": 0,
                     "Izq": round(self._gait["left"]["spaciotemporal"]["duration"], 2)}
            input["Med"] = round((input["Der"] + input["Izq"]) / 2, 2)
            spatiotemporal_fig_3 = self._create_img(13, self._spatiotemporal_figure_duration(input))
            context['stride_duration_1'] = spatiotemporal_fig_3

            input = {"Der": round(self._gait["right"]["spaciotemporal"]["stride_length"],2),
                     "Med":0,
                     "Izq": round(self._gait["left"]["spaciotemporal"]["stride_length"],2)}
            input["Med"] = round((input["Der"]+input["Izq"])/2,2)
            spatiotemporal_fig_1 = self._create_img(13,self._spatiotemporal_figure_length(input))
            context['stride_length'] =  spatiotemporal_fig_1

            input = {"Der": round(self._gait["right"]["spaciotemporal"]["steps_length"], 2),
                     "Med": 0,
                     "Izq": round(self._gait["left"]["spaciotemporal"]["steps_length"], 2)}
            input["Med"] = round((input["Der"] + input["Izq"]) / 2, 2)
            spatiotemporal_fig_2 = self._create_img(13, self._spatiotemporal_figure_length(input))
            context['steps_length'] =  spatiotemporal_fig_2

            input = {"Der": round(self._gait["right"]["spaciotemporal"]["steps_duration"], 3),
                     "Med": 0,
                     "Izq": round(self._gait["left"]["spaciotemporal"]["steps_duration"], 3)}
            input["Med"] = round((input["Der"] + input["Izq"]) / 2, 3)
            spatiotemporal_fig_4 = self._create_img(13, self._spatiotemporal_figure_duration(input))
            context['steps_duration'] =  spatiotemporal_fig_4


            ## Kinematics



            ## Tinetti
            print(self._evaluation)
            context["cp0"] = round(self._evaluation["DC"]["prob"][0] * 100,2)
            context["cp1"] = round(self._evaluation["DC"]["prob"][1] * 100,2)
            context["lap10"] = round(self._evaluation["LAP1"]["prob"][0] * 100,2)
            context["lap11"] = round(self._evaluation["LAP1"]["prob"][1] * 100,2)
            context["lap20"] = round(self._evaluation["LAP2"]["prob"][0] * 100,2)
            context["lap21"] = round(self._evaluation["LAP2"]["prob"][1] * 100,2)
            context["lap30"] = round(self._evaluation["LAP3"]["prob"][0] * 100,2)
            context["lap31"] = round(self._evaluation["LAP3"]["prob"][1] * 100,2)
            context["lap40"] = round(self._evaluation["LAP4"]["prob"][0] * 100,2)
            context["lap41"] = round(self._evaluation["LAP4"]["prob"][1] * 100,2)
            context["pm0"] = round(self._evaluation["PM"]["prob"][0] * 100,2)
            context["pm1"] = round(self._evaluation["PM"]["prob"][1] * 100,2)
            context["dt0"] = round(self._evaluation["DT"]["prob"][0] * 100,2)
            context["dt1"] = round(self._evaluation["DT"]["prob"][1] * 100,2)
            context["dt2"] = round(self._evaluation["DT"]["prob"][2] * 100,2)

            total = 0
            for pat in self._evaluation:
                total += self._evaluation[pat]["result"]

            total += self._evaluation["DC"]["result"]

            context["tinetti_total"] = total

            self._template.render(context)
            self._template.save("generated_doc.docx")

    def _create_img(self,size,buf):
        img_size = Cm(size)  # sets the size of the image
        img = InlineImage(self._template, buf, img_size)
        return img

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