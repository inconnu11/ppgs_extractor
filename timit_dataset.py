import os
import numpy as np

TRAIN_FILE = '/media/luhui/experiments_data/librispeech/train.txt'
TEST_FILE = '/media/luhui/experiments_data/librispeech/dev.txt'
MFCC_DIR = '/media/luhui/experiments_data/librispeech/mfcc_hop12.5'
PPG_DIR = '/media/luhui/experiments_data/librispeech/phone_labels_hop12.5'
MFCC_DIM = 39
PPG_DIM = 345


def text2list(file):
    file_list = []
    with open(file, 'r') as f:
        for line in f:
            file_list.append(line.split()[0])
    return file_list


def onehot(arr, depth, dtype=np.float32):
    assert len(arr.shape) == 1
    onehots = np.zeros(shape=[len(arr), depth], dtype=dtype)
    onehots[np.arange(len(arr)), arr] = 1
    return onehots


def get_single_data_pair(fname, mfcc_dir, ppg_dir):
    assert os.path.isdir(mfcc_dir) and os.path.isdir(ppg_dir)
    mfcc_f = os.path.join(mfcc_dir, fname+'.npy')
    ppg_f = os.path.join(ppg_dir, fname+'.npy')
    mfcc = np.load(mfcc_f)
    # cut the MFCC into the same time length as PPGs
    # mfcc = mfcc[2:mfcc.shape[0]-3, :]
    ppg = np.load(ppg_f)
    ppg = onehot(ppg, depth=PPG_DIM)
    assert mfcc.shape[0] == ppg.shape[0]
    return mfcc, ppg


def train_generator():
    file_list = text2list(file=TRAIN_FILE)
    for f in file_list:
        mfcc, ppg = get_single_data_pair(f, mfcc_dir=MFCC_DIR, ppg_dir=PPG_DIR)
        yield mfcc, ppg, mfcc.shape[0]


def test_generator():
    file_list = text2list(file=TEST_FILE)
    for f in file_list:
        mfcc, ppg = get_single_data_pair(f, mfcc_dir=MFCC_DIR, ppg_dir=PPG_DIR)
        yield mfcc, ppg, mfcc.shape[0]


def tf_dataset():
    import tensorflow as tf
    batch_size = 128
    train_set = tf.data.Dataset.from_generator(train_generator,
                                               output_types=(
                                                   tf.float32, tf.float32, tf.int32),
                                               output_shapes=(
                                                   [None, MFCC_DIM], [None, PPG_DIM], []))
    train_set = train_set.padded_batch(batch_size,
                                       padded_shapes=([None, MFCC_DIM],
                                                      [None, PPG_DIM],
                                                      [])).repeat()
    train_iterator = train_set.make_initializable_iterator()
    batch_data = train_iterator.get_next()

    with tf.Session() as sess:
        sess.run(train_iterator.initializer)
        for i in range(10):
            data = sess.run(batch_data)
            print(data[0].shape, data[1].shape, data[2])
    return


if __name__ == '__main__':
    tf_dataset()
    # file_list = text2list(file=TEST_FILE)
    # for f in file_list:
    #     mfcc, ppg = get_single_data_pair(f, mfcc_dir=MFCC_DIR, ppg_dir=PPG_DIR)
    #     print(mfcc.shape, ppg.shape)
