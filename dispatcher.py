import docker
import os
import threading
import random

idle_containers = []
queue = []
lock = threading.Lock()
containers_lock = {}
command_counter_lock = threading.Lock()

global commands_counter
commands_counter = 0

base_command = "python3 commands.py "

output_dorectory = ''

client = docker.from_env()

for container in client.containers.list():
        print(container)
        idle_containers.append(container)
        containers_lock[container] = threading.Lock()


def handle_input(input):
        global output_directory
        n = len(input)-1
        commands = []
        for i in input[1:n-1].split('>, '):
                commands.append(i.replace('<', ''))
        output_directory = commands.pop(len(commands)-1)

        add_to_queue(commands)
        return output_directory


def add_to_queue(commands):
        for command in commands:
                queue.append(command.replace(',',''))


def dispatch(output_dir):
        global commands_counter
        print("in dispatch")

        while len(queue) > 0:
                command = queue.pop(0)
                print(commands_counter)
                t = threading.Thread(target=running_command, args=(command,commands_counter,))
                t.start()
                command_counter_lock.acquire()
                commands_counter += 1
                command_counter_lock.release()


def running_command(command, command_id):
        global output_directory
        while len(idle_containers) == 0:
                continue
        # lock.acquire()
        container = idle_containers.pop(0)
        containers_lock[container].acquire()
        # lock.release()

        try:
                print('{} : {} command running on container {}'.format(command_id, command.split(' ')[0], container.name))
                data_file = command.split(' ')[1]
                print('data file : {}'.format(data_file))
                os.system('sudo docker cp {} '.format(data_file)+container.name+':/app')

                exit_code, output = container.exec_run(cmd=base_command + command, demux=True)


                if command.split(' ')[0] == 'wordcount':

                        write_to_file(output_directory+str(command_id)+'_output', 'command {} :\n'.format(command_id))

                        words_dict = output[0].decode("utf-8")
                        words_dict = (words_dict[1:len(words_dict)-2].replace(':', '').replace(',', '').split(' '))
                        dict = {}

                        for i in range(0, len(words_dict), 2):

                                dict[words_dict[i]] = words_dict[i+1]
                        words_dict = dict
                        print(words_dict)

                        for word in words_dict.keys():
                                print(word, ' ', words_dict.get(word))
                                write_to_file(output_directory+str(command_id)+'_'+command.split(' ')[0]+'_output', (word+' '+words_dict[word])+'\n',flag='a')
                else:
                        write_to_file(output_directory+str(command_id)+'_'+command.split(' ')[0]+'_output', 'command {} :'.format(command_id)+output[0].decode("utf-8"))

                print('command id {} is finished'.format(command_id))


        except Exception as e:
                print("Container is not healthy")


        finally:
                print('____________________________________________________')
                containers_lock[container].release()
                lock.acquire()
                idle_containers.append(container)
                lock.release()
#                containers_lock[container].release()

def write_to_file(output_name,input,  flag='w'):
        f = open(output_name+ ".txt", flag)
        f.write(input)
        f.close()

inp = input('enter input or x (for exit)\n')
while (inp != 'x'):
        try:
                commands = open(inp)
                inp = commands.readline()
                output_dir = handle_input(inp)
#               print(queue)
                t = threading.Thread(target=dispatch, args=(output_dir,))
                t.start()
                inp = input()
        except Exception as e:
                print(e)
