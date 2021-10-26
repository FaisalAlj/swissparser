import re
import argparse

# Our Argpase for the command prompt

parser = argparse.ArgumentParser(description="Swissparser")
parser.add_argument('-f', '--file', type=str, help='Path to our File')
parser.add_argument('-s', '--search', nargs='+', help='Search Strings', default=[])
parser.add_argument('-l', '--lines', nargs='+', help='Which Lines to print', default=None)
parser.add_argument('-p', '--pattern', type=str, help="Type On,to print the Records with the pattern")
args = parser.parse_args()


# Preparation of Search Terms

def prepareStrings(listofstring):
    z_name, z_term, no_Z_String = [], [], []
    sequence = None
    for string in listofstring:
        if "." in string:
            if not re.search("SQ", string, re.IGNORECASE):
                list_of_spliting = string.rsplit(".")
                z_name.append((list_of_spliting[0]).upper())
                z_term.append(list_of_spliting[1])
            else:
                sequence = string[3:].upper()
        else:
            no_Z_String.append(string)
    return z_name, z_term, no_Z_String, sequence


# Find The Search terms in a line

def pattern(source, record):
    record = (re.sub(r"[\n\t\s]*", "", record)).lower()
    found_pattern = []
    for patt in source:
        patt = re.sub(r"[\n\t\s]*", "", patt)
        if re.search(patt, record, re.IGNORECASE):
            found_pattern.append(patt)
    return found_pattern


# Add to Set ..... P.S : sets don't accept duplication !

def addtoset(set, items):
    for item in items:
        set.add(item)
    return set


#


def findwithPatter(file):
    new_record = None
    newS = set()
    seq = ""
    counter = 0

    for record in file:

        if record.startswith("ID"):  # Record's ID

            new_record = record
            counter += 1
            if counter % 10000 == 0:
                print(("*" * 10), counter, "Records processed", ("*" * 10))

        if record.startswith("//"):

            if (re.search(
                    r"MD(?:P|\w)(N|\w)C(?:S|\w)C(A|T|S|P|M|E|\w)(T|S|P|A|\w)(G|\w)(G|V|D|\w)(S|\w)(C|Y|\w)(T|A|M|S|\w)C(A|T|G|\w)(G|S|D|\w)(S|N|\w)C(K|T|\w)C(K|E|T|\w)(E|G|K|T|\w)(C|Y|\w)(K|N|\w)C(T|K|\w)(S|T|\w)(C|Y|\w)(K|W|\w)K(S|C|N|\w)CC(S|P|\w)CCP(v|M|A|L|P|\w)(G|S|E|\w)C(A|S|E|\w)KCA(Q|K|H|R|\w)(G|D|\w)C(V|I|T|\w)(C|R|\w)KG\w(S|L|A|\w)(E|D)(K|N)C(S|R)CC(A|P|D|Q|\w)",
                    seq)):
                newS.add(new_record)
                print("Found")
                continue

        if record.startswith("  "):
            seq_line = re.sub(r"[\n\t\s]*", "", record)
            seq += seq_line
    return newS


# Here to see which  Record meets the
# Search terms and then add it's ID to print it later


