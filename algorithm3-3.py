from PIL import Image
import imagehash
from os import listdir
import sys
import time
import cv2
import numpy as np
import time

# SIFT algorithm
# Добавление гистограммы в SIFT

sift = cv2.SIFT_create()
# feature matching
bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

index_params = dict(algorithm=0, trees=5)
search_params = dict()
flann = cv2.FlannBasedMatcher(index_params, search_params)


MIN_RES = 300
DIST_RATIO = 0.6
MATCHES_THRESHOLD = 8


def get_hist(img):
    img = cv2.imread(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # extract a 3D RGB color histogram from the image,
    # using 8 bins per channel, normalize, and update
    # the index
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    return cv2.normalize(hist, hist).flatten()


def get_imagehash(pic):
    return imagehash.phash(Image.open(pic))


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
    # folder = 'exact_pics' # sys.argv[1]
    folder = 'tineye' # sys.argv[1]

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

    hists = {}
    keypoints = {}
    descriptors = {}
    categories = {}
    start_time = time.time()

    compare_time_sum = 0
    fill_time_sum = 0

    # pics = pics[:50]
    # pics = pics[:30]
    # pics = pics[-30:]
    # pics = pics[:20] + pics[-20:]
    # pics = pics[:30]
    for pic_a in pics:
        for pic_b in pics:
            # category_a = pic_a.split("_")[0]
            # category_b = pic_b.split("_")[0]
            category_a = pic_a.split(" ")[0]
            category_b = pic_b.split(" ")[0]
            are_same = category_a == category_b

            start = time.time()

            if pic_a not in descriptors:
                keypoints[pic_a], descriptors[pic_a] = get_descriptor_from_file(folder + '/' + pic_a)

            if pic_b not in descriptors:
                keypoints[pic_b], descriptors[pic_b] = get_descriptor_from_file(folder + '/' + pic_b)

            if pic_a not in hists:
                hists[pic_a] = get_hist(folder + '/' + pic_a)

            if pic_b not in hists:
                hists[pic_b] = get_hist(folder + '/' + pic_b)

            end = time.time()
            fill_time_sum += end - start

            comparisons += 1

            start = time.time()
            found_same = False
            good_points_number = '-'
            hist_compare = cv2.compareHist(hists[pic_a], hists[pic_b], cv2.HISTCMP_BHATTACHARYYA)

            # # print('hash_diff:', hash_diff)
            # if hash_diff < 10:
            #     found_same = True
            # else:

            # if hash_diff >= 40:
            #     found_same = False

            # if hash_diff < 35:
            # el

            if hist_compare > 0.8:
                found_same = False
            else:
                good_points_number = get_good_points(descriptors[pic_a], descriptors[pic_b])
                found_same = good_points_number > MATCHES_THRESHOLD

                # found_same = are_same_descriptors(descriptors[pic_a], descriptors[pic_b])

            end = time.time()
            compare_time_sum += end - start

            if are_same != found_same:
                print('compare ' + pic_a + ' and ' + pic_b)
                print('result, are they same?', found_same)
                print("good points:", good_points_number)
                print('hist_compare:', hist_compare)
                print('')

            # print("good points:", good_points_number)

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

    print('время потраченное на сравнение изображений:', compare_time_sum)
    print('время потраченное на обработку изображений для заполнения бд:', fill_time_sum)
    print('сравнения похожих изображений:', same_comparisons)
    print('угадал что два изображения похожи:', right_same_comparisons)
    print('не угадал что два изображения похожи:', wrong_same_comparisons)
    print('')
    print('сравнения разных изображений:', difference_comparisons)
    print('угадал что изображения разные:', right_difference_comparisons)
    print('не угадал что изображения разные:', wrong_difference_comparisons)
    print('')
    print('categories:')
    print(categories)
    # print('matches_for_same')
    # print(matches_for_same)
    # print('matches_for_diff')
    # print(matches_for_diff)
