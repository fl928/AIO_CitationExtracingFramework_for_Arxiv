from parser import *
from multiprocessing import Pool
from tqdm import tqdm
import tarfile
import subprocess
import argparse
import json
import os


class processor:
    def __init__(self, folder_path, result_path, file_name):
        self.read_path = folder_path + [w for w in os.listdir(folder_path) if '.' not in w][0] + '/'
        # file_name = file_name.replace('data_open_arxiv_src_arXiv_src_', '')
        file_name = file_name.replace('.tar', '.json')
        file_name = file_name.strip('Arxiv_data/')
        self.result_file = result_path + file_name
        self.error_result = result_path + file_name.strip('.json') + '_error.json'
        self.file = [w for w in os.listdir(self.read_path) if '.gz' in w]
        self.pdf = [w for w in os.listdir(self.read_path) if '.pdf' in w]

    @staticmethod
    def unzip(file):
        gzip = tarfile.open(file, 'r:gz')
        output_name = file.strip('.gz')
        gzip.extractall(output_name)
        gzip.close()

    @staticmethod
    def unzip_error_file(file):
        subprocess.call(['gunzip', file])

    def active_parser(self, log):
        try:
            if log[1]:
                text_parser = parser(self.read_path + log[0], True)
                txt_length, cit_dict, sentence_dict = ref_file = text_parser.logic_control
            else:
                text_parser = parser(self.read_path + log[0] + '/')
                txt_length, cit_dict, sentence_dict,ref_file = text_parser.logic_control
        except:
            txt_length = 0
            cit_dict = 'Error File'
            ref_file = 'Error File'
            sentence_dict = 'Error File'

        return log[0], txt_length, cit_dict, sentence_dict, ref_file

    def process(self):
        success_log = []
        failed_log = []
        for item in self.file:
            try:
                self.unzip(self.read_path + item)
                success_log.append((item.strip('.gz'), False))
            except:
                try:
                    self.unzip_error_file(self.read_path + item)
                    success_log.append((item.strip('.gz'), True))
                except:
                    failed_log.append(item)

        with Pool() as p:
            results = list(tqdm(p.imap(self.active_parser, success_log), total=len(self.file)))
            p.close()
            p.join()

        output_file = {}
        error_file = self.pdf
        for item in results:
            if item[2] == 'Error File':
                error_file.append(item[0])
            else:
                output_file[item[0]] = {"total_sentences": item[1], "citationID": item[2],'sentence':item[3], "refence": item[4]}

        with open(self.result_file, 'w') as f:
            json.dump(output_file, f)
            f.close()
        with open(self.error_result, 'w') as f:
            json.dump(error_file, f)
            f.close()


if __name__ == '__main__':
    ArgParser = argparse.ArgumentParser(description='Single Folder Parser')
    ArgParser.add_argument('--read_folder', type=str)
    ArgParser.add_argument('--write_folder', type=str)
    ArgParser.add_argument('--file_name', type=str)
    args = ArgParser.parse_args()
    new_processor = processor(args.read_folder, args.write_folder, args.file_name)
    new_processor.process()
