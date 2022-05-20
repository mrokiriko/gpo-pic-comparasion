from PIL import Image
import imagehash
from os import listdir
import sys
import time

# PHASH algorithm

if __name__ == '__main__':
    # folder = sys.argv[1]
    folder = 'exact_pics'
    # threshold = int(sys.argv[2])
    threshold = int(sys.argv[1])

    pics = listdir(folder)

    comparisons = 0
    same_comparisons = 0
    right_same_comparisons = 0
    wrong_same_comparisons = 0
    difference_comparisons = 0
    right_difference_comparisons = 0
    wrong_difference_comparisons = 0

    hashes = {}
    categories = {}
    start_time = time.time()

    for pic_a in pics:
        for pic_b in pics:
            category_a = pic_a.split("_")[0]
            category_b = pic_b.split("_")[0]
            are_same = category_a == category_b

            if pic_a not in hashes:
                hashes[pic_a] = imagehash.phash(Image.open((folder + '/' + pic_a)))

            if pic_b not in hashes:
                hashes[pic_b] = imagehash.phash(Image.open((folder + '/' + pic_b)))

            comparisons += 1

            found_same = abs(hashes[pic_a] - hashes[pic_b]) < threshold

            stat = [0, 0, 0, 0]
            if category_a in categories:
                stat = categories[category_a]

            if are_same:
                same_comparisons += 1

                if are_same == found_same:
                    right_same_comparisons += 1
                    stat[0] += 1
                else:
                    wrong_same_comparisons += 1
                    stat[1] += 1
            else:
                difference_comparisons += 1

                if are_same == found_same:
                    right_difference_comparisons += 1
                    stat[2] += 1
                else:
                    wrong_difference_comparisons += 1
                    stat[3] += 1

            categories[category_a] = stat

    print('сравнения похожих изображений:', same_comparisons)
    print('угадал что два изображения похожи:', right_same_comparisons)
    print('не угадал что два изображения похожи:', wrong_same_comparisons)
    print('')
    print('сравнения разных изображений:', difference_comparisons)
    print('угадал что изображения разные:', right_difference_comparisons)
    print('не угадал что изображения разные:', wrong_difference_comparisons)
