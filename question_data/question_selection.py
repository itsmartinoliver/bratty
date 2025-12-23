import random 

history_path = "question_data/history.txt"
questions_path = "question_data/questions.tsv"

max_entries = 9     
# Determines the number of questions that are stored in history and barred from being repeated.
# The last {max_entries} questions cannot be chosen again

def clear_history():
    with open(history_path, "r+") as history_fp:
        history_fp.truncate(0)

def make_question_lists():
    """
    Returns parallel lists:
        questions: contains each question as a string
        weights: contains the weightings of each question as a float
    """
    questions = []
    weights = []
    with open(questions_path, "r") as questions_fp:
        for line in questions_fp.readlines()[1:]:  # skip header
            split_line = line.split("\t")
            questions.append(split_line[0].strip()) # strip() is just for safety, shouldn't normally have any effect
            weights.append(float(split_line[1]))
    return questions, weights

def remove_recent(questions, weights):
    """
    Produces new parallel lists (questions, weights) containing only the questions that
    do NOT appear in history.txt
    """
    if(len(questions) != len(weights)):
        raise RuntimeError("Questions and Weights do not have the same length")

    history_entries = []
    with open(history_path, "r") as history:
        for line in history.readlines():
            history_entries.append(line.strip())
    new_questions = []
    new_weights = []

    for i in range(len(questions)):
        if questions[i] not in history_entries:
            new_questions.append(questions[i])
            new_weights.append(weights[i])

    return new_questions, new_weights
    
def choose_question():
    questions, weights = make_question_lists()
    questions, weights = remove_recent(questions, weights)
    # Using random.choices to utilize weights. This returns a list, so we need to index the element
    question_choice = random.choices(questions, weights=weights)[0]
    add_to_history(question_choice)
    return question_choice

def add_to_history(new_entry):
    with open(history_path, "r") as history_fp:
        lines = history_fp.read().split("\n")   # splitting to also get rid of the \n for now
        while len(lines) >= max_entries:
            lines.pop(0)    # remove the top line, which is the oldest entry
        lines.append(new_entry)    # final entry did not previously have a new line, must add it now
    
    with open(history_path, "w") as history_fp:
        history_fp.write("\n".join(lines))


if __name__ == "__main__":
    print(choose_question())