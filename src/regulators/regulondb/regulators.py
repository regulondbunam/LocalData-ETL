# import os

import pythoncyc
import pymongo

from utils import constants as EC
from utils import utils


class Regulator(object):
    pt_conn = pythoncyc.select_organism(EC.ORGANISM)
    ri_collection_name = 'regulatoryInteractions'

    def __init__(self, **kwargs):
        # Obj properties
        self.regulator_obj = kwargs.get('regulator_obj', None)
        self.regulator_cyc_id = kwargs.get('regulator_cyc_id', None)
        self.database = kwargs.get('database', None)
        self.url = kwargs.get('url', None)
        self.organism = kwargs.get('organism', None)
        self.ris_cyc_ids = kwargs.get('ris_cyc_ids', None)

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
        self.regulation_type = kwargs.get("regulation_type", None)
        self.conformations = kwargs.get("conformations", None)
        self.note = kwargs.get("note", None)

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
    def citations(self, citations=None):  # TODO: solo las citations de las conformaciones.
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
                self._confidence_level = self.regulator_obj.confidence_level
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
            self._regulator_class = Regulator.pt_conn.get_frame_direct_parents(
                self.regulator_cyc_id)
        else:
            self._regulator_class = regulator_class

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, note=None):
        if note is None:
            self._note = self.regulator_obj.note
        else:
            self._note = note

    @property
    def conformations(self):
        return self._conformations

    @conformations.setter
    def conformations(self, conformations=None):
        self._conformations = conformations
        if conformations is None:
            conformations = []
            mongo_client = pymongo.MongoClient(self.url)
            db = mongo_client[self.database]
            collection = db[Regulator.ri_collection_name]

            if self.regulator_type == 'transcriptionFactor':
                active_conformations = self.regulator_obj.active_conformations
                inactive_conformations = self.regulator_obj.inactive_conformations
                for conf in active_conformations:
                    conf_dict = {
                        "_id": conf.id,
                        "type": conf.type,
                        "class": "active"
                    }
                    conformations.append(conf_dict)
                for conf in inactive_conformations:
                    conf_dict = {
                        "_id": conf.id,
                        "type": conf.type,
                        "class": "inactive"
                    }
                    conformations.append(conf_dict)
            ris = collection.find({
                "regulator.name": self.name
            })

            for ri_obj in ris:
                conf_dict = {
                    "_id": ri_obj.get('regulator').get('_id'),
                    "type": ri_obj.get('regulator').get('type'),
                    "class": "active"
                }
                if conf_dict not in conformations:
                    conformations.append(conf_dict)
                    continue
            self._conformations = conformations
        else:
            self._conformations = conformations

    @property
    def regulation_type(self):
        return self._regulation_type

    @regulation_type.setter
    def regulation_type(self, regulation_type=None):
        if regulation_type is None:
            mongo_client = pymongo.MongoClient(self.url)
            db = mongo_client[self.database]
            collection = db[Regulator.ri_collection_name]
            ris = collection.find({
                "regulator.name": self.name
            })
            self._regulation_type = ''

            # TODO: Revisar si las conformaciones del TF estan regulando
            for ri in ris:
                ri_cyc_id = utils.get_cyc_id_by_rdb_id(ri.get('_id'), self.ris_cyc_ids)
                try:
                    ri_parents = Regulator.pt_conn.get_frame_all_parents(
                        ri_cyc_id)
                    if '|Transcription-Factor-Binding|' in ri_parents:
                        if 'Transcription-Factor-Binding' not in self._regulation_type:
                            self._regulation_type = 'Transcription-Factor-Binding'
                    if '|Allosteric-Regulation-of-RNAP|' in ri_parents:
                        if 'Allosteric-Regulation-of-RNAP' not in self._regulation_type:
                            self._regulation_type = 'Allosteric-Regulation-of-RNAP'
                    if '|RNA-Mediated-Translation-Regulation|' in ri_parents:
                        if 'RNA-Mediated-Translation-Regulation' not in self._regulation_type:
                            self._regulation_type = 'RNA-Mediated-Translation-Regulation'
                except pythoncyc.PTools.PToolsError as pt_er:
                    print(pt_er, ri.get("_id"), ri_cyc_id)
            ris_size = len(list(ris))
            if ris_size >= 0 and self.regulator_type == 'transcriptionFactor':
                regulator_conformations = self.regulator_obj.active_conformations
                conformations_ids = []
                for conf in regulator_conformations:
                    conformations_ids.append(conf.id)
                ris = collection.find({
                    "regulator._id": {
                        '$in': conformations_ids
                    }
                })
                for ri in ris:
                    ri_cyc_id = utils.get_cyc_id_by_rdb_id(ri.get('_id'), self.ris_cyc_ids)
                    try:
                        ri_parents = Regulator.pt_conn.get_frame_all_parents(
                            ri_cyc_id)
                        if '|Transcription-Factor-Binding|' in ri_parents:
                            if 'Transcription-Factor-Binding' not in self._regulation_type:
                                self._regulation_type = 'Transcription-Factor-Binding'
                        if '|Allosteric-Regulation-of-RNAP|' in ri_parents:
                            if 'Allosteric-Regulation-of-RNAP' not in self._regulation_type:
                                self._regulation_type = 'Allosteric-Regulation-of-RNAP'
                        if '|RNA-Mediated-Translation-Regulation|' in ri_parents:
                            if 'RNA-Mediated-Translation-Regulation' not in self._regulation_type:
                                self._regulation_type = 'RNA-Mediated-Translation-Regulation'
                    except pythoncyc.PTools.PToolsError as pt_er:
                        print(pt_er, ri.get("_id"), ri_cyc_id)
        else:
            self._regulation_type = regulation_type
