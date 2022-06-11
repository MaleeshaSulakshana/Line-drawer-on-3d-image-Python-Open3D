import open3d as o3d
import os
os.system('color FF')
import sys

# Import file
import line_genarator as lg


# Command colors
class commandcolors:
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


if __name__ == "__main__":

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
    txt_path = "values.txt"
    point_cloud = "gh.xyz"
    lines_name = "line_set.ply"

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
    lg.genarate_lines(safety_level, corido_level, base_level, corido_height, power_line_level,
                      corido_color_code, main_color_code, safety_color_code, txt_path, lines_name)

    # Check line set is exist
    if not os.path.exists(lines_name):
        print(
            f"{commandcolors.FAIL}Line set not save. Please check and try again!{commandcolors.ENDC}")
        sys.exit(0)

    # Read point cloud
    pcd = o3d.io.read_point_cloud(point_cloud)

    # Read line set
    lines = o3d.io.read_line_set(lines_name)

    # Merge and visualize
    merged_pcd = [pcd, lines]
    o3d.visualization.draw_geometries(merged_pcd)

    print(
        f"{commandcolors.GREEN}Process End!{commandcolors.ENDC}")
