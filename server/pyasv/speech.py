import librosa
import numpy as np
import logging
import os
import h5py
from abc import abstractmethod
from pyasv.basic import ops
from pyasv.pipeline import TFrecordGen
from pyasv.pipeline import TFrecordClassBalanceGen


def audio_time_limit(data, length):
    """padding audio with specified length"""
    assert isinstance(data, np.ndarray)
    if len(data) < length: data = np.concatenate([data, np.zeros(dtype=data.dtype, shape=(length,))], axis=0)
    return data[:length]


def slide_windows(feature, slide_window):
    if type(feature) != np.ndarray: feature = np.array(feature)
    result_ = []
    if slide_window is not None:
        l, r = slide_window
        for i in range(feature.shape[0] - r):
            if i >= l: result_.append(np.array(feature[i - l:i + r + 1]))
        result = np.array(result_)
    else:
        result = feature
    return result


class FeatureExtractor:
    """Base class for feature extracting."""
    def __init__(self, url_folder, config, file_name):
        self.url_folder = url_folder
        self.config = config
        self.n_fft = 512 if config.n_fft is None else config.n_fft
        self.process_num = 10 if config.n_threads is None else config.n_threads
        self.fix_len = None if config.fix_len is None else config.fix_len
        self.sample_rate = config.sample_rate
        if self.fix_len is not None:
            self.fix_len = self.sample_rate * self.fix_len
        self.dims = config.feature_dims
        self.slides = [None, None] if config.slides is None else config.slides
        self.logger = logging.getLogger("data")
        self.file_name = file_name

    @abstractmethod
    def extract(self, url_list):
        """Method of extract feature, need to be overrided. Given url_list is [(url, label), ....], should return list of feature."""
        pass

    def read_url_file(self):
        """Read and parse self.url_folder. url file name should like train_%d.scp, enroll... each line contain wav path and it's speaker """
        files = os.listdir(self.url_folder)
        self.logger.info(files)
        train_urls, enroll_urls, test_urls = [], [], []
        for f in files:
            if f[:5] == 'train':
                with open(os.path.join(self.url_folder, f)) as data:
                    train_urls.append(list(map(lambda x: (str(x.split(' ')[0]), int(x.split(' ')[1])),
                                               data.read().splitlines())))
            elif f[:4] == 'test':
                with open(os.path.join(self.url_folder, f)) as data:
                    enroll_urls.append(list(map(lambda x: (str(x.split(' ')[0]), int(x.split(' ')[1])),
                                                data.read().splitlines())))
            elif f[:6] == 'enroll':
                with open(os.path.join(self.url_folder, f)) as data:
                    test_urls.append(list(map(lambda x: (str(x.split(' ')[0]), int(x.split(' ')[1])),
                                              data.read().splitlines())))
        return train_urls, test_urls, enroll_urls

    def extract_h5(self, urls):
        """Use this method to extract feature to a h5 file, recommend for storing test set and enroll set."""
        h5_file = h5py.File(os.path.join(self.config.save_path, 'data', self.file_name + '.h5'))
        for i in range(len(urls)):
            data, label = self.extract(urls[i])
            if i == 0:
                h5_file.create_dataset("data", data=data)
                h5_file.create_dataset("label", data=label)
            else:
                data = np.concatenate([h5_file['data'].value, data], axis=0)
                label = np.concatenate([h5_file['label'].value, label], axis=0)
                h5_file['data'] = data
                h5_file['label'] = label
            self.logger.info("Extracted %d url of %s set." % (i + 1, self.file_name))

    def extract_rcd(self, urls):
        """Use this method to extract feature to a rcd file, recommend for storing train set."""
        generator = TFrecordGen(self.config, self.file_name + '.rcd')
        for i in range(len(urls)):
            data, label = self.extract(urls[i])
            generator.write(data, label)

    def extract_class_balance_rcd(self, urls):
        """Use this method to extract feature to a rcd file, recommend for storing train set."""
        generator = TFrecordClassBalanceGen(self.config, self.file_name)
        for i in range(len(urls)):
            data, label = self.extract(urls[i])
            generator.write(data, label)


