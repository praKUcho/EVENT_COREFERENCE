import xml.etree.ElementTree as ET
import sys
import os

DEBUG = False
class words(object):

    def __init__(self, text, sentence_no, token_no, relation_id = None):
        self.text = text
        self.sentence_no = sentence_no
        self.token_no = token_no
        self.relation_id = relation_id

    def set_relation_id(self, relation_id):
        self.relation_id = relation_id

    def __str__(self):
        try:
            return self.text +'__'+ self.relation_id[0] + '__'+ self.relation_id[1]
        except TypeError:
            return self.text + '__NONE__NONE'

def parseDocument(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    related_events = {}
    mid_2_tid = {}
    mid_2_event_tag = {}
    tag_descriptor = {}
    tokens = {} #sentences in news article, Each elemnt is a list of tokens in that sentence
    doc_name = root.attrib['doc_name']
    cur_mid = ''
    for action in root.find('Markables').iter():
        if action.tag == 'Markables':
            continue
        elif action.tag == 'token_anchor':
            mid_2_tid[cur_mid].append(action.attrib['t_id'])
        else:
            cur_mid = action.attrib['m_id']
            if 'TAG_DESCRIPTOR' in action.attrib:
                try:
                    mid_2_event_tag[cur_mid] = (action.attrib['TAG_DESCRIPTOR'], action.attrib['instance_id'])
                    tag_descriptor[action.attrib['instance_id']] = action.attrib['TAG_DESCRIPTOR']
                except KeyError:
                    mid_2_event_tag[cur_mid] = ('UKNOWN_TAG', "UNKNOWN_INSTANCE_ID")
                    tag_descriptor["UNKNOWN_INSTANCE_ID"] = "UNKNOWN_TAG"
            else:
                mid_2_tid[cur_mid] = []

    cur_instance_id =''
    source_ids = []
    for cross_doc_coref in root.find('Relations').findall('CROSS_DOC_COREF'):
        for child in cross_doc_coref.iter():
            if child.tag == 'CROSS_DOC_COREF':
                related_events[child.attrib['note']]=()
                cur_instance_id = child.attrib['note']
            else:
                if child.tag == 'source':
                    source_ids += (mid_2_tid[child.attrib['m_id']])
                else:
                    related_events[cur_instance_id] = (source_ids, mid_2_event_tag[child.attrib['m_id']][0])
                    source_ids = []

    for token in root.findall('token'):
        tokens[token.attrib['t_id']] = words(token.text, token.attrib['sentence'], token.attrib['number'])

    for key in related_events:
        for token_id in related_events[key][0]:
            tokens[token_id].set_relation_id((key,related_events[key][1]))

    sentence_no = '-1'
    document = []
    sentence = []
    tokens = {int(key):value for key,value in tokens.items()}
    for token_key in sorted(tokens):
        if tokens[token_key].sentence_no == sentence_no:
            sentence.append(tokens[token_key])
        else:
            document.append((sentence,doc_name))
            sentence_no = tokens[token_key].sentence_no
            sentence = [tokens[token_key]]
    document.append((sentence,doc_name))
    return tokens,document

def print_document_tagged(tokens, filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    file = open(filename, 'w')
    sentence_no = '-1'
    for token_key in (tokens):
        if tokens[token_key].sentence_no == sentence_no:
            try:
                file.write('\t\t'+tokens[token_key].__str__())
            except UnicodeEncodeError:
                file.write('\t\t' + tokens[token_key].__str__().encode('ascii','ignore'))
                if DEBUG:
                    print "------------------UNICODE ERROR-----------------"
                    print tokens[token_key].__str__(), " changed to ", tokens[token_key].__str__().encode('ascii','ignore')
        else:
            sentence_no = tokens[token_key].sentence_no
            try:
                file.write('\n\n'+tokens[token_key].__str__())
            except UnicodeEncodeError:
                file.write('\n\n' + tokens[token_key].__str__().encode('ascii','ignore'))
                if DEBUG:
                    print "--------------UNICODE ERROR---------------------"
                    print tokens[token_key].__str__(), " changed to ", tokens[token_key].__str__().encode('ascii','ignore')

def print_document_text(tokens, filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    file = open(filename, 'w')
    sentence_no = '-1'
    for token_key in (tokens):
        if tokens[token_key].sentence_no == sentence_no:
            try:
                file.write(' '+tokens[token_key].text)
            except UnicodeEncodeError:
                file.write(' ' + tokens[token_key].text.encode('ascii','ignore'))
                if DEBUG:
                    print "------------------UNICODE ERROR-----------------"
                    print tokens[token_key].text, " changed to ", tokens[token_key].text.encode('ascii','ignore')
        else:
            sentence_no = tokens[token_key].sentence_no
            try:
                file.write('\n'+tokens[token_key].text)
            except UnicodeEncodeError:
                file.write('\n' + tokens[token_key].text.encode('ascii','ignore'))
                if DEBUG:
                    print "--------------UNICODE ERROR---------------------"
                    print tokens[token_key].text, " changed to ", tokens[token_key].text.encode('ascii','ignore')

def write_rel_sentence(sentence):
    text = ''
    for token in sentence[0]:
        text += token.text.encode('ascii','ignore')+' '
    return text+sentence[1]+'\n'

def print_all_files(all_files, filename):
    file = open(filename, 'w')
    doc_dict = {}
    for document in all_files:
        for sentence in document:
            for token in sentence[0]:
                try:
                    if 'ACT' in token.relation_id[0]:
                        try:
                            doc_dict[token.relation_id].append(sentence)
                            break
                        except KeyError:
                            doc_dict[token.relation_id] = [sentence]
                            break
                except TypeError:
                    pass
    for relation_id in doc_dict:
        file.write("\n"+relation_id[0]+"  "+relation_id[1]+'\n')
        for sentence in doc_dict[relation_id]:
            file.write(write_rel_sentence(sentence))

def parseFolder(foldername):
    for subdir, dirs, files in os.walk(foldername):
        if DEBUG:
            print subdir
        if subdir[-1].isdigit():
            #start from here to merge them
            all_files = []
            for file in files:
                if file.endswith('xml'):
                    filename = os.path.join(subdir, file)
                    tokens, document = parseDocument(filename)
                    all_files.append(document)
                    outfilename = subdir+'/out_tagged/'+file[:-4]+'_tagged.txt'
                    print_document_tagged(tokens, outfilename)
                    outfilename = subdir+'/out_text/'+file[:-4]+'_tagged.txt'
                    print_document_text(tokens, outfilename)
            outfilename = subdir+'/'+subdir[-1]+'_all_files.txt'
            print_all_files(all_files, outfilename)

if __name__ == "__main__":
    args = sys.argv
    try:
        foldername = args[1]
        parseFolder(foldername)
        print "Output Format: OUT TEXT"
        print "Docs Text"
        print
        print "Output Format: OUT TAG"
        print "Each word is represented as word__InstanceID__TagDescriptor"
        print "Words are separated with double tab space"
        print "Sentences are separated with 2 newline character"
    except IndexError:
        print "Instruction: python parseECB.py folder_name(ECB+)"
