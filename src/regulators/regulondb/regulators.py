import os

import pythoncyc

from utils import constants as EC
from utils import utils


class Regulator(object):
    pt_conn = pythoncyc.select_organism(EC.ORGANISM)

    def __init__(self, **kwargs):
        # Obj properties
        self.regulator_obj = kwargs.get('regulator_obj', None)
        self.regulator_cyc_id = kwargs.get('regulator_cyc_id', None)

        # Dict properties
        self.regulator_id = kwargs.get("regulator_id", None)
        self.abbreviated_name = kwargs.get("abbreviated_name", None)
        self.name = kwargs.get("name", None)
        self.citations = kwargs.get("citations", None)
        self.confidence_level = kwargs.get("confidence_level", None)
        self.external_cross_references = kwargs.get(
            "external_cross_references", None)
        self.regulator_type = kwargs.get("regulator_type", None)
        self.synonyms = kwargs.get("synonyms", None)
        self.regulator_class = kwargs.get("regulator_class", None)

    # Properties

    @property
    def regulator_id(self):
        return self._regulator_id

    @regulator_id.setter
    def regulator_id(self, regulator_id=None):
        if regulator_id is None:
            self._regulator_id = self.regulator_obj.id
        else:
            self._regulator_id = regulator_id

    @property
    def abbreviated_name(self):
        return self._abbreviated_name

    @abbreviated_name.setter
    def abbreviated_name(self, abbreviated_name=None):
        if abbreviated_name is None:
            try:
                self._abbreviated_name = self.regulator_obj.abbreviated_name
            except AttributeError:
                self._abbreviated_name = None
        else:
            self._abbreviated_name = abbreviated_name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name=None):
        if name is None:
            self._name = self.regulator_obj.name
        else:
            self._name = name

    @property
    def citations(self):
        return self._citations

    @citations.setter
    def citations(self, citations=None):
        if citations is None:
            mg_citations = self.regulator_obj.citations
            citations = []
            for citation in mg_citations:
                citation_dict = {
                    'evidences_id': citation.evidences_id,
                    'publications_id': citation.publications_id,
                }
                citation_dict = utils.get_only_properties_with_values(
                    citation_dict)
                citations.append(citation_dict)
            self._citations = citations
        else:
            self._citations = citations

    @property
    def confidence_level(self):
        return self._confidence_level

    @confidence_level.setter
    def confidence_level(self, confidence_level=None):
        if confidence_level is None:
            try:
                self._confidence_level = self.regulator_object.confidence_level
            except AttributeError:
                self._confidence_level = None
        else:
            self._confidence_level = confidence_level

    @property
    def external_cross_references(self):
        return self._external_cross_references

    @external_cross_references.setter
    def external_cross_references(self, external_cross_references=None):
        if external_cross_references is None:
            external_cross_references = self.regulator_obj.external_cross_references
            references_list = []
            for reference in external_cross_references:
                cross_reference = {
                    'externalCrossReferences_id': reference.external_cross_references_id,
                    'objectId': reference.object_id,
                }
                cross_reference = utils.get_only_properties_with_values(
                    cross_reference)
                references_list.append(cross_reference)
            self._external_cross_references = references_list
        else:
            self._external_cross_references = external_cross_references

    @property
    def regulator_type(self):
        return self._regulator_type

    @regulator_type.setter
    def regulator_type(self, regulator_type=None):
        if regulator_type is None:
            self._regulator_type = self.regulator_obj.regulator_type
        else:
            self._regulator_type = regulator_type

    @property
    def synonyms(self):
        return self._synonyms

    @synonyms.setter
    def synonyms(self, synonyms=None):
        if synonyms is None:
            self._synonyms = self.regulator_obj.synonyms
        else:
            self._synonyms = synonyms

    @property
    def regulator_class(self):
        return self._regulator_class

    @regulator_class.setter
    def regulator_class(self, regulator_class=None):
        if regulator_class is None:
            print(self.regulator_cyc_id)
            self._regulator_class = Regulator.pt_conn.get_frame_direct_parents(
                self.regulator_cyc_id)
        else:
            self._regulator_class = regulator_class
