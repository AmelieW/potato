from utils.utils import Annotator, LabeledInstance, instance_stats, group_instances_wrt_id
import pandas as pd
import os
import argparse

#L = ['5caad602a15c9800161ad6d3', '61671c6dc5d5587bdaf08989', '6303814dfe5bbd0b827d10b4', '5e8783b0fde5153fbd9dca43', '5f0448506587140241493cbe', '60dc54db60a4dca481ba3608', '61001309835f7fddeb965ea9', '60cf529b26650af60dbc0440', '60ccbcfaa216558af6d8bf0e', '60a2d1593f270f92fa69305d']
#P= "/Users/amelie/Documents/1_Uni/Promotion/admin/research-stay/information-changes/data/anno-environment/potato/projects/info_changes/pilot/batch-1_annotation_output/"
#5e820a415b6ebc01e6cd81a8/annotated_instances.jsonl"

P= "/Users/amelie/Documents/1_Uni/Promotion/admin/research-stay/information-changes/data/anno-environment/potato/projects/info_changes/pilot/batch-2_annotation_output/"
L = ['5ce33217f1117f0017c80de1', '60d3867b6e7529fc77032b54', '6168926c2ebd65e2f7eee82c', '5c1bb460a05a64000125c522', '5c131126d6d169000148414a', '60e2ebb6ad1d5ee0e515a7c5', '614dd12e1864621b9d8436ac', '5f96b94504b0720009b4a1ed', '6072e4e6236de7ca7d4bf06e', '61747e90d6980cdffa3de99d', '5fdf4ff8b112b67125e0b2b1', '61572a3b2955ccd1969daecd', '5d6d15ce424136001af41fbc']
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
        file = f"{P}{prolific_id}/annotated_instances.jsonl"

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
    for g in instance_groups:
        print(g)



if __name__ == "__main__":
    # parse arguments from the commandline with argparse
    args = parse_args()
    run(args)