doc_list=['The Learn Python Challenge Casino has a big casino full of casino games', 'They bought a car', 'Casinoville']

def word_search(doc_list, keyword):
    """
    Takes a list of documents (each document is a string) and a keyword.
    Returns list of the index values into the original list for all documents
    containing the keyword.

    Example:
    doc_list = ["The Learn Python Challenge Casino.", "They bought a car", "Casinoville"]
    >>> word_search(doc_list, 'casino')
    >>> [0]
    """
    found = []
    keyword = keyword.lower()
    for index, st in enumerate(doc_list):
        splitted = st.replace(".", "").replace(",", "").split()
        for word in splitted:
            if keyword == word.lower():
                found.append(index)
                break
    print(found)
    return found





def multi_word_search(doc_list, keywords):
    """
    Takes list of documents (each document is a string) and a list of keywords.
    Returns a dictionary where each key is a keyword, and the value is a list of indices
    (from doc_list) of the documents containing that keyword

    >>> doc_list = ["The Learn Python Challenge Casino.", "They bought a car and a casino", "Casinoville"]
    >>> keywords = ['casino', 'they']
    >>> multi_word_search(doc_list, keywords)
    {'casino': [0, 1], 'they': [1]}
    """

    dictionary = {}
    for word in keywords:
        res = word_search(doc_list, word)
        dictionary[word] = res
    return dictionary

multi_word_search(doc_list, ['casino'])