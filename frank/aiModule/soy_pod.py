from PyQt5.QtCore import QThread, pyqtSignal


import os

import cv2
import numpy as np
import math

from tqdm import tqdm


def display_cv2(window_name, img):
    return
    """显示图像"""
    cv2.imwrite(f"{window_name}.png", img)
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 800, 800)
    cv2.imshow(window_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def apply_strong_smoothing(image):
    """加强均值迁移和平滑"""
    # 1. 强化均值迁移（Mean Shift）
    mean_shift = cv2.pyrMeanShiftFiltering(image, 30, 60)  # 增强平滑
    # 2. 强化形态学操作（Opening + Closing 去毛边）
    kernel = np.ones((7, 7), np.uint8)  # 由 (3,3) 提高到 (7,7)
    opening = cv2.morphologyEx(mean_shift, cv2.MORPH_OPEN, kernel, iterations=3)  # 迭代 3 次
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=3)  # 迭代 3 次
    return closing


def find_pod_endpoints(cnt, epsilon=8, target_angle=120):
    # 使用 epsilon进行多边形逼近
    poly = cv2.approxPolyDP(cnt, epsilon, True)

    # 计算每个逼近点与相邻两点形成的夹角
    endpoints = []
    num_points = len(poly)
    for i in range(num_points):
        # 获取当前点及其相邻两点
        p1 = poly[(i - 1) % num_points][0]  # 前一个点
        p2 = poly[i][0]  # 当前点
        p3 = poly[(i + 1) % num_points][0]  # 后一个点

        # 计算向量 p2p1 和 p2p3
        vec1 = np.array(p1) - np.array(p2)
        vec2 = np.array(p3) - np.array(p2)

        # 计算向量的模
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)

        # 计算夹角（弧度）
        dot_product = np.dot(vec1, vec2)
        angle_rad = math.acos(dot_product / (norm_vec1 * norm_vec2))
        # 转换为角度
        angle_deg = math.degrees(angle_rad)

        # 判断是否为锐角（小于90度）
        if angle_deg < target_angle:
            endpoints.append(p2)

    if len(endpoints) < 2:
        return endpoints, poly
    max_pair = (0, 1)  # 存储最大距离对应的两个点的索引
    # 如果有多个端点，存储相距最远的两个端点
    if len(endpoints) > 2:
        max_dist = 0
        for i in range(len(endpoints)):
            for j in range(i + 1, len(endpoints)):
                dist = np.sqrt((endpoints[i][0] - endpoints[j][0]) ** 2 + (endpoints[i][1] - endpoints[j][1]) ** 2)
                if dist > max_dist:
                    max_dist = dist
                    max_pair = (i, j)  # 记录最远的两个点的索引
    endpoints = [endpoints[max_pair[0]], endpoints[max_pair[1]]]

    return endpoints, poly


def compute_arc_length(segment):
    """
    计算连续点段的弧长（欧氏距离累加）。
    :param segment: 输入一个包含多个坐标点的数组
    :return: 返回该点段的弧长
    """
    return np.sum(np.sqrt(np.sum(np.diff(segment, axis=0) ** 2, axis=1)))


def compute_inner_arc_length(cnt, endpoints):
    # 计算距离endpoints[0]最近的轮廓点，并返回其索引
    idx1 = np.argmin(np.linalg.norm(cnt - endpoints[0], axis=1))
    idx2 = np.argmin(np.linalg.norm(cnt - endpoints[1], axis=1))
    if idx1 < idx2:
        segment1 = cnt[idx1:idx2 + 1]
        segment2 = np.concatenate((cnt[idx2:], cnt[:idx1 + 1]), axis=0)
    else:
        segment1 = cnt[idx2:idx1 + 1]
        segment2 = np.concatenate((cnt[idx1:], cnt[:idx2 + 1]), axis=0)

    arc_length1 = compute_arc_length(segment1)
    arc_length2 = compute_arc_length(segment2)

    inner_arc = segment1 if arc_length1 < arc_length2 else segment2

    return inner_arc, min(arc_length1, arc_length2)


def find_maximum_inscribed_circle(contour, binary_mask):
    """
    计算轮廓中的最大内切圆
    :param contour: 物体的轮廓 (numpy array)
    :param binary_mask: 该物体的二值掩码图像
    :return: (cx, cy, max_radius) 最大内切圆的圆心坐标和半径
    """
    # 计算二值掩码的距离变换图
    dist_transform = cv2.distanceTransform(binary_mask, cv2.DIST_L2, 5)

    # 找到最大值的位置（即最大内切圆的圆心）
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(dist_transform)
    cx, cy = max_loc  # 圆心坐标
    max_radius = int(max_val)  # 半径（取整）

    return cx, cy, max_radius
def compute_hsv_green(image, mask):
    """ 计算豆荚的平均绿色程度（基于 HSV） """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # 转换到 HSV
    h, s, v = cv2.split(hsv)  # 分离通道

    # 计算 H（色调）在绿色范围（35-85）内的平均值
    green_mask = (h >= 35) & (h <= 85)  # 绿色范围
    green_hue_mean = np.mean(h[green_mask & (mask > 0)]) if np.any(green_mask & (mask > 0)) else 0

    # 计算 S（饱和度）均值（只计算绿色区域）
    green_saturation_mean = np.mean(s[green_mask & (mask > 0)]) if np.any(green_mask & (mask > 0)) else 0

    return green_hue_mean, green_saturation_mean