class FilterBank(FeatureExtractor):
    """Class for extracting fbank feature."""
    def __init__(self, url_folder, config, file_name='train'):
        super().__init__(url_folder, config, file_name)

    @staticmethod
    def _extract_one(url, sample_rate, n_fft, n_mels, length=None):
        y, sr = librosa.load(url, sr=sample_rate)
        y *= 0.2
        librosa.output.write_wav(path=url.split("/")[-1], y=y, sr=sr)
        if length is not None:
            y = audio_time_limit(y, length)
        fbank = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft, n_mels=n_mels).T
        return np.squeeze(fbank)

    def extract(self, url_list):
        labels = [item[1] for item in url_list]
        url_list = [item[0] for item in url_list]
        self.logger.info("Start extract %d audio." % len(url_list))
        param = zip(url_list, [self.sample_rate for i in range(len(url_list))],
                    [self.n_fft for i in range(len(url_list))],
                    [self.dims for i in range(len(url_list))],
                    [self.fix_len for i in range(len(url_list))])
        fbanks = ops.multi_processing(self._extract_one, param, self.process_num)
        if self.slides != [None, None] and self.slides != [0, 0]:
            slides = [self.slides for i in range(len(fbanks))]
            fbanks = ops.multi_processing(slide_windows, zip(fbanks, slides), self.process_num)
        return fbanks, labels


class MFCC(FeatureExtractor):
    """Class for extracting MFCC feature"""
    def __init__(self, url_folder, config, file_name='train'):
        super().__init__(url_folder, config, file_name)

    @staticmethod
    def _extract_one(url, sample_rate, n_fft, n_mels, length=None):
        y, sr = librosa.load(url, sr=sample_rate)
        if length is not None:
            y = audio_time_limit(y, length)
        fbank = librosa.feature.melspectrogram(y, sr=sr, n_fft=n_fft, n_mels=n_mels)
        mfcc = librosa.feature.mfcc(S=fbank, sr=sr)
        mfcc_delta_1 = librosa.feature.delta(mfcc)
        mfcc_delta_2 = librosa.feature.delta(mfcc, order=2)
        return np.concatenate(np.stack([mfcc, mfcc_delta_1, mfcc_delta_2]), 1)

    def extract(self, url_list):
        labels = [item[1] for item in url_list]
        url_list = [item[0] for item in url_list]
        self.logger.info("Start extract %d audio." % len(url_list))
        param = zip(url_list, [self.sample_rate for i in range(len(url_list))],
                    [self.n_fft for i in range(len(url_list))],
                    [self.dims for i in range(len(url_list))],
                    [self.fix_len for i in range(len(url_list))])
        mfccs = ops.multi_processing(self._extract_one, param, self.process_num)
        if self.slides != [None, None] and self.slides != [0, 0]:
            slides = [self.slides for i in range(len(mfccs))]
            mfccs = ops.multi_processing(slide_windows, zip(mfccs, slides), self.process_num)
        return mfccs, labels


class STFTSourceSparation(FeatureExtractor):
    """Class for extracting STFT spectrogram for source sparation model"""
    def __init__(self, url_folder, config, source_num=2, use_log=True, file_name='train'):
        super().__init__(url_folder, config, file_name)
        self.source_num = source_num

    @staticmethod
    def url_pair(url_list, source_num):
        paired_data = []
        for i in url_list:
            paired_data.append([i[0]])
            for i in range(source_num-1):
                j = i
                while j[1] == i[1]: j = url_list[np.random.randint(0, len(url_list-1))]
                paired_data.append(j[0])
        return paired_data
            
    @staticmethod
    def _extract_one(url_pair, sample_rate, n_fft, hop_length, length=None,
                     db_func=librosa.amplitude_to_db, use_log=True):
        source_nums = len(url_pair)
        def get_mag(url):
            y, _ = librosa.load(url, sr=sample_rate)
            complex_spec = librosa.core.stft(y, n_fft=n_fft, win_length=n_fft, hop_length=hop_length)
            mag_spec = np.abs(complex_spec)
            if use_log:  mag_spec = db_func(mag_spec)
            return mag_spec
        def get_label(data_dic):
            Y = [data['s_%d']%i for i in range(source_nums)]
            max_labels = np.amax(np.stack(Y).T, -1)
            Y = np.array(Y == max_labels, np.int32)
            return Y
        data = {'s_%d'%i: get_mag(url_pair[i]) for i in range(source_nums)}
        label = get_label(data)
        return {'data':data, 'label': label}
    
    def extract(self, url_list):
        paired_data = self.url_pair(url_list, self.source_num)
        self.logger.info("Start extract %d audio." % len(url_list))
        param = zip(paired_data, 
                    [self.sample_rate for i in range(len(url_list))],
                    [self.n_fft for i in range(len(url_list))],
                    [self.dims for i in range(len(url_list))],
                    [self.config.hop_length for i in range(url_list)],
                    [self.fix_len for i in range(len(url_list))])
        spec_dic = ops.multi_processing(self._extract_one, param, self.process_num)
        return spec_dic['data'], spec_dic['label']
