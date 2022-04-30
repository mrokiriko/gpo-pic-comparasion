import cv2
import numpy as np
from matplotlib import pyplot as plt


def are_same(img, template, threshold=0.8, resize_iterations=1, step=0.01):
    img_height = np.size(img, 0)
    img_width = np.size(img, 1)

    percent = 0.2
    template = get_template(template, percent)

    template_height = np.size(template, 0)
    template_width = np.size(template, 1)

    print('template itself width and height:')
    print(template_width, template_height)

    # во сколько раз надо уменьшить шаблон или итогове изображение
    scalability_h = img_height / (template_height / (2 * percent))
    scalability_w = img_width / (template_width / (2 * percent))
    print('scalability_h', scalability_h)
    print('scalability_w', scalability_w)

    scalability = scalability_h

    if scalability_h > 1:
        dim = (int(img_width / scalability), int(img_height / scalability))
        img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    else:
        dim = (int(template_width * scalability), int(template_height * scalability))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

    for i in range(0, resize_iterations):

        print('iteration #', i)

        template_height = np.size(template, 0)
        template_width = np.size(template, 1)

        dim = (int(template_width * (1 - step * i)), int(template_height * (1 - step * i)))
        template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)

        cv2.imshow('in this image', img)
        cv2.waitKey(0)
        cv2.imshow('search for this template', template)
        cv2.waitKey(0)

        if are_same_iteration(img, template, threshold):
            return True

    return False


def are_same_iteration(img, template, threshold=0.8):
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    print(res)
    loc = np.where(res >= threshold)

    # print('loc')
    # print(loc)

    found_templates = 0

    # сюда занесем первую точку найденного шаблона
    first_x = -1
    first_y = -1

    # здесь хранятся максимальные отступы от первой точки
    x_diff = 0
    y_diff = 0

    w, h = template.shape[::-1]

    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        found_templates += 1

        if first_y < 0 and first_x < 0:
            first_x = pt[0]
            first_y = pt[1]

        x_change = abs(first_x - pt[0])
        y_change = abs(first_y - pt[1])

        if x_change > x_diff:
            x_diff = x_change

        if y_change > y_diff:
            y_diff = y_change

        if found_templates > 20:
            break

    img_height = np.size(img, 0)
    img_width = np.size(img, 1)

    # в пределеах скольких пикселей мы считаем что все шаблоны найдены корректно
    x_tolerance = img_width * 0.03
    y_tolerance = img_height * 0.03

    print('found_templates:', found_templates)
    print('x_diff:', x_diff)
    print('y_diff:', y_diff)
    print('x_tolerance:', x_tolerance)
    print('y_tolerance:', y_tolerance)

    if found_templates > 0 and x_diff <= x_tolerance and y_diff <= y_tolerance:

        cv2.imshow('in this image', img)
        cv2.waitKey(0)

        return True

    return False


def get_template(template, percent):
    template_height = np.size(template, 0)
    template_width = np.size(template, 1)

    if template_height < template_width:
        square_half_side = int(template_height * percent / 2)
    else:
        square_half_side = int(template_width * percent / 2)

    # вырезать квадрат посередине изображения-шаблона
    height_from = int((template_height / 2) - square_half_side)
    height_to = int((template_height / 2) + square_half_side)
    width_from = int((template_width / 2) - square_half_side)
    width_to = int((template_width / 2) + square_half_side)

    # print('img.shape')
    # print(img.shape)
    # print(height_from, height_to, height_to - height_from)
    # print(width_from, width_to, width_to - width_from)
    #
    # print('img width and height:')
    # print(img_width, img_height)
    # print('template image width and height:')
    # print(template_width, template_height)

    return template[height_from:height_to, width_from:width_to]


# img2 = img.copy()

# img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# cv2.imshow('img before squarable', img)
# cv2.waitKey(0)

# превратить изображение в квадрат
# if img_height < img_width:
#     img = img[0:img_height, int(img_width / 2 - img_height / 2):int(img_width / 2 + img_height / 2)]
# else:
#     img = img[int(img_height / 2 - img_width / 2):int(img_height / 2 + img_width / 2), 0:img_width]

# cv2.imshow('img after squarable', img)
# cv2.waitKey(0)


# высота и ширина шаблона будет 40 процентов от изначального изображения

img = cv2.imread('exact_pics/spidermanpoint_04.jpg', 0)
template = cv2.imread('exact_pics/spidermanpoint_01.jpg', 0)

min_size = 400

img_height = np.size(img, 0)
img_width = np.size(img, 1)
if img_height > min_size:
    scalability = img_height / min_size
    dim = (int(img_width / scalability), int(img_height / scalability))
    img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)


template_height = np.size(template, 0)
template_width = np.size(template, 1)
if template_height > min_size:
    scalability = template_height / min_size
    dim = (int(template_width / scalability), int(template_height / scalability))
    template = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)


if are_same(img, template, 0.9, 8, 0.02):
    print('Same Images')
else:
    print('images are not the same')

cv2.imshow('in this image', img)
cv2.waitKey(0)
# cv2.imshow('search for this template', template)
# cv2.waitKey(0)
exit()



# methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
# for meth in methods:
#     img = img2.copy()
#     method = eval(meth)
#     # Apply template Matching
#     res = cv2.matchTemplate(img, template, method)
#
#
#     print(meth)
#     print(1 - res)
#     (min_x, max_y, minloc, maxloc) = cv2.minMaxLoc(res)
#     (x, y) = minloc
#     #print(maxloc)
#     print(cv2.minMaxLoc(res))
#
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#     # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
#     if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
#         top_left = min_loc
#     else:
#         top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)
#     cv2.rectangle(img, top_left, bottom_right, 255, 2)
#     plt.subplot(121), plt.imshow(res, cmap='gray')
#     plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
#     plt.subplot(122), plt.imshow(img, cmap='gray')
#     plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
#     plt.suptitle(meth)
#     plt.show()
