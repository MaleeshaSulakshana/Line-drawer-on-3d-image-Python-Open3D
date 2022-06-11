import open3d as o3d
import drawer


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

    print(f"{drawer.commandcolors.GREEN}Tower count - {len(points)}{drawer.commandcolors.ENDC}")

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
