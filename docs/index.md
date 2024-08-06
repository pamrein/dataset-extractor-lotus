# Dataset Extractor for LOTUS

[LOTUS](https://lotus.naturalproducts.net/) is a database with over 700'000 natural products (NPs).  

For developing reasons it can be better to work with smaller datasets. 
This script can help to extract randomly or specifically a subset of this data.

The script allows you to choose from a taxonomy specific member a samplesize.
You have to give your data to sample from and the location to save it. 
If the location to save it is the same as an existing, it will append it (and remove the duplicates).
If the given samplesize is to big, it will choose the max.
In the end, the duplicates will be removed.


## Information
Poetry was used as an environment control.
It is highly recommended to use the *.lock file for set up the same environment.

```bash
# Install pipx and poetry
pip install pipx
pipx install poetry

# Install from the poetry.lock file (command should be run in the same folder as the poetry.lock file)
poetry install
```

## Running the script
The script `main.py` can be run from the terminal.  

To run the script it is recommended to use it with the poetry command. 
```bash
# run the script in poetry and get the help page 
poetry run python dataset_extractor_lotus/main.py -h
```

Or a poetry shell can be used.
```bash
# run the script in poetry and get the help page 
poetry shell
python dataset_extractor_lotus/main.py -h
```


## Examples

One line command
```bash
poetry shell
python dataset_extractor_lotus/main.py -i data/test.csv -o test.csv -t organism_taxonomy_10varietas -m 'Abies sachalinensis var. gracilis' -s 100
```

interactive mode
```bash
poetry shell
python dataset_extractor_lotus/main.py
```


## to be improved
&#9744; In the moment, the samplespace will be sampled and then added to the existing dataframe. After this step the duplications will be removed.  
It would be better, if the samplespace would be first filtered out for the existing samples and then sampled.   
&#9744; Add some default parameters for a faster toysample experience.  
&#9744; possibility to add a seed, so the sampling step can be repeated.
&#9744; add parametermode for downloading  
&#9744; check again, if the appending mode works well. 