def findString(file, z_name=None, z_term=None, no_Z_String=None, sequence=None, patt=None):
    found_patt_set, found_patt_noZset = set(), set()
    found_ids = []
    seq = ""
    new_record = None
    counter = 0
    if (sequence is not None) or (no_Z_String is not None) or ((z_term is not None) and (z_name is not None)):

        for record in file:
            # Record's ID
            if record.startswith("ID"):
                new_record = record
                counter += 1
                if counter % 10000 == 0:
                    print(("*" * 10), counter, "Records processed", ("*" * 10))

            # End of a record , Now to see if we add this Record's ID to our List

            if record.startswith("//"):

                # We try to check if the length of the set(s) is the same as the length of the "list of terms"

                # If yes it means we found a record with all the wanted Search Terms and if not then we continue to search

                # No [no_Z_String = "Human""] (And) NO searchTerms with Preffix exp. ["ID.Human"] (And) only Seq

                if (not no_Z_String) and (not z_name) and (sequence):
                    if (re.search(sequence, seq, re.IGNORECASE)):
                        found_ids.append(new_record)

                # [no_Z_String = "Human""] (And)  ["ID.Human"]

                elif no_Z_String and z_name:

                    if sequence:  # IF Seq Available
                        if (re.search(sequence, seq, re.IGNORECASE)) and (len(found_patt_set) == len(z_term)) and (
                                len(found_patt_noZset) == len(no_Z_String)):
                            found_ids.append(new_record)
                    else:
                        if (len(found_patt_set) == len(z_term)) and (len(found_patt_noZset) == len(no_Z_String)):
                            found_ids.append(new_record)

                # For example [z_name "ID.Human"]

                elif z_name:

                    if sequence:  # IF Seq Available
                        if (re.search(sequence, seq, re.IGNORECASE)) and (len(found_patt_set) == len(z_term)):
                            found_ids.append(new_record)
                    else:
                        if (len(found_patt_set) == len(z_term)):
                            found_ids.append(new_record)

                # For example [no_Z_String = "Human""]

                elif no_Z_String:

                    if (len(found_patt_noZset) == len(no_Z_String)):
                        found_ids.append(new_record)

                found_patt_noZset = set()
                found_patt_set = set()
                seq = ""

            # From here we try to put all (the wanted Terms) that we found so far in the Record in (a) set(s)

            # For example... no_Z_String = "Human" (And) z_name =  "ID.Human"

            if z_name and no_Z_String:

                if record.startswith(tuple(z_name)):
                    found_patt = pattern(z_term, record)
                    found_patt_set = addtoset(found_patt_set, found_patt)
                found_patt_noZ = pattern(no_Z_String, record)
                found_patt_noZset = addtoset(found_patt_noZset, found_patt_noZ)

            # for Example z_name = "ID.Human"

            elif z_name:

                if record.startswith(tuple(z_name)):
                    found_patt = pattern(z_term, record)
                    found_patt_set = addtoset(found_patt_set, found_patt)

            # [no_Z_String = "Human""]

            elif no_Z_String:
                found_patt_noZ = pattern(no_Z_String, record)
                found_patt_noZset = addtoset(found_patt_noZset, found_patt_noZ)

            # IF Seq Available

            if sequence:
                if record.startswith("  "):
                    seq_line = re.sub(r"[\n\t\s]*", "", record)
                    seq += seq_line

    # now we try to compare each sequence wth our pattern String....in case we have a certain pattern in our minds

    if (patt is not None):
        file.seek(0)
        pat = findwithPatter(file)
        tempSET = set(found_ids)
        found_ids = list(tempSET.union(patt))

    return found_ids


def print_Records(found_ids, file, lines=None):
    count, what_record, actuall_record = 0, 0, 0
    if lines:
        lines = [x.upper() for x in lines]
        found_lines = set()
        if "SQ" in lines:
            lines.append("  ")

    for line in file:

        if line.startswith("ID"):
            what_record += 1
            if line in found_ids:
                actuall_record = what_record

        if what_record == actuall_record:

            if line.startswith("ID"):
                count += 1
                print("-" * 100)
            if lines is not None:

                if line.startswith(tuple(lines)):
                    print(line, end="")
                    start_ofLine = line[:2]
                    found_lines.add(start_ofLine)
                if line.startswith("//"):

                    if len(found_lines) < len(lines):
                        for x in lines:
                            if x not in found_lines:
                                print(x, " \t [not found] !!!!".upper())
            else:
                print(line, end="")
    print("-" * 100)
    print("ID(S) FOUND : ", count)
    print("-" * 100)


# Lines >>>> which lines should be printed out for Example the ones start with ID only

def swissparser(path, search=None, lines=None, patt=None):
    if search is not None:
        z_name, z_term, no_Z_String, sequence = prepareStrings(search)

    with open(path) as records:
        found_ids = findString(records, z_name=None, z_term=None, no_Z_String=None, sequence=None, patt=None)
        records.seek(0)
        print_Records(found_ids, records, lines)


# swissparser("unip1.txt",patt=not None,lines=["id","de"])
# # SQ.SVGYVDDTQFVRFDSDAASPRGEPRAP" "id.gorgo"

if __name__ == '__main__':
    swissparser(args.file, args.search, args.lines, args.pattern)
