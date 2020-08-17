import os
import chardet
import re


class parser:
    # initialize read path and write path, and condition
    def __init__(self, read_path, single_file=False):
        if not single_file:
            self.read_path = read_path
            self.content = os.listdir(read_path)
            self.scan_folder()
            self.whole_text = self.read_file(self.read_path + self.texName)
            self.cit_dict = {}
            self.sentence_dict = {}
        elif single_file:
            # Since some of unzipped item is a single latex file, we need to decide scan item or not
            self.read_path = read_path
            self.whole_text = self.read_file(self.read_path)
            self.hasBib = False
            self.cit_dict = {}
            self.sentence_dict = {}

    def scan_folder(self):
        self.hasBib = False
        self.BibName = ''
        tex_list = []
        for item in self.content:
            if '.bbl' in item:
                self.BibName = item
                self.hasBib = True
            if '.tex' in item:
                tex_list.append(item)
        if len(tex_list) == 1:
            self.texName = tex_list[0]
        else:
            self.texName = self.get_size(tex_list)

    @staticmethod
    def read_file(path):
        try:
            with open(path, 'r') as f:
                whole_text = f.read()
                f.close()
        except:
            with open(path, 'rb') as f:
                coding = f.read()
                f.close()
            char_encoding = chardet.detect(coding)['encoding']
            with open(path, 'r', encoding=char_encoding) as f:
                whole_text = f.read()
                f.close()
        return whole_text

    def get_size(self, tex_name):
        target = ''
        target_size = 0
        for item in tex_name:
            current_size = os.path.getsize(self.read_path + item)
            if current_size > target_size:
                target = item
                target_size = current_size
        return target

    def get_ref(self):
        if self.hasBib:
            bbl_path = self.read_path + self.BibName
            return self.read_file(bbl_path)
        else:
            if not re.findall(r'\\begin{thebibliography}', self.whole_text):
                return None
            else:
                begin_pos = re.finditer(r'\\begin{thebibliography}', self.whole_text)
                end_pos = re.finditer(r'\\end{thebibliography}', self.whole_text)
                for item in begin_pos:
                    new_text_end = item.start()
                    begin_index = item.end() + 1
                for item in end_pos:
                    end_index = item.start() - 1
                ref = self.whole_text[begin_index:end_index]
                self.whole_text = self.whole_text[:new_text_end]
                return ref

    @staticmethod
    def split_to_sentence(text):
        alphabets = "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        mathdot = "(?<=[0-9])+(\.)"
        text = " " + text + "  "
        text = text.replace("\n", " ")
        text = text.replace("\t", "")
        text = re.sub(prefixes, "\\1<prd>", text)
        text = re.sub(websites, "<prd>\\1", text)
        if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
        text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
        text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
        text = re.sub(mathdot,'\_',text)
        if "”" in text: text = text.replace(".”", "”.")
        if "\"" in text: text = text.replace(".\"", "\".")
        if "!" in text: text = text.replace("!\"", "\"!")
        if "?" in text: text = text.replace("?\"", "\"?")
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<prd>", ".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        return sentences

    @staticmethod
    def scan_cit(text):
        all_match = re.findall(r'cite{(.*?)}|citeA{(.*?)}|citep{(.*?)}|citet{(.*?)}', text)
        output = []
        for item in all_match:
            for sub_item in item:
                if sub_item != '':
                    output.extend([w.replace(' ', '') for w in sub_item.split(',')])
        return set(output)

    @property
    def logic_control(self):
        ref = self.get_ref()
        splitted_text = self.split_to_sentence(self.whole_text)
        text_length = len(splitted_text)
        for i in range(text_length):
            current_sentence_cit = self.scan_cit(splitted_text[i])
            if current_sentence_cit != []:
                self.sentence_dict[i] = splitted_text[i]
                for item in current_sentence_cit:
                    if item in self.cit_dict.keys():
                        self.cit_dict[item].append(i)
                    else:
                        self.cit_dict[item] = [i]
        return text_length,self.cit_dict,self.sentence_dict,ref

