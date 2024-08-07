# Description:
# extract a small LOTUS dataset to sample N lines from M members of taxa level T.

import polars as pl  # for data manipulation
import numpy as np  # specialy for NaN
import sys  # for command line arguments
import getopt  # for checking command line arguments
import datetime  # for naming the output file
import logging


# for interactive mode
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from pathlib import Path

import zenodo_downloader as zd
from InquirerPy.validator import PathValidator

def read_LOTUS_dataset(file_to_sample):
    df = pl.read_csv(
        file_to_sample,
        dtypes={
            "structure_xlogp": pl.Float32,
            "structure_cid": pl.UInt32,
            "organism_taxonomy_ncbiid": pl.UInt32,
            "organism_taxonomy_ottid": pl.UInt32,
            "structure_stereocenters_total": pl.UInt32,
            "structure_stereocenters_unspecified": pl.UInt32,
        },
        separator=",",
        infer_schema_length=50000,
        null_values=["", "NA"],
    )

    # print("Before type: ", df["organism_taxonomy_gbifid"].dtype)

    if not df["organism_taxonomy_gbifid"].dtype.is_numeric():
        df = df.with_columns(
            pl.col("organism_taxonomy_gbifid")
            .map_elements(lambda x: np.nan if x.startswith("c(") else x, return_dtype=pl.Float64)
            .cast(pl.Int32, strict=False)  # Cast with strict=False to allow NaN to be retained
            .alias("organism_taxonomy_gbifid")
        )
    else:
        df = df.with_columns(
            pl.col("organism_taxonomy_gbifid")
            .cast(pl.Int32, strict=False)  # Cast with strict=False to allow NaN to be retained
            .alias("organism_taxonomy_gbifid")
        )

    # print("After type: ", df["organism_taxonomy_gbifid"].dtype)
    return df

def read_arg(argv):

    arg_help = f'''
    Please give the arguments as following:
        {argv[0]} -i <input_path_file> -o <output_path_file> -t <taxalevel> -s <samplesize_per_member>
    
    Or don't give any arguments, so the script will start in interactive mode.
    '''

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
            "h:i:o:t:m:s:", 
            [
                "help",
                "input_path_file=",
                "output_path_file=",
                "taxalevel=",
                "taxalevel_membername="
                "samplesize_per_member=",
            ],
        )
    except getopt.GetoptError as err:
        # print help information and exit:
        print(arg_help)  
        sys.exit(2)

    input_path_file = str()
    output_path_file = str()
    taxalevel = str()
    taxalevel_membername = str()
    samplesize_per_member = int()

    # If argument values given, overwrite the default values
    for o, a in opts:
        if o in ("-h", "--help"):
            print(arg_help)
            sys.exit()
        elif o in ("-i", "--input_path_file"):
            input_path_file = a
        elif o in ("-o", "--output_path_file"):
            output_path_file = a
        elif o in ("-t", "--taxalevel"):
            taxalevel = a
        elif o in ("-m", "--taxalevel_membername"):
            taxalevel_membername = a
        elif o in ("-s", "--samplesize_per_member"):
            samplesize_per_member = a
        else:
            assert False, "unhandled option"
        
    return {
            "input_path_file" : input_path_file, 
            "output_path_file" : output_path_file, 
            "taxalevel" : taxalevel, 
            "taxalevel_membername" : taxalevel_membername,
            "samplesize_per_member" : samplesize_per_member,
            }



