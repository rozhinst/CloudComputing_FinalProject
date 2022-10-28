import sys

def handle_file(path, is_number=True):
        data = []
        with open(path) as f:
                for line in f:
                        if is_number:
                                data.append(int(line))
                        else:
                                data.extend(line.split())

        return data

def find_max(data):
        return max(data)

def find_min(data):
        return min(data)

def calc_average(data):
        return sum(data)/len(data)

def sort(data):
        data.sort(reverse=True)
        return data

def count_words(data):
        dict = {i:data.count(i) for i in data}
        return dict

def write_to_file(command,input):
        f = open(command+ ".txt", "w")
        f.write(input)
        f.close()


def main():
        command = sys.argv[1]
        data = handle_file(sys.argv[2])

        if command == "min":
                print(find_min(data))
        elif command == "max":
                print(find_max(data))
        elif command == "sort":
                print(sort(data))
        elif command == "average":
                print(calc_average(data))
        elif command == "wordcount":
                print(count_words(data))
        else:
                print("command is not valid")
main()