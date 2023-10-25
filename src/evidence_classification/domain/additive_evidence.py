ACRONYM = "AEC"


def additive_evidence(**identifier_properties):
    unique_data_string = [
        #identifier_properties.get("evidenceIds", "NoEvidenceIds"),
        identifier_properties.get("code", "NoCode")
    ]

    return unique_data_string


if __name__ == '__main__':
    identifier_properties = {
        "entity_data": {
            # "evidenceIds": "evidenceIds",
            "code": "code"
        }
    }
    print(additive_evidence(**identifier_properties))
