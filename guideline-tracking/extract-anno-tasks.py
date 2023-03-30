"""We want to keep an up to date document that documents all the tasks, labels and tooltips that annotators see during their work;
* this gets all information from the yaml file
* saves it to a markdown file
"""


YAML = "../projects/info_changes/config/info-change.yaml"
OUTPUT_DOC = "tasks.md"

import yaml

def read_yaml(yaml_file):
    """reads all the contents from the yaml file into a dictionary"""
    yaml_content = {}
    with open(yaml_file, "r") as file_p:
        yaml_content.update(yaml.safe_load(file_p))

        return yaml_content

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def format_task_in_md(extracted_tasks):

    md_string = ""
    for task in extracted_tasks:
        # task = (description, [(label, tooltip),..])
        labels_tooltips_listed = ""
        for l in task[1]:
            name = l[0]
            labels_tooltips_listed = f"{labels_tooltips_listed}\n" \
                                     f"* **{name}**"
            if len(l[1])!=0:
                labels_tooltips_listed = f"{labels_tooltips_listed}, *tooltip*: {l[1]}"

        task_html_free = remove_html_tags(task[0])

        task_string = f"{task_html_free}\n{labels_tooltips_listed.strip()}\n"
        if len(md_string) == 0: #the first append
            md_string=f"{md_string}### Example Instance\n" \
                      f"{task_string}\n"
        else:
            md_string = f"{md_string}{task_string}\n"

    return md_string


def extract_tasks(task_content, markdown = False):
    """takes a list of annotation schemes from the yaml file,
    for each task, extracts the description along with all labels and their tooltips;
    if markdown = True: returns string formatted with MD, else, returns list of (description, [(label, tooltip), ..])"""

    extracted_tasks = []
    for task in task_content:
        labels_tooltips = []
        for l in task["labels"]:
            try:
                labels_tooltips.append((l["name"], l["tooltip"]))
            except TypeError: # if there's only one label that does not have a tooltip
                labels_tooltips.append((l, "")) # append an empty tooltip to keep the structure intact

        t = (task["description"], labels_tooltips)
        extracted_tasks.append(t)

    if markdown:
        tasks_in_md = format_task_in_md(extracted_tasks)
        return tasks_in_md
    else:
        return extracted_tasks

def extract(yaml_file, annotation_tasks = False, survey_flow = False):

    # read content from yaml:
    yaml_content = read_yaml(yaml_file)

    if annotation_tasks:
        # extract the tasks
        tasks = extract_tasks(yaml_content["annotation_schemes"], markdown = True)

    # write to file
    with open(OUTPUT_DOC, "a+") as o:
        o.write(tasks)










if __name__ == "__main__":
    extract(YAML, annotation_tasks=True)