def process_image(image, epsilon=8, target_angle=100):
    # 读取图像

    h, w = image.shape[:2]
    display_cv2("src", image)
    # 应用平滑处理
    blurred_image = apply_strong_smoothing(image)
    display_cv2("blurred_image", blurred_image)
    # 图像预处理
    gray = cv2.cvtColor(blurred_image, cv2.COLOR_BGR2GRAY)
    display_cv2("gray", gray)
    th = 20
    _, binary = cv2.threshold(gray, th, 255, cv2.THRESH_BINARY)
    display_cv2("binary", binary)
    # 轮廓检测
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # print(f"轮廓数量: {len(contours)}")
    result_image = image.copy()
    # 多边形逼近处理并识别端点
    handle_id = 0

    # 初始化累计变量
    total_width = 0
    total_height = 0
    total_inner_length = 0
    total_diameter = 0
    total_lustre = 0
    pod_count = 0
    for cnt in contours:
        if len(cnt) < 200: continue
        cnt = cnt.squeeze()
        # 计算外接矩形（最小面积矩形）
        rect = cv2.minAreaRect(cnt)
        width = min(rect[1])
        height = max(rect[1])
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        width_cm = width * 0.01
        height_cm = height * 0.01

        # 单独创建这个豆荚的mask
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [cnt], -1, 255, thickness=cv2.FILLED)
        display_cv2("mask", mask)
        # 找到最小内切圆心和半径
        cx, cy, radius = find_maximum_inscribed_circle(cnt, mask)
        print(cx, cy, radius)
        # 返回最小翠绿程度
        avg_hue, avg_sat = compute_hsv_green(image, mask)
        lustre = avg_hue * avg_sat
        endpoints = []
        poly = None

        cur_angle = target_angle

        # # 画出轮廓检测
        # cv2.drawContours(result_image, [cnt], 0, (0, 255, 0), 2)
        # display_cv2("contours", result_image)

        while True:
            endpoints, poly = find_pod_endpoints(cnt, epsilon, cur_angle)
            tmg = result_image.copy()
            # 在tmg上画出多边形
            cv2.drawContours(tmg, [poly], 0, (0, 255, 0), 2)
            display_cv2(f"tmg{handle_id}", tmg)
            handle_id += 1
            if len(endpoints) >= 2:
                break
            else:
                cur_angle += 5

        print(endpoints)

        inner_arc, arc_length = compute_inner_arc_length(cnt, endpoints)
        inner_length_cm = arc_length * 0.01

        while inner_length_cm < height_cm:
            cur_angle += 5
            endpoints, poly = find_pod_endpoints(cnt, epsilon, cur_angle)

            tmg = result_image.copy()
            # 在tmg上画出多边形
            cv2.drawContours(tmg, [poly], 0, (0, 255, 0), 2)
            display_cv2(f"tmg{handle_id}", tmg)
            handle_id += 1

            inner_arc, arc_length = compute_inner_arc_length(cnt, endpoints)
            inner_length_cm = arc_length * 0.01

        print(inner_length_cm, width_cm, height_cm, cur_angle)
        # 绘制端点
        for ep in endpoints:
            cv2.circle(result_image, tuple(ep), 10, (0, 0, 255), -1)  # 用红色圆点标记端点
        display_cv2("endpoints", result_image)

        # 画出多边形图像
        cv2.drawContours(result_image, [poly], 0, (0, 255, 0), 2)
        display_cv2("poly", result_image)

        # 绘制内弧
        inner_arc_draw = inner_arc.astype(np.int32).reshape(-1, 1, 2)
        cv2.polylines(result_image, [inner_arc_draw], False, (0, 0, 255), 2)

        # 下面代码是单独生成内弧图片
        t_img = image.copy()
        # 绘制端点
        for ep in endpoints:
            cv2.circle(t_img, tuple(ep), 10, (0, 0, 255), -1)  # 用红色圆点标记端点
        cv2.polylines(t_img, [inner_arc_draw], False, (0, 0, 255), 2)
        display_cv2("inner_arc", t_img)

        cv2.drawContours(result_image, [box], 0, (0, 255, 0), 2)
        cv2.circle(result_image, (cx, cy), radius, (255, 245, 0), 2)
        display_cv2("box", result_image)

        # 累加统计
        total_width += width_cm
        total_height += height_cm
        total_inner_length += inner_length_cm
        total_diameter += 2 * radius * 0.01  # 换成 cm
        total_lustre += lustre
        pod_count += 1

    # 平均值计算（避免除零）
    if pod_count > 0:
        result = {
            "width": round(total_width / pod_count, 2),
            "height": round(total_height / pod_count, 2),
            "inner_length": round(total_inner_length / pod_count, 2),
            "diameter": round(total_diameter / pod_count, 2),
            "lustre": round(total_lustre / pod_count, 2),
            "pod_count": pod_count,  # 整数不需要 round
            "pic": result_image,  # 图片不用管
        }
    else:
        result = {
            "width": 0.00,
            "height": 0.00,
            "inner_length": 0.00,
            "diameter": 0.00,
            "lustre": 0.00,
            "pod_count": 0,
            "pic": result_image,
        }

    return result






# epsilon = 8
# target_angle = images
# image_path = '10078466.jpg'
# output_path = 'result.png'
# process_image(image_path, output_path, epsilon, target_angle)  # 处理图片并保存结果

# batch_process_images(input_folder, output_folder)  # 调用批量处理函数




