"""
Pure Display Layout
"""


def generate_pure_display_layout(annotation_scheme):

    schematic = f"{annotation_scheme['description']} {'<br>'.join(annotation_scheme['labels'])}"
    schematic = f'<span style="font-size:15pt;">{schematic}</span>'

    schematic_old = "<Strong>%s</Strong> %s" % (
        annotation_scheme["description"],
        "<br>".join(annotation_scheme["labels"]),
    )
    #assert schematic == schematic_old
    return schematic, None
