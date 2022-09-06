import sys
import re
import pickle
print("This is the name of the program:", sys.argv[0])
  
print("Argument List:", str(sys.argv))

class Person:
    first = ""
    last = ""
    mi = ""
    id = ""
    phone = ""

    def __init__(self,person):
        self.first = person['first']
        self.last = person['last']
        self.mi = person['mi']
        self.id = person['id']
        self.phone = person['phone']

    def display(self):
        print("Employee id: {3}\n\t{0} {2} {1}\n\t{4}\n".format( self.first, self.last, self.mi, self.id, self.phone))

#Processes the line into a list of dictionaries for person attributes
def process_data():
    people = []
    with open(sys.argv[1]) as file: 
        file.readline()
        for line in file.readlines():
            #split each line by comma
            proc_line = line.split(",")
            person = {}
            
            #capitalize first and last
            person["first"] = proc_line[0].capitalize()
            person["last"] = proc_line[1].capitalize()
            
            #capitalize initial or set to 'X'
            proc_line[2] = proc_line[2].upper()
            if(not proc_line[2]):
                proc_line[2] = 'X'
            person["mi"] = proc_line[2]

            #validate id number
            while(not re.search('\S\S\d\d\d\d',proc_line[3])):
                print("ID invalid:",proc_line[3])
                print("ID is two letters followed by 4 digits\nPlease enter a valid id: ")
                proc_line[3] = input()
            person["id"] = proc_line[3]

            #format phone number
            proc_line[4]=re.sub('\D','',proc_line[4])
            proc_line[4]=re.sub(r'(\d{3})(\d{3})(\d{4})', r'\1-\2-\3', proc_line[4])
            person["phone"] = proc_line[4]

            #pickle person
            people.append(person)
        pickle.dump(people,open('dict.p', 'wb'))
        #print(data)

process_data()
print("Employee List:\n")
people = pickle.load(open('dict.p','rb'))
for person in people:
    _person = Person(person)
    _person.display()
