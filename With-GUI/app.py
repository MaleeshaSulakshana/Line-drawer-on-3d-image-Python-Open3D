import os
import sys
import random
import threading
import webbrowser
import glob
import shutil

import open3d as o3d
os.system('color FF')

from datetime import datetime
from flask import Flask, render_template, redirect, jsonify, url_for, request

# sys.path.append(os.path.abspath('./python/'))

# import drawer

app = Flask(__name__)

app.secret_key = "3dLines"
app.static_folder = "templates/"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Document folder root path
document_folder = os.path.expanduser('~/Downloads')
software_name = "3D-Line-Drawer"
software_folder_path = r"" + document_folder + "/" + software_name


# Command colors
class commandcolors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def draw_lines(folder_path, point_cloud_name):

    # Default values
    safety_level = 2.7  # m
    power_line_level = 1.5  # m
    corido_level = 1.5  # m
    base_level = 9  # m
    corido_height = 200  # cm
    corido_color_code = [1, 255, 0]  # RGB - yellow
    main_color_code = [0, 0, 0]  # RGB - black
    safety_color_code = [1, 0, 0]  # RGB - red

    # Paths
    txt_path = folder_path + "/values.txt"
    point_cloud = folder_path + "/" + point_cloud_name
    lines_name = folder_path + "/line_set.ply"

    # Check text file is exist
    if not os.path.exists(txt_path):
        print(f"{commandcolors.FAIL}Please check text file path!{commandcolors.ENDC}")
        sys.exit(0)

    # Check point cloud is exist
    if not os.path.exists(point_cloud):
        print(
            f"{commandcolors.FAIL}Please check point cloud path!{commandcolors.ENDC}")
        sys.exit(0)

    print(
        f"{commandcolors.GREEN}Process Start!{commandcolors.ENDC}")

    # Call genarate lines function
    genarate_lines(safety_level, corido_level, base_level, corido_height, power_line_level,
                   corido_color_code, main_color_code, safety_color_code, txt_path, lines_name)

    # Check line set is exist
    if not os.path.exists(lines_name):
        print(
            f"{commandcolors.FAIL}Line set not save. Please check and try again!{commandcolors.ENDC}")
        sys.exit(0)

    show_merged_point_cloud(point_cloud, lines_name)

    print(
        f"{commandcolors.GREEN}Process End!{commandcolors.ENDC}")


def show_merged_point_cloud(point_cloud, lines_name):

    # Read point cloud
    pcd = o3d.io.read_point_cloud(point_cloud)

    # Read line set
    lines = o3d.io.read_line_set(lines_name)

    # Merge and visualize
    merged_pcd = [pcd, lines]
    o3d.visualization.draw_geometries(merged_pcd)


