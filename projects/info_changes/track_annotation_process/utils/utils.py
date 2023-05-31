

class Annotator:
    def __init__(self, anno_id):
        self.id = anno_id
        self.instances = []

    def add_new_instance(self, labeled_instance):
        self.instances.append(labeled_instance)


class LabeledInstance:
    def __init__(self, instance_id):
        self.id = instance_id

    def __str__(self):
        return f"id: {self.id}\n" \
               f"instance text: {self.instance_text}\n" \
               f"labels: {self.labels}\n" \
               f"spans: {self.spans}\n" \
               f"meta_data: {self.meta_data}"

    def parse_annotations(self, label_anno, span_anno):
        """takes in the label_annotations and span_annoations that we get from potato and extract it into attributes"""
        # {'changes-key-entity': {'no': '2'}, 'Level-of-generality': {'no': '2'}, 'how-certain-is-the-reported-finding': {'Somewhat certain': '4'}, 'how-certain-is-the-paper-finding': {'Certain': '5'}, 'reporting-is-sensational': {'Neutral': '1'}, 'paper-is-sensational': {'Neutral': '1'}, 'how-causal-is-the-reporting': {'Correlation': '2'}, 'how-causal-is-the-paper-finding': {'Correlation': '2'}}
        labels = []
        spans = []

        for item in label_anno.items():
            label_name = item[0]
            for key in item[1].keys():
                label_value_name = key
                label_value_numeric = item[1][key]
            labels.append((label_name, label_value_name, label_value_numeric))
        if span_anno:
            same_label_and_span = None
            # check if there are multiple labels for the same span
            if len(span_anno) != len(list(set(s["span"] for s in span_anno))):
                print("pause")
                # find the duplicate span: create an ordered dict with the span as key and the number of occurences as value
                from collections import OrderedDict
                span_dict = OrderedDict()
                for s in span_anno:
                    span_dict[s["span"]] = span_dict.get(s["span"], 0) + 1
                # find the span that occurs more than once
                duplicate_spans = []
                for k, v in span_dict.items():
                    if v > 1:
                        duplicate_span = k
                        duplicate_spans.append(duplicate_span)
                    else:
                        continue
                for d in duplicate_spans:
                    # check if the span is annotated with the same label:
                    labels_for_span = [item for item in span_anno if item["span"] == d]
                    # check if the there are duplicates in the labels_for_span:
                    if len(labels_for_span)>len(list(set([l["annotation"] for l in labels_for_span]))):
                        same_label_and_span = (True, labels_for_span)
                    else:
                        same_label_and_span = None

            if same_label_and_span is not None:  # if there are any spans which have the same span and label, we want to be careful when searching for them in the string
                problematic_labels = [l['annotation'] for l in same_label_and_span[1]]
            else:
                problematic_labels = []
            for span in span_anno:
                span_name = span["annotation"]
                span_string = span["span"]
                span_string = self.remove_html_tags(span_string)  # removing any rouge html tags
                span_onset = None
                if span_name in problematic_labels:
                    # check if this is the first mention of this span:
                    label_names = [s[0] for s in spans]
                    strings = [s[2] for s in spans]
                    clean_string = self.remove_html_tags(span['span'])
                    if clean_string not in strings:
                        if span_name not in label_names:
                            pass
                    else:
                        span_onset = self.handle_problematic_labels(span_name, span, span_anno, spans)
                if span_onset is None:
                    span_onset = self.find_span_onset(span_string) # find the onset of the span in the instance text
                span_start_end = (span_onset, span_onset+len(span_string))
                spans.append((span_name, span_start_end, span_string))


        return labels, spans

    def add_labeled_instance(self, annotator_id, instance_text, label_annotations, span_annotations, meta_data):
        self.annotator_id = annotator_id
        self.instance_text = instance_text
        self.meta_data = meta_data
        labels, spans = self.parse_annotations(label_annotations,span_annotations)
        self.labels = labels
        self.spans = spans

    def find_span_onset(self, span_string):

        span_onset = self.instance_text.find(span_string)
        if span_onset == -1: # find returns -1 if the string is not found
            span_string = span_string.replace('&nbsp;', '')
            span_onset = self.instance_text.find(span_string)
        return span_onset

    def handle_problematic_labels(self, span_name, span, span_anno, spans):
        # if this is the second or third .. mention of this particular label and span, we search in the remainder of the instance text
        # get the offset of the previous mention of this label and span
        previous_mention = [s for s in spans if s[2] == self.remove_html_tags(span['span']) and s[2] == self.remove_html_tags(span['span'])]
        # search for the span string, but only after the off set of the previous mention
        span_onset = self.instance_text.find(span['span'], previous_mention[0][1][1])

        return span_onset

    def remove_html_tags(self, span_string):

        # something goes wrong with the on and offsets, so we map the string back to the original text and get the offsets this way
        # check if the annotated span contains an html span container:
        # using regex to find the span container
        container = "<span class=[^>]*>"
        #if container in span_string, replace it with an empty string
        import re
        if re.search(container, span_string):
            span_string = re.sub(container, "", span_string)

        return span_string


def instance_stats(list_of_annotators):
    i = {}

    for annot in list_of_annotators:
        for inst in annot.instances:
            if inst.id not in i.keys():
                i[inst.id] = 1
            else:
                i[inst.id] += 1
    """print(i)
    print([id for id in i.keys()])
    print(len([id for id in i.keys()]))"""

def group_instances_wrt_id(list_of_annotators):
    grouped = {}

    for annot in list_of_annotators:
        for inst in annot.instances:
            if inst.id not in grouped.keys():
                grouped[inst.id] = []

            grouped[inst.id].append(inst)

    return grouped

