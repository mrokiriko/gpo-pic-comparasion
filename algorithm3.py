from PIL import Image
import imagehash
from os import listdir
import sys
import time
import cv2
import numpy as np

# SIFA algorithm

sift = cv2.SIFT_create()
# feature matching
bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

index_params = dict(algorithm=0, trees=5)
search_params = dict()
flann = cv2.FlannBasedMatcher(index_params, search_params)


MIN_RES = 300
DIST_RATIO = 0.6
MATCHES_THRESHOLD = 10


def get_descriptor_from_file(filepath):
    image = cv2.imread(filepath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    img_height = np.size(image, 0)
    img_width = np.size(image, 1)

    downscale = 1
    if img_height > MIN_RES:
        downscale = int(img_height / MIN_RES)
    elif img_width > MIN_RES:
        downscale = int(img_width / MIN_RES)

    dimensions = (int(img_width / downscale), int(img_height / downscale))

    image = cv2.resize(image, dimensions, interpolation=cv2.INTER_AREA)
    return get_descriptor(image)


def get_descriptor(image):
    return sift.detectAndCompute(image, None)


def get_good_points(descriptor_a, descriptor_b):
    matches = flann.knnMatch(descriptor_a, descriptor_b, k=2)
    good_points = []
    for m, n in matches:
        if m.distance < DIST_RATIO * n.distance:
            good_points.append(m)
    return len(good_points)


def are_same_descriptors(descriptor_a, descriptor_b):
    return get_good_points(descriptor_a, descriptor_b) > MATCHES_THRESHOLD

    # matches = bf.match(descriptor_a, descriptor_b)
    matches = sorted(matches, key=lambda x: x.distance)
    # return len(matches) > 300


if __name__ == '__main__':
    folder = 'exact_pics' # sys.argv[1]

    pics = listdir(folder)

    comparisons = 0
    same_comparisons = 0
    right_same_comparisons = 0
    wrong_same_comparisons = 0
    difference_comparisons = 0
    right_difference_comparisons = 0
    wrong_difference_comparisons = 0

    matches_for_same = []
    matches_for_diff = []

    keypoints = {}
    descriptors = {}
    categories = {}
    start_time = time.time()

    compare_time_sum = 0
    fill_time_sum = 0

    # pics = pics[:30]
    for pic_a in pics:
        for pic_b in pics:
            category_a = pic_a.split("_")[0]
            category_b = pic_b.split("_")[0]
            are_same = category_a == category_b

            print('compare ' + pic_a + ' and ' + pic_b)

            start = time.time()

            if pic_a not in descriptors:
                keypoints[pic_a], descriptors[pic_a] = get_descriptor_from_file(folder + '/' + pic_a)

            if pic_b not in descriptors:
                keypoints[pic_b], descriptors[pic_b] = get_descriptor_from_file(folder + '/' + pic_b)

            comparisons += 1

            end = time.time()
            fill_time_sum += end - start


            start = time.time()

            # found_same = are_same_descriptors(descriptors[pic_a], descriptors[pic_b])
            good_points_number = get_good_points(descriptors[pic_a], descriptors[pic_b])
            found_same = good_points_number > MATCHES_THRESHOLD
            print("good points:", good_points_number)

            end = time.time()
            compare_time_sum += end - start


            # found_same = are_same_descriptors(descriptors[pic_a], descriptors[pic_b])

            # matches_len = len(bf.match(descriptors[pic_a], descriptors[pic_b]))

            stat = [0, 0, 0, 0]
            if category_a in categories:
                stat = categories[category_a]

            if are_same:
                same_comparisons += 1
                matches_for_same.append(good_points_number)

                if are_same == found_same:
                    right_same_comparisons += 1
                    stat[0] += 1
                else:
                    wrong_same_comparisons += 1
                    stat[1] += 1
            else:
                difference_comparisons += 1
                matches_for_diff.append(good_points_number)

                if are_same == found_same:
                    right_difference_comparisons += 1
                    stat[2] += 1
                else:
                    wrong_difference_comparisons += 1
                    stat[3] += 1

            categories[category_a] = stat

    print('?????????? ?????????????????????? ???? ?????????????????? ??????????????????????:', compare_time_sum)
    print('?????????? ?????????????????????? ???? ?????????????????? ?????????????????????? ?????? ???????????????????? ????:', fill_time_sum)
    print('?????????????????? ?????????????? ??????????????????????:', same_comparisons)
    print('???????????? ?????? ?????? ?????????????????????? ????????????:', right_same_comparisons)
    print('???? ???????????? ?????? ?????? ?????????????????????? ????????????:', wrong_same_comparisons)
    print('')
    print('?????????????????? ???????????? ??????????????????????:', difference_comparisons)
    print('???????????? ?????? ?????????????????????? ????????????:', right_difference_comparisons)
    print('???? ???????????? ?????? ?????????????????????? ????????????:', wrong_difference_comparisons)
    print('')
    # print('matches_for_same')
    # print(matches_for_same)
    # print('matches_for_diff')
    # print(matches_for_diff)
