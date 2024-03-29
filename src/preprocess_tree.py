import random

# Given a text file in UD format, return a list of dicts. Each dict is representing a sentence
# Each sentence has the following attributes:
# 1. sent_id: sentence id
# 2. text: raw text of that sentence
# 3. words: a list containing every word in that sentence
def read_ud_file(ud_path, min_sent_length=10):
    with open(ud_path, 'r', encoding='utf-8') as file:
        sentences = []

        # initialize the first sentence
        sentence = {}
        words = []
        for line in file:
            # lines start with #: metadata
            if 'sent_id' in line:
                sentence['sent_id'] = line.split(sep='=')[1].strip()
                continue
            if 'text' in line:
                sentence['text'] = line.split(sep='=')[1].strip()
                continue
            if '#' in line:
                continue

            # \n => end of a sentence
            if line == '\n':
                # finish and save the current sentence
                if len(words) < min_sent_length:
                    continue 
                else:
                    sentence['words'] = words
                    sentences.append(sentence)
                    sentence = {}
                    words = []
                    continue

            # read word line
            # sample: 2	While	while	SCONJ	IN	_	9	                mark	    9:mark	_
            #         # text    lemma   upos            arrow from word     relation
            words.append(line.split(sep='\t'))
        print(f'Successfully loaded UD treebank: "{ud_path}". It has {len(sentences)} trees.')
        return sentences

# Given a sentence, return a dict showing forward arrows.
# Example: key: 7, value:[4, 5, 6] means that word 7 has a forward arrow to word 4, 5, 6
def process_sentence(sentence):
    sent_len = len(sentence['words']) + 1 # add ROOT
    arrow_to_dict = {}  # arrow is from key to value
    for i in range(sent_len):
        arrow_to_dict[i] = []
    # print(arrow_to_dict)

    for word in sentence['words']:
        word_number = int(word[0])
        arrow_from = int(word[6])  # the arrow is from 'arrow_from' to 'word_number'
        arrow_to_dict[arrow_from].append(word_number)

    return arrow_to_dict

# Return the training instances for the given sentence, in the form discussed in the proposal
# min_num_dependent: minimum number of dependents that a head should have to be included in the training instance
def create_head_dependency(sentence, arrow_to_dict, min_num_dependent=3):
    sentence_data = []
    sent_len = len(sentence['words']) + 1  # add ROOT
    for head in arrow_to_dict:  # arrow: head -> dependent
        dependents = arrow_to_dict[head]
        if len(dependents) >= min_num_dependent:
            # create a training instance for this head
            instance = ['RAND'] * sent_len
            instance[head] = 'OPEN_PARENTHESIS'
            for dependent_index in dependents:
                instance[dependent_index] = 'CLOSE_PARENTHESIS'
            sentence_data.append(instance)
    return sentence_data

def generate_vocab(vocab_size=400, paren_tokens=50):
    max_len = len(str(vocab_size))
    vocab = []
    for i in range(vocab_size):
        len_str = len(str(i))
        if len_str < max_len:
            str_id = f'T{"0"*(max_len - len_str) + str(i)}'

        else: 
            str_id = f'T{i}'
        
        vocab.append(str_id)


    open_tokens = []
    close_tokens = []
    for i in range(paren_tokens): 
        len_str = len(str(i))

        if len_str < max_len: 
            open = f'({"0"*(max_len - len_str) + str(i)}'
            close = f'){"0"*(max_len - len_str) + str(i)}'
        else: 
            open = f'({i}'
            close = f'){i}'

        open_tokens.append(open)
        close_tokens.append(close)

    return vocab, open_tokens, close_tokens

def sample_one_sentence(inst, vocab, open_tokens, close_tokens):
    """ Samples random tokens for each training instance. 
    inst (List()): i.e. ['RAND', 'CLOSE_PARENTHESIS', 'OPEN_PARENTHESIS', 'RAND', 'RAND', 'CLOSE_PARENTHESIS', 'CLOSE_PARENTHESIS', 'RAND', 'RAND', 'RAND', 'RAND', 'RAND']
    """
    inst_tokens = []
    paren_idx = random.randint(0, len(open_tokens)-1)
    for t in inst: 
        if t == "OPEN_PARENTHESIS": 
            inst_tokens.append(open_tokens[paren_idx])
        elif t == "CLOSE_PARENTHESIS":
            inst_tokens.append(close_tokens[paren_idx])
        else: 
            inst_tokens.append(vocab[random.randint(0, len(vocab)-1)])
    return inst_tokens

# sentences = read_ud_file('data/en_pud-ud-test.conllu')
# for sentence in sentences:
#     arrow_to_dict = process_sentence(sentence)

#     training_instances = create_head_dependency(sentence, arrow_to_dict)
#     # print(training_instances)
#     # print(len(training_instances))
#     break


