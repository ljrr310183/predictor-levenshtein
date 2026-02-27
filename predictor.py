from Levenshtein import distance as levenshtein_distance
from dictionary import DICTIONARY

def get_best_matches(partial_string:str, max_results:int = 5)->list:
    """ Search similar word inside dictionary using levenshtein """
    #basic security, minimum chars allowed >= 2
    if not partial_string or len(partial_string) < 2:
        return []

    #normalize_word
    partial_string = partial_string.lower().strip()

    #list to store results
    results = []

    #iterate over dictionary
    for word in DICTIONARY:
        #calculate distance
        distance = levenshtein_distance(partial_string, word)

        if distance <= 2:
            results.append({
                "word": word,
                "distance": distance
            })

    #sort results by distance
    results.sort(key=lambda x: x["distance"])

    #return only the best matches
    return results[:max_results]