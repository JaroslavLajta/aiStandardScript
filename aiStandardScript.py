#Jaroslav Lajta

import os
import json
from maya import cmds
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QPushButton,QFileDialog,QComboBox,QFrame
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt
import re



class ShaderCreator(QtWidgets.QMainWindow):
    def __init__(self,parent = None):

        if(self.load_json()):



            #Creates Window
            super(ShaderCreator, self).__init__(parent)

            self.window_title = "Shader Creator"
            self.setWindowTitle(self.window_title)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            central_widget = QtWidgets.QWidget()
            self.setCentralWidget(central_widget)
            self.main_layout = QtWidgets.QVBoxLayout(central_widget)


            #Variables
            self.folder_directory = "None"


            #Supported all file formats as in https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-BF7C7484-C7F6-48C6-9092-7E6EB373B312
            self.file_format = ["psd","als","avi","dds","gif","jpg","cin","iff","jpeg","exr","png","eps","yuv","pic","hdr","sgi","tim","tga","tif","rla","bmp","xpm"]
            self.texture_maps = {}

            #List off all the possible input spaces
            self.COLOR_SPACES = cmds.colorManagementPrefs(query=True, inputSpaceNames=True)

            #SubLayout
            self.sub_layout = None
            self.scroll_area = None
            self.create_shader_button = None

            #Name of the shader
            self.shader_name_field = self.add_text_field(label='Shader Name', label_w=100, label_h=50, box_w=300)
            self.shader_name_field.setPlaceholderText("standard_surface_shader")

            #File directory button
            self.dialogButton = self.add_button("CHOOSE FILE DIRECTORY", "Choose a file directory where all the texture maps are located")
            self.directory_text = self.add_text_label(f"Directory: {self.folder_directory}","No Directory selected",False)

            self.add_separator()

            self.dialogButton.clicked.connect(self.add_file_window)
        else:
            pass





    def format_camel_case(self,text:str):
        """
        Formats title
        """
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
        return formatted.title()


    def add_separator(self):

        """
        Creates a separator in the UI so it helps with visibility
        """
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        self.main_layout.addWidget(separator)


    def add_separator_sublayout(self):
        """
        Same function but only for the sub layout
        """
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setLineWidth(1)
        self.sub_layout.addWidget(separator)


    def add_file_window(self):

        #Saves the directory inside a variable

        self.folder_directory = QFileDialog.getExistingDirectory(None, "Select Directory")
        if self.folder_directory == "":
            self.folder_directory = "None"
        else:
            self.directory_text.setText(f"Directory: {self.folder_directory}")
            self.directory_text.setToolTip("Directory Selected")
            self.load_files()


    def load_files(self):
        """
        Loads all the respectable files, filters and saves them to a dictionary

        """

        # LOADING OF FILES

        self.texture_maps = {}
        all_files = set()
        only_images = set()
        all_images = set()

        for item in os.listdir(self.folder_directory):
            if os.path.isfile(f'{self.folder_directory}/{item}'):
                all_files.add(f'{self.folder_directory}/{item}')




        # Keep only files with chosen extensions

        for file in all_files:
            for file_type in self.file_format:
                if file.split('.')[-1].lower() == file_type:
                    only_images.add(file)
                    break

        # Just to show files that aren't images
        non_images = all_files.difference(only_images)

        for file in non_images:
            self.raise_warning(f"{os.path.basename(file)} doesn't have an acceptable extension!")

        config = self.shader_config["textures"]



        for filepath in only_images:
            filename = os.path.basename(filepath).lower()
            filename_split = os.path.splitext(filename)[0].split("_")


            for part in filename_split:
                for texture_type, data in config.items():
                    if part.lower() == texture_type.lower():

                        all_images.add(filepath)

                        if part.lower() == "normal":
                            self.texture_maps[texture_type] = self.texture_maps.get(texture_type, {})

                            if "directx" in filename.lower():


                                self.texture_maps[texture_type]["DirectX"] = {
                                    "filePath": filepath,
                                    "colorSpace": data["colorSpace"],
                                    "connectType": data["connectType"],
                                    "enableAlphaIsLuminance": data["enableAlphaIsLuminance"],
                                }
                                break
                            elif "opengl" in filename.lower():
                                self.texture_maps[texture_type]["OpenGL"] = {
                                    "filePath": filepath,
                                    "colorSpace": data["colorSpace"],
                                    "connectType": data["connectType"],
                                    "enableAlphaIsLuminance": data["enableAlphaIsLuminance"],
                                }

                                break
                            else:
                                self.texture_maps[texture_type]["Undefined"] = {
                                    "filePath": filepath,
                                    "colorSpace": data["colorSpace"],
                                    "connectType": data["connectType"],
                                    "enableAlphaIsLuminance": data["enableAlphaIsLuminance"],
                                }

                                break
                        else:

                            self.texture_maps[texture_type] = {

                                "filePath": filepath,

                                "colorSpace": data["colorSpace"],

                                "connectType": data["connectType"],

                                "enableAlphaIsLuminance": data["enableAlphaIsLuminance"],

                            }

                            break






        not_usable_images = all_files.difference(non_images)
        not_usable_images = not_usable_images.difference(all_images)



        for file in not_usable_images:
            self.raise_warning(f"{os.path.basename(file)} are not usable for the Shader!")



        if len(self.texture_maps) == 0:
            self.raise_warning("Didn't find any usable files")
        else:

            self.update_ui()


    def update_ui(self):
        """
                Updates the UI to display texture type, color space dropdown, and filename
                """
        # Removes additional UI if it exists so it can be readded, also removes button, so it always stay on bottom
        if self.sub_layout != None:
            self.main_layout.removeItem(self.sub_layout)
            self.main_layout.removeWidget(self.scroll_area)
            self.scroll_area.deleteLater()
            self.scroll_area = None

            while self.sub_layout.count():
                item = self.sub_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    item.layout().deleteLater()
            if self.create_shader_button != None:
                self.create_shader_button.deleteLater()
                self.create_shader_button = None

        # Sublayout that gets added for the files and colorspaces
        self.sub_layout = QtWidgets.QVBoxLayout()
        sub_widget = QtWidgets.QWidget()
        sub_widget.setLayout(self.sub_layout)

        # Wrap the sub_layout in a QScrollArea
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidget(sub_widget)
        self.scroll_area.setMinimumHeight(200)

        self.scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(self.scroll_area)

        # Creating UI elements to display to a user and to select ColorSpace
        only_one_normal = True

        for texture_type, data in self.texture_maps.items():

            if texture_type == "normal":

                self.add_text_label_sublayout(f"Texture: Normal", "", True)

                if len(data) == 1:

                    directx_opengl_selector = QComboBox()
                    found_normals = []
                    for normal_type in data:
                        found_normals.append(normal_type)

                    directx_opengl_selector.addItems(found_normals)
                    data["normal_selector"] = directx_opengl_selector


                    self.add_text_label_sublayout("Normal Map Type:", "", True)
                    directx_opengl_selector.setDisabled(True)
                    self.sub_layout.addWidget(directx_opengl_selector)



                else:
                    directx_opengl_selector = QComboBox()
                    found_normals = []
                    for normal_type in data:
                        found_normals.append(normal_type)

                    directx_opengl_selector.addItems(found_normals)
                    data["normal_selector"] = directx_opengl_selector


                    self.add_text_label_sublayout("Select Normal Map Type:", "", True)
                    self.sub_layout.addWidget(directx_opengl_selector)

                color_space_selector = QComboBox()
                color_space_selector.addItems(self.COLOR_SPACES)

                for map_type in ["directx", "opengl", "undefined"]:
                    for normal_type, normal_data in data.items():

                        if normal_type.lower() == map_type:

                            filename = os.path.basename(data[normal_type]["filePath"])
                            self.add_text_label_sublayout(f"File: {filename}", "", True)
                            color_space_index = color_space_selector.findText(data[normal_type]["colorSpace"])




                if color_space_index != -1:
                    color_space_selector.setCurrentIndex(color_space_index)

                data["ui_colorSpace"] = color_space_selector
                # Add the color space drop-down to the layout
                self.add_text_label_sublayout("Color Space:", "", True)
                self.sub_layout.addWidget(color_space_selector)
                self.add_separator_sublayout()

            else:

                texture_display_name = self.format_camel_case(texture_type)

                # texture_display_name = texture_display_name.title()

                self.add_text_label_sublayout(f"Texture: {texture_display_name}", "", True)

                # Display the file path (filename)
                filename = os.path.basename(data["filePath"])
                self.add_text_label_sublayout(f"File: {filename}", "", True)

                # Create a color space selector for each texture
                color_space_selector = QComboBox()
                color_space_selector.addItems(self.COLOR_SPACES)

                # Set the default color space based on the texture details
                color_space_index = color_space_selector.findText(data["colorSpace"])
                if color_space_index != -1:
                    color_space_selector.setCurrentIndex(color_space_index)

                data["ui_colorSpace"] = color_space_selector
                # Add the color space drop-down to the layout
                self.add_text_label_sublayout("Color Space:", "", True)
                self.sub_layout.addWidget(color_space_selector)
                self.add_separator_sublayout()

        self.main_layout.addLayout(self.sub_layout)

            # Button
        if self.create_shader_button == None:
            self.create_shader_button = self.add_button("CREATE YOUR SHADER", "After clicking this, your shader will be created")
            self.create_shader_button.clicked.connect(self.make_shader)


    def make_shader(self,**kwargs):
        """
        Creates Standard Surface Shader, imports texture maps and connects them to the correct part of shader
        """

        if self.shader_name_field.text() == "":
            shader_name = self.shader_name_field.placeholderText()
        else:
            shader_name = self.shader_name_field.text()
            shader_name = shader_name.replace(" ", "_")
            self.shader_name_field.setText(shader_name)




        shader = cmds.shadingNode('aiStandardSurface', asShader=True, name=shader_name)


        #Gives a warning if the shader name is already exists
        if shader != shader_name:
            self.raise_warning(f"Material {self.shader_name_field.text()} already exists, created a material with name: {shader}")

        shader_name = shader

        if self.shader_name_field.text() == "":
            self.shader_name_field.setPlaceholderText(shader_name)
        else:
            self.shader_name_field.setText(shader_name)

        shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{shader_name}SG")
        cmds.connectAttr(f"{shader}.outColor", f"{shading_group}.surfaceShader", force=True)

        #All the connections for the place2d node

        connections = ['rotateUV', 'offset', 'noiseUV', 'vertexCameraOne', 'vertexUvThree',
                       'vertexUvTwo', 'vertexUvOne', 'repeatUV', 'wrapV', 'wrapU', 'stagger',
                       'mirrorU', 'mirrorV', 'rotateFrame', 'translateFrame', 'coverage']


        #Boolean if normal and bump exists at the same time

        texture_maps_list = []
        for texture_type in self.texture_maps:
            texture_maps_list.append(texture_type)

        createBump = "bump" in texture_maps_list and "normal" not in texture_maps_list






        #This creates everything and connects based on the dictionary

        for texture_type, details in self.texture_maps.items():

            if "normal" == texture_type:



                combo_box_normal = details["normal_selector"]  # Get user selection (DirectX/OpenGL)
                normal_map_type = combo_box_normal.currentText()

                normal_map_details = details.get(normal_map_type)

                file_path = normal_map_details.get('filePath')


                file_node = cmds.shadingNode('file', asTexture=True, name=f"{texture_type}_file")

                place2d_node = cmds.shadingNode('place2dTexture', asUtility=True)

                cmds.connectAttr(place2d_node + '.outUV', file_node + '.uvCoord')
                cmds.connectAttr(place2d_node + '.outUvFilterSize', file_node + '.uvFilterSize')



                for i in connections:
                    cmds.connectAttr(place2d_node + '.' + i, file_node + '.' + i)


                cmds.setAttr(f"{file_node}.fileTextureName", file_path, type="string")

                # Apply color space from UI
                selected_color_space = details['ui_colorSpace'].currentText()
                cmds.setAttr(f"{file_node}.colorSpace", selected_color_space, type="string")

                # Create and connect aiNormalMap node
                normal_node = cmds.shadingNode('aiNormalMap', asUtility=True, name=f"{shader_name}_normal")




                cmds.connectAttr(f"{file_node}.outColor", f"{normal_node}.input", force=True)
                cmds.connectAttr(f"{normal_node}.outValue", f"{shader}.normalCamera", force=True)

            elif "height" == texture_type:

                #Height map connections with the displacement shader

                file_node = cmds.shadingNode('file', asTexture=True, name=f"{texture_type}_file")
                cmds.setAttr(f"{file_node}.fileTextureName", details['filePath'], type="string")

                place2d_node = cmds.shadingNode('place2dTexture', asUtility=True)

                cmds.connectAttr(place2d_node + '.outUV', file_node + '.uvCoord')
                cmds.connectAttr(place2d_node + '.outUvFilterSize', file_node + '.uvFilterSize')



                for i in connections:
                    cmds.connectAttr(place2d_node + '.' + i, file_node + '.' + i)

                # Apply color space from UI
                selected_color_space = details['ui_colorSpace'].currentText()
                cmds.setAttr(f"{file_node}.colorSpace", selected_color_space, type="string")
                cmds.setAttr(f"{file_node}.alphaIsLuminance", details['enableAlphaIsLuminance'])

                # Create and connect displacement shader
                disp_node = cmds.shadingNode('displacementShader', asShader=True, name=f"{shader_name}_disp")
                cmds.setAttr(f"{disp_node}.aiDisplacementZeroValue", 0.5)
                cmds.connectAttr(f"{file_node}.outAlpha", f"{disp_node}.displacement", force=True)
                cmds.connectAttr(f"{disp_node}.displacement", f"{shading_group}.displacementShader", force=True)


            elif "bump" == texture_type:
                #BUmp map connections

                if createBump:
                    file_node = cmds.shadingNode('file', asTexture=True, name=f"{texture_type}_file")
                    cmds.setAttr(f"{file_node}.fileTextureName", details['filePath'], type="string")

                    place2d_node = cmds.shadingNode('place2dTexture', asUtility=True)

                    cmds.connectAttr(place2d_node + '.outUV', file_node + '.uvCoord')
                    cmds.connectAttr(place2d_node + '.outUvFilterSize', file_node + '.uvFilterSize')

                    for i in connections:
                        cmds.connectAttr(place2d_node + '.' + i, file_node + '.' + i)

                    selected_color_space = details['ui_colorSpace'].currentText()
                    cmds.setAttr(f"{file_node}.colorSpace", selected_color_space, type="string")
                    cmds.setAttr(f"{file_node}.alphaIsLuminance", details['enableAlphaIsLuminance'])

                    bump_node = cmds.shadingNode('aiBump2d', asUtility=True)

                    cmds.connectAttr(f"{file_node}.outAlpha", f"{bump_node}.bumpMap", force=True)

                else:
                    self.raise_warning("Bump map will not be created since there is a Normal map")


            else:
                # Everything else
                file_node = cmds.shadingNode('file', asTexture=True, name=f"{texture_type}_file")
                cmds.setAttr(f"{file_node}.fileTextureName", details['filePath'], type="string")

                place2d_node = cmds.shadingNode('place2dTexture', asUtility=True)

                cmds.connectAttr(place2d_node + '.outUV', file_node + '.uvCoord')
                cmds.connectAttr(place2d_node + '.outUvFilterSize', file_node + '.uvFilterSize')



                for i in connections:
                    cmds.connectAttr(place2d_node + '.' + i, file_node + '.' + i)

                # Apply color space from UI
                selected_color_space = details['ui_colorSpace'].currentText()
                cmds.setAttr(f"{file_node}.colorSpace", selected_color_space, type="string")
                cmds.setAttr(f"{file_node}.alphaIsLuminance", details['enableAlphaIsLuminance'])

                # Connect based on connectType
                connect_attr = "outColor" if details['connectType'].lower() == "color" else "outAlpha"

                cmds.connectAttr(f"{file_node}.{connect_attr}", f"{shader}.{texture_type}", force=True)


    def load_json(self)->bool:

        """
        Loads a Json file with all the names and colorspaces inside python
        Gives error if it can't find it
        """

        flag = False
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_filename = 'ai_standard_surface_shader_config.json'

        json_filepath = os.path.join(script_dir, json_filename)

        try:
            with open(json_filepath, 'r') as json_file:
                self.shader_config = json.load(json_file)
                flag = True


        except:
            cmds.warning("Error with JSON file")
            cmds.confirmDialog(message="There has been an issue with the JSON file.\n\nMake sure it is in the same directory as the script."
                                       "\n\nReload script after", button=["OK"])




        return flag


    def raise_warning(self, msg: str):

        """

        Raises a warning inside maya with a custom message that it receives as a variable

        :param msg:
        :return:
        """
        cmds.warning(msg)


    def add_text_label(self,msg:str,annotation:str,isEnabled:bool):

        """
        Makes a simple label in the ui, basic text
        """

        label = QLabel()
        label.setText(msg)
        label.setToolTip(annotation)
        label.setAlignment(Qt.AlignLeft)
        label.setEnabled(isEnabled)
        self.main_layout.addWidget(label)
        return label


    def add_text_label_sublayout(self,msg:str,annotation:str,isEnabled:bool):

        """
        Makes a simple text but in the sublayout
        """

        label = QLabel()
        label.setText(msg)
        label.setToolTip(annotation)
        label.setAlignment(Qt.AlignLeft)
        label.setEnabled(isEnabled)
        self.sub_layout.addWidget(label)
        return label


    def add_text_field(self,label:str,label_w:int,label_h:int,box_w:int):

        """
        Text field to type in name
        """

        text_field_label = QLabel(label)
        text_field_label.setFixedSize(label_w,label_h)

        text_field_box = QLineEdit()
        text_field_box.setFixedWidth(box_w)

        local_layout = QHBoxLayout()
        local_layout.addWidget(text_field_label)
        local_layout.addWidget(text_field_box)


        self.main_layout.addLayout(local_layout)
        return text_field_box


    def add_button(self,text_str : str,annotation_str : str):

        """
        Button to click
        """

        button = QPushButton(text_str)
        button.setToolTip(annotation_str)
        local_layout = QHBoxLayout()
        local_layout.addWidget(button)
        self.main_layout.addLayout(local_layout)

        return button


def show_ui():
    """
    Closes the main window if it was previously created.
    Makes a new main window.
    """
    global Arnold_Standart_Surface_Shader_Window
    try:
        Arnold_Standart_Surface_Shader_Window.close()  # Close if it exists
    except:
        pass
    Arnold_Standart_Surface_Shader_Window = ShaderCreator()
    Arnold_Standart_Surface_Shader_Window.show()

# Run the UI
show_ui()