# Method for genarte main, safety and corido lines using given coordinates
def genarate_lines(safety_level=2.7, corido_level=1.5, base_level=11, corido_height=200, power_line_level=1.5,
                   corido_color_code=[1, 255, 0], main_color_code=[0, 0, 0], safety_color_code=[1, 0, 0], txt_path="", line_set_name="line_set.ply"):

    # Create safety level height with cm
    safety_level_height = int(safety_level * 100)

    # Check and set corido height
    if corido_height < 5:
        corido_height = 5

    # Read text file
    file1 = open(txt_path, "r+")
    text_data = file1.readlines()

    # Get main towers top coordinates from text file
    points = []
    for data in text_data:
        # Replace \n & space to ''
        replaced = data.replace("\n", "")
        replaced = data.replace(" ", "")

        # Split by comma(,)
        splitted = replaced.split(",")

        # Append values to points array
        points.append([float(splitted[0]), float(
            splitted[1]), float(splitted[2])])

    print(f"{commandcolors.GREEN}Tower count - {len(points)}{commandcolors.ENDC}")

    # Create copy of points
    final_points = points.copy()

    # Create left power line
    for point in points:
        final_points.append(
            [(point[0] - power_line_level), point[1], point[2]])

    # Create right power line
    for point in points:
        final_points.append(
            [(point[0] + power_line_level), point[1], (point[2])])

    # Create safety line
    for count in range(1, safety_level_height):
        for point in points:
            final_points.append(
                [point[0], point[1], (point[2] - (count / 100))])

    # Create left corido line (wall)
    for count in range(1, corido_height):
        for point in points:
            final_points.append(
                [(point[0] - corido_level), point[1], (point[2] - base_level + count / 100)])

    # Create right corido line (wall)
    for count in range(1, corido_height):
        for point in points:
            final_points.append(
                [(point[0] + corido_level), point[1], (point[2] - base_level + count / 100)])

    lines = []
    # Create line maping for main line
    points_length = len(points)
    for i in range(points_length):
        if i < (points_length - 1):
            lines.append([i, i + 1])

    # Create line maping for left power line
    lines_length = len(lines) + 1
    for i in range(points_length):
        if i < (points_length - 1):
            lines.append([lines_length + i, i + 1 + lines_length])

    # Create line maping for right power line
    lines_length = len(lines) + 2
    for i in range(points_length):
        if i < (points_length - 1):
            lines.append([lines_length + i, i + 1 + lines_length])

    main_power_lines_length = len(lines)

    # Create line maping for safety line
    lines_length = len(lines) + 3
    for count in range(1, safety_level_height):
        for i in range(points_length):
            if i < (points_length - 1):
                lines.append(
                    [(lines_length + i), (i + 1) + lines_length])
        lines_length += i + 1

    safety_line_length = len(lines)

    # Create line maping for left corido line (wall)
    lines_length = len(lines) + (safety_level_height - 2) + 4
    for count in range(1, corido_height):
        for i in range(points_length):
            if i < (points_length - 1):
                lines.append(
                    [(lines_length + i), (i + 1) + lines_length])
        lines_length += i + 1

    # Create line maping for right corido line (wall)
    lines_length = len(lines) + (safety_level_height - 2) + \
        (corido_height - 2) + 5
    for count in range(1, corido_height):
        for i in range(points_length):
            if i < (points_length - 1):
                lines.append(
                    [(lines_length + i), (i + 1) + lines_length])
        lines_length += i + 1

    colors = []
    for i in range(len(lines)):
        # Set main line color for main 3 power lines
        if i <= (main_power_lines_length) - 1:
            colors.append(main_color_code)

        # Set safety line color for safety line
        elif i >= (main_power_lines_length) - 1 and i <= (safety_line_length) - 1:
            colors.append(safety_color_code)

        # Set corido line color for corido lines
        else:
            colors.append(corido_color_code)

    # Create line set using given data
    line_set = o3d.geometry.LineSet()
    line_set.points = o3d.utility.Vector3dVector(final_points)
    line_set.lines = o3d.utility.Vector2iVector(lines)
    line_set.colors = o3d.utility.Vector3dVector(colors)

    # Save line set
    o3d.io.write_line_set(filename=line_set_name, line_set=line_set,
                          write_ascii=False, compressed=False, print_progress=False)


# Method for create software folder on computerr
def create_software_folders():

    if not os.path.exists(software_folder_path):
        os.makedirs(software_folder_path)


# Create the folder structure
def genarate_folder():
    # Get date and time
    date_time = datetime.now()
    date_time = str(date_time.strftime("%d-%m-%Y-%H-%M-%S"))

    # Get random number
    random_no = str(random.randint(100000, 999999))

    # Paths
    folder_name = date_time + "-" + random_no + "/"
    folder_path = os.path.join(software_folder_path, folder_name)

    # Genarate folders
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    return folder_path


# Route for index/home page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# Route for draw lines
@app.route('/drawing_process', methods=['GET', 'POST'])
def drawing_process():

    point_cloud = request.files.get('point_cloud')
    point_text = request.files.get('point_text')

    if point_cloud == None or point_text == None:
        return jsonify({'error': "Point cloud or point text file not uploaded"})

    else:

        # Save items
        folder_path = genarate_folder()

        point_cloud_extention = point_cloud.filename.split('.')[-1]
        point_cloud_name = "point_cloud." + point_cloud_extention
        point_cloud.save(
            folder_path + point_cloud_name)

        # point_text_name = point_text.filename
        point_text.save(
            folder_path + "values.txt")

        draw_lines(folder_path, point_cloud_name)
        shutil.rmtree(folder_path)
        return jsonify({'success': "Lines draw success and viewed!"})


# Main
if __name__ == '__main__':

    port = 5000 + random.randint(0, 999)
    url = "http://127.0.0.1:{0}".format(port)
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    create_software_folders()
    app.run(port=port, debug=False)
