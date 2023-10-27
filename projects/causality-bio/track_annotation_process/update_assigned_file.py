import json
import os
from track import run_in_pipeline


# Define the path to the JSON file
json_file_path = '../annotation_output/task_assignment.json'

# Check if the JSON file exists
if os.path.exists(json_file_path):
    # Read the JSON file
    with open(json_file_path, 'r') as json_file:
        json_content = json.load(json_file)

        # Access the 'assigned' attribute within the JSON file
        unassigned_tasks = json_content['unassigned']

        # Iterate over the assigned tasks
        for task, count in unassigned_tasks.items():
            print(f"Task: {task}, Assignments needed: {count}")
else:
    print("JSON file does not exist.")

actually_annotated, productive_annotators = run_in_pipeline("../annotation_output/", "../data/pilot/medicine/score_[4, 5]_batch_3_fixed_context.tsv")

print("pause")

print(actually_annotated)

# check if the instances in unassigned_tasks.items() are actually annotated:
# if not we want to store them in a list:
label_needed = []
num_labels_needed =3

assigned_tasks = json_content['assigned']
# we go over each task in assigned_tasks and check if we have an actual annotation for it
ignore = ['Welcome.html', 'Task.html', 'ChangeTypes.html', 'Consent.html', 'Navigation.html', 'Experience.html', 'End.html']

assignments_to_be_removed = []
for task, users in assigned_tasks.items():
    if task not in ignore:
        if actually_annotated[task] != len(users):
            label_needed.append((task, num_labels_needed - actually_annotated[task]))
            # check who of users is not in productive_annotators:
            for user in users:
                if user not in productive_annotators:
                    # we remove them later
                    assignments_to_be_removed.append((task, user))


print(label_needed)

# update up the json file:
for item in assignments_to_be_removed:
    assigned_tasks[item[0]].remove(item[1])

for label in label_needed:
    unassigned_tasks[label[0]] = label[1]


json_content['assigned'] = assigned_tasks
json_content['unassigned'] = unassigned_tasks

# save json_content to json_file_path
file_path = "updated_task_assignment.json"
with open(file_path, 'w') as json_file:
    json.dump(json_content, json_file)