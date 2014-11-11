f = open("instance_types_dbpedia.txt", "r")
out = open("instance_types_processed.txt", "w")

count = 0
curr = None
lst = []
for line in f:
    count += 1
    if count % 100000 == 0: print count
    curr_instance = line.split()[0].replace("<http://dbpedia.org/resource/", "").replace(">", "")
    curr_type = line.split()[1].replace("<http://dbpedia.org/ontology/", "").replace(">", "")
    if curr != None and curr_instance != curr:
        # new instance
        out.write(curr + "\t" + ", ".join(lst) + "\n")
        lst = [curr_type]
        curr = curr_instance
    else:
        # old instance
        curr = curr_instance
        lst.append(curr_type)
out.write(curr + ":" + ",".join(lst) + "\n")
out.close()
f.close()
