
dataset_name = "dd"
#dataset_name = "enzymes"
#dataset_name = "imdb_binary"
#dataset_name = "mutag"
#dataset_name = "nci1"
#dataset_name = "nci109"
#dataset_name = "proteins"
#dataset_name = "ptc"

in_f = open("../data/"+dataset_name+"/"+dataset_name+"_graph.txt").readlines()
out_f = open("../data/"+dataset_name+"/"+dataset_name+"_ord_graph.txt", "w")

e_ord = 0
for line in in_f:
    if line.startswith("t"):
        e_ord = 0

    if line.startswith("e"):
        line = line.replace("\n", " "+str(e_ord)+"\n")
        e_ord += 1

    out_f.write(line)