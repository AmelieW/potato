from utils.utils import Annotator, LabeledInstance, instance_stats, group_instances_wrt_id
import pandas as pd
import os
import argparse


def parse_args():
    # use the argparse module to parse commandline arguments

    parser = argparse.ArgumentParser(description='Evaluate the annotation process')
    # add argument for the directory with the annotation output
    parser.add_argument('-d', '--directory', type=str, required=True,
                        help='the directory with the annotation output')

    return parser.parse_args()

def run(args):
    """starts the eval pipeline"""

    all_annotations = []

    print(f"Reading in data from {args.directory}")

    # create a list of all Prolific Ids in the directory:
    L = os.listdir(args.directory)
    # make sure the list only contains directories with prolific ids as names:
    L = [l for l in L if len(l) == 24]


    for prolific_id in L:
        file = f"{args.directory}{prolific_id}/annotated_instances.jsonl"

        print(f"Reading in data from {file}")

        # check if the annotator did anything (this removes people who returned from the study without doing anything)
        if not os.path.exists(file):
            print("File does not exist. Skipping.")
            continue

        #create Annotator obj.
        annotator = Annotator(prolific_id)
        print("Annotator created.")

        # read in their data:
        df = pd.read_json(file, lines=True)
        ignore = ["Consent.html", "Experience.html"]
        for d, id in enumerate(df["id"]):
            if id not in ignore:
                instance = LabeledInstance(id)
                instance.add_labeled_instance(prolific_id,
                                              df.at[d, "displayed_text"],
                                              df.at[d, "label_annotations"],
                                              df.at[d, "span_annotations"],
                                              df.at[d, "behavioral_data"])
                annotator.add_new_instance(instance)

        all_annotations.append(annotator)

    instance_stats(all_annotations)

    # for each instance id, get the annotations for this instacne grouped
    instance_groups = group_instances_wrt_id(all_annotations)
    



if __name__ == "__main__":
    # parse arguments from the commandline with argparse
    args = parse_args()
    run(args)