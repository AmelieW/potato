import json
import os
from track import run_in_pipeline
import pandas as pd


TO_ANNOTATE = "../data/pilot/medicine/score_[4, 5]_batch_3_fixed_context.tsv"
ANNO_OUTPUT_DIR = "../pilot/batch-3_annotation_output/"

IGNORE = ['Welcome.html', 'Task.html', 'ChangeTypes.html', 'Consent.html', 'Navigation.html', 'Experience.html',
              'End.html']




def save_json(json_content):
    # save json_content to json_file_path
    file_path = "combined_task_assignment.json"
    with open(file_path, 'w') as json_file:
        json.dump(json_content, json_file)

def find_unassigned(to_be_annoated, assigned_ids):
    # read in to_be_annoated as a dataframe
    df = pd.read_csv(to_be_annoated, sep="\t")
    # get a list of the id column
    ids = df['id'].tolist()
    # check which ids are not in assigned_ids
    unassigned = []
    for id in ids:
        if id not in assigned_ids:
            unassigned.append(id)
    return unassigned

def correct_json(json_task_assignment, num_of_annoations_needed=3):
    actually_annotated, productive_annotators = run_in_pipeline(ANNO_OUTPUT_DIR,
                                                                TO_ANNOTATE)


    print(actually_annotated)

    # check if the instances in unassigned_tasks.items() are actually annotated:
    # if not we want to store them in a list:
    label_needed = []

    assigned_tasks = json_task_assignment['assigned']
    unassigned_tasks = json_task_assignment['unassigned']
    # we go over each task in assigned_tasks and check if we have an actual annotation for it


    assignments_to_be_removed = []
    for task, users in assigned_tasks.items():
        if task not in IGNORE:
            if actually_annotated[task] != len(users):
                label_needed.append((task, num_of_annoations_needed - actually_annotated[task]))
                # check who of users is not in productive_annotators:
                for user in users:
                    if user not in productive_annotators:
                        # we remove them later
                        assignments_to_be_removed.append((task, user))

    print(label_needed)

    # update up the json file:
    for item in assignments_to_be_removed:
        assigned_tasks[item[0]].remove(item[1])

    # check if there are any instances which haven't been assigned
    completely_unassigned = find_unassigned(TO_ANNOTATE, assigned_tasks.keys())

    if len(completely_unassigned) > 0:
        for id in completely_unassigned:
            label_needed.append((id,num_of_annoations_needed))

    for label in label_needed:
        if label[1] !=0:
            unassigned_tasks[label[0]] = label[1]

    json_task_assignment['assigned'] = assigned_tasks
    json_task_assignment['unassigned'] = unassigned_tasks

    return json_task_assignment

def combine_task_files(json_data):
    # combines the json files by adding the assigned tasks from both files
    # take the first json file as our base structure
    base_json = json_data['json_0']
    # go over the other json files and add the assigned tasks to the base_json
    for e, (k, val) in enumerate(json_data.items()):
        if e>0:
            assigned_tasks = val['assigned']
            for task, users in assigned_tasks.items():
                if task not in IGNORE:
                    if task in base_json['assigned']:
                        base_json['assigned'][task].extend(users)
                    else:
                        base_json['assigned'][task] = users

    return base_json


def run(list_of_json_file_paths):
    #read json files we want to combine
    json_data = {}
    for p, path in enumerate(list_of_json_file_paths):
        # Check if the JSON file exists
        if os.path.exists(path):
            # Read the JSON file
            with open(path, 'r') as json_file:
                json_content = json.load(json_file)
                json_data[f"json_{p}"] = json_content
        else:
            print("JSON file does not exist.")

    # combine the files
    combined = combine_task_files(json_data)

    # correct the json files
    correcetd_json_data = correct_json(combined, num_of_annoations_needed=3)

    print(correcetd_json_data)
    save_json(correcetd_json_data)


if __name__ == "__main__":
    paths = ['../pilot/batch-3_annotation_output/task_assignment_2.json', '../pilot/batch-3_annotation_output/task_assignment.json']
    run(paths)