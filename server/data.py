import pickle
import numpy as np


class Speakers:
    def __init__(self, info_path, vec_path):
        self.info_path = info_path
        self.vec_path = vec_path
        try:
            with open(info_path, 'rb') as f:
                self.spkr = pickle.load(f)
            self.vectors = np.load(vec_path).item()
        except FileNotFoundError:
            self.spkr = []
            self.vectors = {}
            print("Warning. file not found.")

    def dump(self, data=None, path=None):
        if data is None or path is None:
            data = self.spkr
            path = self.info_path
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def add(self, dic):
        for spkr in self.spkr:
            print(spkr)
            print(dic)
            if dic['name'] == spkr['name']:
                spkr['number'] += 1
                self.dump(self.spkr, self.info_path)
                return
        dic['number'] = 1
        self.spkr.append(dic)
        self.dump(self.spkr, self.info_path)
        return

    def to_options(self):
        return list({'label': s['name'], 'value': s['name']} for s in self.spkr)

    def to_table(self):
        return self.spkr

    def remove(self, name):
        try:
            new_lis = []
            for i in self.spkr:
                if i['name'] != name:
                    new_lis.append(i)
            self.spkr = new_lis
            try:
                del self.vectors[name]
            except:
                pass
            self.dump(self.spkr, self.info_path)
        except:
            pass

    def update_vector_file(self):
        np.save("vector", np.array(self.vectors))
        return


if __name__ == '__main__':
    spkr = Speakers(info_path='spkr.pkl', vec_path='vec.npy')
    dates = ["2019-8-16 0:51:23", "2019-8-16 0:41:23"]
    names = ["yes", 'no']
    numbers = [1, 2]
    data = [{'date': date, 'name': name, 'number': number} for date, name, number in zip(dates, names, numbers)]
    for i in data:
        spkr.add(i)
