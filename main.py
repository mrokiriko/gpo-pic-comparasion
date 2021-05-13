from PIL import Image
import imagehash
from os import listdir
from os.path import isfile, join

folder_path = 'compare_pics'


# def are_similar_phash(pic_a, pic_b, folder_path):
#     # ToDo try out other image hashing
#     # https://pypi.org/project/ImageHash/
#     pic_a_path = folder_path + '/' + pic_a
#     pic_b_path = folder_path + '/' + pic_b
#     pic_a_hash = get_imagehash(pic_a_path)
#     pic_b_hash = get_imagehash(pic_b_path)
#     # return pic_a_hash == pic_b_hash
#     return abs(pic_a_hash - pic_b_hash) < 10


def are_similar_hashes(hash_a, hash_b):
    # return hash_a == hash_b
    return abs(hash_a - hash_b) < 10


def get_imagehash(pic):
    return imagehash.phash(Image.open(pic))


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def is_pic(path):
    if '.DS_Store' in path:
        return False
    return isfile(path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    pics = [f for f in listdir(folder_path) if is_pic(join(folder_path, f))]
    pics.sort()
    # pics = pics[0:8]
    # pics = chunks(pics, 4)

    comparisons = 0
    comparisons_correct = 0

    pics_hashes = []
    for index, pic in enumerate(pics):
        pic_path = folder_path + '/' + pic
        pics_hashes.append(get_imagehash(pic_path))

    for index_a, hash_a in enumerate(pics_hashes):
        # print(index_a, '-', pic_a)
        for index_b, hash_b in enumerate(pics_hashes):
            comparisons += 1
            are_similar = index_a // 4 == index_b // 4
            are_similar_by_hash = are_similar_hashes(hash_a, hash_b)
            print(pics[index_a], '/', pics[index_b], '(', are_similar, ',', are_similar_by_hash, ')')

            if are_similar == are_similar_by_hash:
                comparisons_correct += 1

    correct_percent = round(comparisons_correct / comparisons * 100 * 100) / 100
    print('there were', comparisons, 'comparisons.', comparisons_correct, 'of them are correct', correct_percent, '%')

    # for index_a, pic_a in enumerate(pics):
    #     # print(index_a, '-', pic_a)
    #     for index_b, pic_b in enumerate(pics):
    #         comparisons += 1
    #         are_similar = index_a // 4 == index_b // 4
    #         are_similar_by_hash = are_similar_phash(pic_a, pic_b, folder_path)
    #         print(pic_a, '/', pic_b, '(', are_similar, ',', are_similar_by_hash, ')')
    #
    #         if are_similar == are_similar_by_hash:
    #             comparisons_correct += 1


        # for pic in chunk:
        #     print(pic)
            # get_chunk[pic] = index


    # for chunk_a in pics:
    #     print('chunk_a', chunk_a)
    #     for pic_a in chunk_a:
    #         print(pic_a)
    #         for chunk_b in pics:
    #             print('chunk_b', chunk_b)
                # for pic_b in chunk_b:
                #     print(pic_a, pic_b)

    # pic_path = folder_path + '/' + 'bgyg1.jpg'
    # pic_hash = imagehash.phash(Image.open(pic_path))
    # print(pic_hash)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
