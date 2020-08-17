#!/bin/bash

# check if there is result folder
if [ ! -d "$./result" ];
	then mkdir result
fi

# get tar file name
for f in Arxiv_data/*.tar;
do 
	mkdir new;
	tar -C ./new -xf $f;
	echo "starting parsing file in file $f";
	python process.py --read_folder new/ --write_folder ./result/ --file_name $f
	rm -rf $f;
	rm -rf ./new;
done