if __name__ == "__main__":

    url_all_doi = "https://zenodo.org/search?q=parent.id%3A5794106&f=allversions%3Atrue&l=list&p=1&s=20&sort=version"
    filenames_list = list()

    # Read arguments after the scriptname
    if sys.argv[1:]:
        file_info = read_arg(sys.argv)

        # load the dataset (can load *.csv, *.csv.gz...)
        df = read_LOTUS_dataset(file_info["input_path_file"])
        
        # select all the possible samples
        df_filtered_taxonomy = df.filter(pl.col(file_info["taxalevel"]) == file_info["taxalevel_membername"])
        df_filtered_taxonomy_size = len(df_filtered_taxonomy)

        # check the samplesize and if it's bigger, just take max
        if int(file_info["samplesize_per_member"]) > df_filtered_taxonomy_size:
            file_info["samplesize_per_member"] = df_filtered_taxonomy_size
        
        print(f'We can sample {file_info["samplesize_per_member"]} (Max. possible: {df_filtered_taxonomy_size}).')

        # sample from the data
        df_sampled = df_filtered_taxonomy.sample(n=file_info["samplesize_per_member"])

        try:
            # if the file exists, read it and append the data
            df_exist = read_LOTUS_dataset(file_info["output_path_file"])
            print(f'File {file_info["output_path_file"]} exists. Appending to file.') 
            df_sampled.extend(df_exist)       
        except:
            # if the file does not exist, create a new dataframe (df_exist)
            print(f'File {file_info["output_path_file"]} does not exist. Creating new file.')

        # drop all the duplicates and save it
        df_sampled = df_sampled.unique()
        df_sampled.write_csv(file_info["output_path_file"])
        
    else:   
        print("Start interactive mode.")
    
        user_option = inquirer.select(
            message=
            '''Welcome to the "toydataset extractor" for the LOTUS datasets. 
            Chose your action:''',
            choices=[
                "sampling", 
                "download", 
                "LOTUS to MINEs (save LOTUS file as a MINEs)",
                "exit (Ctrl+C)",
            ],
            multiselect=False,
        ).execute()
        
        ##################
        # OPTION: cancel #
        ################## 
        if user_option == "exit (Ctrl+C)":
            sys.exit(2)

        ####################
        # OPTION: download #
        #################### 
        elif user_option == "download":
            print("The datasets will be searched from the internet. One moment please...")
            all_doi_list = zd.get_all_records(url=url_all_doi)
            filenames_records, filenames, download_urls = zd.get_filenames(all_doi_list)

            # make the options for downloading and sort them
            options = filenames_records.copy()
            options.sort(reverse=True)
            
            # Add for the option for exit
            options.append(Separator())
            options.append("exit (Ctrl+C)")

            download_option = inquirer.select(
                message=
                '''Please choose your dataset to download (sorted from newest to oldest):''',
                choices=options,
                ).execute()

            if download_option == "exit (Ctrl+C)":
                sys.exit(2)

            dest_path = inquirer.filepath(
                message="Enter path to download:",
                validate=PathValidator(is_dir=True, message="Input is not a directory"),
                only_directories=True,
                ).execute()

            print(f'The dataset will be downloaded to {dest_path}/{download_option}.')
            for filename, filenames_record, download_url in zip(filenames, filenames_records, download_urls):
                if download_option == filenames_record:
                    zd.download_file(download_url=download_url, filename=dest_path + '/' + filename)
                    print("Download complete:", filename)


        ####################
        # OPTION: sampling #
        ####################            
        elif user_option == "sampling":
            
            # get the filepath for sampling (theoreticaly we can sample from diffrent sources for one toydataset)
            file_to_sample = inquirer.filepath(
                message="Enter the filepath to sample from:",
                validate=PathValidator(is_file=True, message="Input is not a file"),
                # only_directories=True,
                ).execute()

            # load the dataset (can load *.csv, *.csv.gz...)
            df = read_LOTUS_dataset(file_to_sample)

            
            # get all columns with "taxonomy" inside
            taxonomy = list()
            for col_name in df.columns:
                if "taxonomy" in col_name:
                    taxonomy.append(col_name)

            # choose the taxonomy level
            taxalevel = inquirer.select(
                message=
                '''Please choose the taxonomy level to sample from:''',
                choices=taxonomy,
                ).execute()
            
            # get all possible members in this taxalevel
            members_list = df[taxalevel].unique().drop_nulls()

            members_dict = dict()
            for member in members_list:
                members_dict[member] = None

            # choose from which members to sample / check if it in member_list
            membername = inquirer.text(
                message=f"Choose from which member to sample ({len(members_list)} options):",
                completer=members_dict,
                ).execute()


            # select all the possible samples
            df_filtered_taxonomy = df.filter(pl.col(taxalevel) == membername)
            df_filtered_taxonomy_size = len(df_filtered_taxonomy)

            # choose how many to sample
            samplesize_per_member = inquirer.text(
                message=f"Please enter the amount of members to sample (max. {df_filtered_taxonomy_size}):",
                validate=lambda result: isinstance(int(result), int) and 0 < int(result) <= df_filtered_taxonomy_size,
                ).execute()

            # choose the format of output among full or "for MINES" (this will just return the structure_wikidata and structure_smiles)
            possible_output_format = ["full", "MINES"]

            output_format = inquirer.select(
                message=
                '''Please choose the output format:''',
                choices=possible_output_format,
                ).execute()


            # give a existing file name to append it or give a new name to create a new file
            output_path_file = inquirer.filepath(
                message="Enter the output file name or existing filename to append:",
                # validate=PathValidator(is_file=False, message="Input is not a file"),
                ).execute()


            # sample from the data
            data_sampled = df_filtered_taxonomy.sample(n=samplesize_per_member)

            # depending on the output format, drop the columns. And rename the columns
            # structure_wikidata to id, structure_smiles to smiles

            if output_format == "MINES":
                data_sampled = data_sampled.select([
                    "structure_wikidata",
                    "structure_smiles",
                ])
                data_sampled = data_sampled.rename({
                    "structure_wikidata": "id",
                    "structure_smiles": "smiles"
                })
            else:
                data_sampled = data_sampled

            try:
                # if the file exists, read it and append the data
                df_exist = read_LOTUS_dataset(output_path_file)
                print(f'File {output_path_file} exists. Appending to file.') 
                data_sampled.extend(df_exist)  
                data_sampled = data_sampled.unique()
            except:
                # if the file does not exist, create a new dataframe (df_exist)
                print(f'File {output_path_file} does not exist. Creating new file.')

            # drop all the duplicates and save it
            data_sampled.write_csv(output_path_file)


        ##########################
        # OPTION: LOTUS to MINEs #
        ##########################            
          
        elif user_option == "LOTUS to MINEs (save LOTUS file as a MINEs)":

            # Get the filepath for sampling (theoretically we can sample from different sources for one toydataset)
            file_to_sample = inquirer.filepath(
                message="Enter the filepath to sample from:",
                validate=lambda path: Path(path).is_file(),
            ).execute()

            # Load the dataset using the existing read_LOTUS_dataset function
            df = read_LOTUS_dataset(file_to_sample)

            # Get the list of columns from the DataFrame
            columns = df.columns

            # Choose the column names for ID and SMILES interactively
            id_column = inquirer.select(
                message="Select the column name for the ID:",
                choices=columns,
                default="structure_inchikey",
            ).execute()

            smiles_column = inquirer.select(
                message="Select the column name for the SMILES:",
                choices=columns,
                default="structure_smiles",
            ).execute()

            # Give an existing file name to append it or give a new name to create a new file
            output_path_file = inquirer.filepath(
                message="Enter the output file name or existing filename to append:",
            ).execute()

            df = df.select(
                [
                    id_column,
                    smiles_column,
                ]
            ).rename(
                {
                    id_column: "id",
                    smiles_column: "smiles"
                }
            ).unique()
            #).unique(subset=["smiles"])

            # Find duplicates in the columns
            duplicates_id = df.group_by("id").count().filter(pl.col("count") > 1)
            duplicates_smiles = df.group_by("smiles").count().filter(pl.col("count") > 1)

            # info about dataframe
            print(f"""--- Uniqueness of dataframe ---\nall columns: {df.unique().shape[1]}\nid: {df.unique(subset="id").shape[0]}\nsmiles: {df.unique(subset="smiles").shape[0]}""")

            # Print the duplicate IDs
            if not duplicates_id.is_empty():
                print(f'Duplicate IDs found:\n{duplicates_id}')

            # Print the duplicate SMILES
            if not duplicates_smiles.is_empty():
                print(f'Duplicate SMILES found:\n{duplicates_smiles}')

            # Write the transformed DataFrame to a new CSV file
            df.write_csv(output_path_file)

