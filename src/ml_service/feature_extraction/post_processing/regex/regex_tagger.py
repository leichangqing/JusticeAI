# -*- coding: utf-8 -*-
import os
import numpy
from util.file import Save
from util.log import Log
from util.constant import Path
from sys import stdout
from util.file import Load
from feature_extraction.post_processing.regex.regex_entity_extraction import EntityExtraction


class TagPrecedents:
    empty_line_length = 6

    def __init__(self):
        self.structured_data_dict = {}
        self.statements_tagged = 0
        self.text_tagged = 0
        self.nb_lines = 0
        self.nb_text = 0
        self.regexes = Load.load_binary("regexes.bin")
        self.precedents_directory_path = Path.raw_data_directory

    def get_intent_indice(self):
        """
        :return: primary key of every intent in a tuple (int, string)
        """
        facts_vector = []
        for i in range(len(self.regexes["regex_facts"])):
            facts_vector.append((i, self.regexes["regex_facts"][i][0]))

        demands_vector = []
        for i in range(len(self.regexes["regex_demands"])):
            demands_vector.append((i, self.regexes["regex_demands"][i][0]))

        outcomes_vector = []
        for i in range(len(self.regexes["regex_outcomes"])):
            outcomes_vector.append((i, self.regexes["regex_outcomes"][i][0]))

        return {
            'facts_vector': facts_vector,
            'demands_vector': demands_vector,
            'outcomes_vector': outcomes_vector
        }

    def tag_precedents(self, nb_files=-1):
        """
        Reads all precedents in a directory
        :param nb_files when -1 then read all directory
        :return: numpy matrix of facts
        """
        Log.write('Tagging precedents')
        for file in os.listdir(self.precedents_directory_path):
            if nb_files == -1:
                percent = float(
                    self.nb_text / len(os.listdir(self.precedents_directory_path))) * 100
            else:
                percent = float(self.nb_text / nb_files) * 100
                if self.nb_text > nb_files:
                    break
            stdout.write("\rPrecedents taged: %f " % percent)
            stdout.flush()
            self.structured_data_dict[file] = self.__tag_file(file)
            self.nb_text += 1
        Log.write('Precedent coverage: ' +
                  str(self.text_tagged / self.nb_text))
        Log.write('Line Coverage: ' +
                  str(self.statements_tagged / self.nb_lines))
        save = Save()
        save.save_binary('structured_data_dict.bin', self.structured_data_dict)
        return self.structured_data_dict

    def __tag_file(self, filename):
        """
        For every line in a precedent, tag facts
        When fact is found then its index is set to 1
        increments text tagged, line tagges to get a percentage
        of coverage at the end of the process
        :param filename: string
        :return: numpy vector of facts
        """
        facts_vector = numpy.zeros(len(self.regexes["regex_facts"]))
        demands_vector = numpy.zeros(len(self.regexes["regex_demands"]))
        outcomes_vector = numpy.zeros(len(self.regexes["regex_outcomes"]))
        file = open(self.precedents_directory_path + "/" +
                    filename, 'r', encoding="ISO-8859-1")
        text_tagged = False
        file_contents = file.read()
        statement_tagged = False
        self.nb_lines += len(file_contents.split('\n'))

        for i, (_, regex_array, regex_type) in enumerate(self.regexes["regex_facts"]):
            match = EntityExtraction.match_any_regex(file_contents, regex_array, regex_type)
            if match[0]:
                facts_vector[i] = match[1]
                statement_tagged = True
                text_tagged = True

        for i, (_, regex_array, regex_type) in enumerate(self.regexes["regex_demands"]):
            match = EntityExtraction.match_any_regex(file_contents, regex_array, regex_type)
            if match[0]:
                demands_vector[i] = match[1]
                statement_tagged = True
                text_tagged = True

        for i, (_, regex_array, regex_type) in enumerate(self.regexes["regex_outcomes"]):
            match = EntityExtraction.match_any_regex(file_contents, regex_array, regex_type)
            if match[0]:
                outcomes_vector[i] = match[1]
                statement_tagged = True
                text_tagged = True

        if statement_tagged:
            self.statements_tagged += 1
        file.close()
        if text_tagged:
            self.text_tagged += 1

        return {
            'facts_vector': facts_vector,
            'demands_vector': demands_vector,
            'outcomes_vector': outcomes_vector
        }
 
    def __ignore_line(self, line):
        """
        Verifies if we should ignore line from total count
        Add constraints to make covered lines more realistic
        :param line: String
        :return: Boolean
        """
        if len(line) < self.empty_line_length:
            return True
        elif 'No dossier' in line:
            return True
        return False


def run():
    # Models saved to ml_service//data/binary/
    tag = TagPrecedents()
    structured_data_dict = tag.tag_precedents(10)
    # prints fact intents
    indices = tag.get_intent_indice()

    Log.write("Total precedents parsed: {}".format(len(structured_data_dict)))
    for i in range(len(next(iter(structured_data_dict.values()))['facts_vector'])):
        total_fact = len([1 for val in structured_data_dict.values() if val['facts_vector'][i] == 1])
        Log.write("Total precedents with {:41} : {}".format(indices['facts_vector'][i][1], total_fact))

    for i in range(len(next(iter(structured_data_dict.values()))['demands_vector'])):
        total_fact = len([1 for val in structured_data_dict.values() if val['demands_vector'][i] == 1])
        Log.write("Total precedents with {:41} : {}".format(indices['demands_vector'][i][1], total_fact))

    for i in range(len(next(iter(structured_data_dict.values()))['outcomes_vector'])):
        total_fact = len([1 for val in structured_data_dict.values() if val['outcomes_vector'][i] == 1])
        Log.write("Total precedents with {:41} : {}".format(indices['outcomes_vector'][i][1], total_fact))