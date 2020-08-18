# All-In-One citation extraction module

## Data Description
* Arxiv_data - data folder
* parser.py - parsing module includes decompressing ,scanning file folder, reading file with encoding detection, extracting reference.
* process.py - logic control applying multiprocessing module and generating result from the result of running parser.
* run.sh - bash script run through all compressed file from Arxiv database.

## Data
[Arxiv Database](https://arxiv.org) is an open-access repository of scientific papers([detail info](https://en.wikipedia.org/wiki/ArXiv)], this job's task is extracting citations from each paper, include the reference information as well as the sentence where the auther using the reference. This project is a pre-job of a future citation sentiment analysis task.

The Arxiv database I got was pre-downloaded in google bucket, which was formated in multiple compressed files(Each compressed file represents a single year or part of a year due to the records. For an example, Jan 1990 might just recorded few publications, therefore there is just one .tar file for that month but for the Jan 2018, there are bunch of records, then there might apper few files record in order 1801.0001 to 1801.000x, the total size of these files are more than 100 TB.) Here in the Arxiv_data folder, I uploaded two example file which is the first two parts recorded in Oct 2007. Insided each file, each publication is also a compressed file(since most of them are in Latex format, might contain some images or bib item).

## Project Logic
__process.py__ is the main logic control I am using here,i contains all the logic level instructor. After decompressed the first level compressed file, there might appear two types of files, .first is a .gz file which is a compressed Latex folder or a single .tex file, another one is a PDF file. For the pdf file here, I will record them as "ERROR FILE" in the log, and other groups with well-tested pdf parser will figure these out later. For these .gz file, by using Python tarfile API, if the .gz file just contain a single .tex file, it will return error, so here I used the subprocess API which can call bash script directly in Python to decompress these error file. After finished the first level, I got a bunch of folders which contain the publications in Latex format or single Latex file, then the main processer will call the __parser.py__ to parse all the items, no matter it is a folder or a .tex file. In order to boost the speed, I applied multiprocesser here so the computing machine will process all the items together. After I got the result, they will be recorded in JSON files, each first level .tar file will now becomes one JSON file which recorded successfully parsed publicitaion and an error file recording failures which might because of pdf format or decoding issue.

__parser.py__ is the module I use to parse either the Latex folder or single .tex file. It will automatically detict the format of the input file, at the meantime, if the input file is a Latex folder, it will check if there is .bib file inside which representing the reference part. Also, lots of publications were not written in English, so the ecoding is also a big problem, here I used the chardet API to detecting the encoding and open the file with correct encoding. Also, sometimes in some Latex folders, there are multiple .tex file, as a discussion with my superviser, we decided to only read the largest .tex file. Then the script will parse the read file and with the list of output:
* text length: num of sentences without reference of the publication
* citation dictionary: __key__ is unique cited papers(some paper appear multiple times in a publication), __value__ is a list of positions where the author using the reference.
* sentence dictionary: __key__ is position number: the related sentence. 
* extracted reference
## Usage
Simply type `bash run.sh` in terminal.

