
def reprocess_chunks(content, word):

    combined = "".join(content)

    first_index = combined.find(word)
    last_index = first_index + len(word) - 1
    word_indices = list(range(first_index, last_index + 1))

    # get first and last chunk index
    index_counter = 0
    for i, chunk in enumerate(content):
        for char in chunk:
            if index_counter == first_index:
                first_chunk_index = i
            if index_counter == last_index:
                last_chunk_index = i
            index_counter += 1

    # get modified chunks
    index_counter = 0
    modified_chunks = []
    for i, chunk in enumerate(content):
        new_chunk = ""
        for char in chunk:
            if i >= first_chunk_index or i <= last_chunk_index:
                if index_counter in word_indices:
                    pass
                else:
                    new_chunk += char
            else:
                new_chunk += char
            index_counter += 1
        modified_chunks.append(new_chunk)

    # insert the chunks
    # print("pre", modified_chunks)
    modified_chunks.insert(last_chunk_index, word)
    return modified_chunks


# # chunks = ["The f", "o", "x jumped."]
# # word = "fox"
# chunks = ["Placeholder <A", "-12", "3> in", "the sentence"]
# word = "<A-123>"
# new_chunks = reprocess(chunks, word)
# print(chunks)
# print(new_chunks)  # Output should be ['Hel', 'lo', ' wo', 'rld']
