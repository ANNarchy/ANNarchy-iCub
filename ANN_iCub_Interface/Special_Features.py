"""
   Copyright (C) 2022 Torsten Fietzek; Helge Ülo Dinkelbach

   Special_Features.py is part of the iCub ANNarchy interface

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   The iCub ANNarchy interface is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this headers. If not, see <http://www.gnu.org/licenses/>.
 """

import os
import xml.etree.ElementTree as ET


def _textToList(liststring):
    l_x = liststring.strip('[]').replace('\'', '').replace(' ', '')
    if len(l_x) == 0:
        return list(l_x)
    else:
        return [int(x) for x in l_x.split(",")]


def create_robot_interface_file(filename_config: str, filename_interface: str = "./robot_interface.py"):
    """Create file with interface init code.

    Parameters
    ----------
    filename_config :
        filename of XML config file
    filename_interface :
        filename of created interface file (Default value = "./robot_interface.py")

    Returns
    -------

    """

    file_template = {}

    file_template["comment_file"] = "\"\"\" Generated file for ANNarchy-iCub-interface usage. \"\"\"\n\n"
    file_template["import_const"] = "\nimport ANN_iCub_Interface.Vocabs as iCub_Constants\n"
    file_template["import_interface"] = "from ANN_iCub_Interface.iCub import iCub_Interface"
    file_template["create_instance"] = "{0[var]}{0[count]} = {0[mod]}.{0[type]}()\n"
    file_template["args_dict"] = "args_{var}{count} = {cont}\n"
    file_template["comment_mod"] = "## Create and initialize {mod} instances.\n"
    file_template["instance_init"] = "{var}{count}.init(iCub, **args_{var}{count})\n\n"
    file_template["instance_init_grpc"] = "{var}{count}.init_grpc(iCub, **args_{var}{count})\n\n"

    file_data = []
    file_data.append(file_template["comment_file"])
    file_data.append(file_template["import_const"])
    file_data.append("## Create main interface wrapper class\n")
    file_data.append(file_template["create_instance"].format({'var': "iCub", "count": "", "mod": "iCub_Interface", "type": "ANNiCub_wrapper"}) + "\n\n")

    # Read from XML
    if os.path.isfile(filename_config):
        tree = ET.parse(filename_config)
        robot = tree.getroot()

        if robot is not None:
            # init joint reader
            jreader = []
            for idx, jread in enumerate(robot.iter('JReader')):
                args = {"name": jread.attrib['name']}
                grpc = False
                no_error_jread = True
                if jread.find('part') is None:
                    print(args['name'], "Element part is missing")
                    no_error_jread = False
                else:
                    args['part'] = jread.find('part').text
                if jread.find('sigma') is None:
                    print(args['name'], "Element sigma is missing")
                    no_error_jread = False
                else:
                    args['sigma'] = float(jread.find('sigma').text)
                if jread.find('popsize') is None:
                    if jread.find('n_pop') is None:
                        print(args['name'], "Element popsize is missing")
                        no_error_jread = False
                    else:
                        args['n_pop'] = int(jread.find('n_pop').text)
                else:
                    args['n_pop'] = int(jread.find('popsize').text)
                if jread.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing")
                    no_error_jread = False
                else:
                    args['ini_path'] = jread.find('ini_path').text
                if not jread.find('ip_address') is None:
                    args['ip_address'] = jread.find('ip_address').text
                    if not jread.find('port') is None:
                        args['port'] = int(jread.find('port').text)
                        grpc = True
                if jread.find('deg_per_neuron') is not None:
                    args['degr_per_neuron'] = float(jread.find('deg_per_neuron').text)

                if no_error_jread:
                    jreader.append(file_template["create_instance"].format({'var': "jreader", "count": idx, "mod": "Joint_Reader", "type": "PyJointReader"}))
                    jreader.append(file_template["args_dict"].format(var="jreader", count=idx, cont=str(args)))
                    if grpc:
                        jreader.append(file_template["instance_init_grpc"].format(count=idx, var="jreader"))
                    else:
                        jreader.append(file_template["instance_init"].format(count=idx, var="jreader"))
                else:
                    print("Skipped Joint Reader '" + jread.attrib['name'] + "' init due to missing element")

            if len(jreader) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Joint Reader"))
                file_template["import_interface"] += ", Joint_Reader"
                file_data.extend(jreader)
                file_data.append("\n")

            # init joint writer
            jwriter = []
            for idx, jwrite in enumerate(robot.iter('JWriter')):
                args = {"name": jwrite.attrib['name']}
                grpc = False
                no_error_jwrite = True
                if jwrite.find('part') is None:
                    print(args['name'], "Element part is missing")
                    no_error_jwrite = False
                else:
                    args['part'] = jwrite.find('part').text
                if jwrite.find('popsize') is None:
                    if jwrite.find('n_pop') is None:
                        print(args['name'], "Element popsize is missing")
                        no_error_jwrite = False
                    else:
                        args['n_pop'] = int(jwrite.find('n_pop').text)
                else:
                    args['n_pop'] = int(jwrite.find('popsize').text)
                if jwrite.find('speed') is None:
                    print(args['name'], "Element speed is missing")
                    no_error_jwrite = False
                else:
                    args['speed'] = float(jwrite.find('speed').text)
                if jwrite.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing")
                    no_error_jwrite = False
                else:
                    args['ini_path'] = jwrite.find('ini_path').text
                if not jwrite.find('ip_address') is None:
                    args['ip_address'] = jwrite.find('ip_address').text
                    if not jwrite.find('port') is None:
                        args['port'] = int(jwrite.find('port').text)
                        if not jwrite.find('mode') is None:
                            args['mode'] = jwrite.find('mode').text
                            if not jwrite.find('blocking') is None:
                                args['blocking'] = eval(jwrite.find('blocking').text.capitalize())
                                if not jwrite.find('joint_select') is None:
                                    args['joints'] = _textToList(jwrite.find('joint_select').text)
                                    grpc = True
                                elif not jwrite.find('joints') is None:
                                    args['joints'] = _textToList(jwrite.find('joints').text)
                                    grpc = True
                if jwrite.find('deg_per_neuron') is not None:
                    args['degr_per_neuron'] = float(jwrite.find('deg_per_neuron').text)

                if no_error_jwrite:
                    jwriter.append(file_template["create_instance"].format({'var': "jwriter", "count": idx, "mod": "Joint_Writer", "type": "PyJointWriter"}))
                    jwriter.append(file_template["args_dict"].format(var="jwriter", count=idx, cont=str(args)))
                    if grpc:
                        jwriter.append(file_template["instance_init_grpc"].format(count=idx, var="jwriter"))
                    else:
                        jwriter.append(file_template["instance_init"].format(count=idx, var="jwriter"))

            if len(jwriter) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Joint Writer"))
                file_template["import_interface"] += ", Joint_Writer"
                file_data.extend(jwriter)
                file_data.append("\n")

            # init visual reader
            vreader = []
            for idx, vread in enumerate(robot.iter('VisReader')):
                args = {"name": vread.attrib['name']}
                grpc = False
                no_error_vread = True
                if vread.find('eye') is None:
                    print(args['name'], "Element eye is missing")
                    no_error_vread = False
                else:
                    args['eye'] = vread.find('eye').text
                if (vread.find('fov_width') is None) or (vread.find('fov_height') is None):
                    print(args['name'], "Element fov_width or fov_height is missing")
                    no_error_vread = False
                else:
                    args['fov_width'] = float(vread.find('fov_width').text)
                    args['fov_height'] = float(vread.find('fov_height').text)
                if (vread.find('img_width') is None) or (vread.find('img_height') is None):
                    print(args['name'], "Element img_width or img_height is missing")
                    no_error_vread = False
                else:
                    args['img_width'] = int(vread.find('img_width').text)
                    args['img_height'] = int(vread.find('img_height').text)
                if vread.find('fast_filter') is None:
                    print(args['name'], "Element fast_filter is missing")
                    no_error_vread = False
                else:
                    args['fast_filter'] = eval(vread.find('fast_filter').text.capitalize())
                if vread.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing")
                    no_error_vread = False
                else:
                    args['ini_path'] = vread.find('ini_path').text
                if not vread.find('ip_address') is None:
                    args['ip_address'] = vread.find('ip_address').text
                    if not vread.find('port') is None:
                        args['port'] = int(vread.find('port').text)
                        grpc = True
                if no_error_vread:
                    vreader.append(file_template["create_instance"].format({'var': "vreader", "count": idx, "mod": "Visual_Reader", "type": "PyVisualReader"}))
                    vreader.append(file_template["args_dict"].format(var="vreader", count=idx, cont=str(args)))
                    if grpc:
                        vreader.append(file_template["instance_init_grpc"].format(count=idx, var="vreader"))
                    else:
                        vreader.append(file_template["instance_init"].format(count=idx, var="vreader"))
                else:
                    print("Skipped Visual Reader init due to missing element")

            if len(vreader) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Visual Reader"))
                file_template["import_interface"] += ", Visual_Reader"
                file_data.extend(vreader)
                file_data.append("\n")

            # init tactile reader
            sreader = []
            for idx, sread in enumerate(robot.iter('TacReader')):
                args = {"name": sread.attrib['name']}
                grpc = False
                no_error_sread = True
                if sread.find('arm') is None:
                    print(args['name'], "Element arm is missing")
                    no_error_sread = False
                else:
                    args['arm'] = sread.find('arm').text
                if sread.find('normalize') is None:
                    print(args['name'], "Element norm is missing")
                    no_error_sread = False
                else:
                    args['norm'] = eval(sread.find('normalize').text.capitalize())
                if sread.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing")
                    no_error_sread = False
                else:
                    args['ini_path'] = sread.find('ini_path').text
                if not sread.find('ip_address') is None:
                    args['ip_address'] = sread.find('ip_address').text
                    if not sread.find('port') is None:
                        args['port'] = int(sread.find('port').text)
                        grpc = True
                if no_error_sread:
                    sreader.append(file_template["create_instance"].format({'var': "sreader", "count": idx, "mod": "Skin_Reader", "type": "PySkinReader"}))
                    sreader.append(file_template["args_dict"].format(var="sreader", count=idx, cont=str(args)))
                    if grpc:
                        sreader.append(file_template["instance_init_grpc"].format(count=idx, var="sreader"))
                    else:
                        sreader.append(file_template["instance_init"].format(count=idx, var="sreader"))
                else:
                    print("Skipped Skin Reader '" + sread.attrib['name'] + "' init due to missing element")

            if len(sreader) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Skin Reader"))
                file_template["import_interface"] += ", Skin_Reader"
                file_data.extend(sreader)
                file_data.append("\n")

            # init kinematic reader
            kreader = []
            for idx, kread in enumerate(robot.iter('KinReader')):
                args = {"name": kread.attrib['name']}
                grpc = False
                no_error_kread = True
                if kread.find('part') is None:
                    print(args['name'], "Element part is missing!")
                    no_error_kread = False
                else:
                    args['part'] = kread.find('part').text
                if kread.find('version') is None:
                    print(args['name'], "Element version is missing!")
                    no_error_kread = False
                else:
                    args['version'] = float(kread.find('version').text)
                if kread.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing!")
                    no_error_kread = False
                else:
                    args['ini_path'] = kread.find('ini_path').text
                if kread.find('offline_mode') is None:
                    print(args['name'], "Standard value for element 'offline_mode' is used.")
                    args['offline_mode'] = False
                else:
                    args['offline_mode'] = eval(kread.find('offline_mode').text.capitalize())
                if not kread.find('ip_address') is None:
                    args['ip_address'] = kread.find('ip_address').text
                    if not kread.find('port') is None:
                        args['port'] = int(kread.find('port').text)
                        grpc = True
                if no_error_kread:
                    kreader.append(file_template["create_instance"].format({'var': "kreader", "count": idx, "mod": "Kinematic_Reader", "type": "PyKinematicReader"}))
                    kreader.append(file_template["args_dict"].format(var="kreader", count=idx, cont=str(args)))
                    if grpc:
                        kreader.append(file_template["instance_init_grpc"].format(count=idx, var="kreader"))
                    else:
                        kreader.append(file_template["instance_init"].format(count=idx, var="kreader"))
                else:
                    print("Skipped Kinematic Reader '" + kread.attrib['name'] + "' init due to missing element")

            if len(kreader) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Kinematic Reader"))
                file_template["import_interface"] += ", Kinematic_Reader"
                file_data.extend(kreader)
                file_data.append("\n")

            # init kinematic writer
            kwriter = []
            for idx, kwrite in enumerate(robot.iter('KinWriter')):
                args = {"name": kwrite.attrib['name']}
                grpc = False
                no_error_kwrite = True
                if kwrite.find('part') is None:
                    print(args['name'], "Element part is missing")
                    no_error_kwrite = False
                else:
                    args['part'] = kwrite.find('part').text
                if kwrite.find('version') is None:
                    print(args['name'], "Element version is missing")
                    no_error_kwrite = False
                else:
                    args['version'] = float(kwrite.find('version').text)
                if kwrite.find('ini_path') is None:
                    print(args['name'], "Element ini_path is missing")
                    no_error_kwrite = False
                else:
                    args['ini_path'] = kwrite.find('ini_path').text
                if not kwrite.find('ip_address') is None:
                    args['ip_address'] = kwrite.find('ip_address').text
                    if not kwrite.find('port') is None:
                        args['port'] = int(kwrite.find('port').text)
                        grpc = True
                if no_error_kwrite:
                    kwriter.append(file_template["create_instance"].format({'var': "kwriter", "count": idx, "mod": "Kinematic_Writer", "type": "PyKinematicWriter"}))
                    kwriter.append(file_template["args_dict"].format(var="kwriter", count=idx, cont=str(args)))
                    if grpc:
                        kwriter.append(file_template["instance_init_grpc"].format(count=idx, var="kwriter"))
                    else:
                        kwriter.append(file_template["instance_init"].format(count=idx, var="kwriter"))
                else:
                    print("Skipped Kinematic Writer '" + kwrite.attrib['name'] + "' init due to missing element")

            if len(kwriter) > 0:
                file_data.append(file_template["comment_mod"].format(mod="Kinematic Writer"))
                file_template["import_interface"] += ", Kinematic_Writer"
                file_data.extend(kwriter)
                file_data.append("\n")

        else:
            print("Failed to read XML-file")
    else:
        print("Not a valid XML-Filepath given!")

    # Write to python file
    file_data.insert(2, file_template["import_interface"] + "\n\n\n")
    with open(filename_interface, "w") as file:
        file.writelines(file_data)
