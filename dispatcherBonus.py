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

base_python_install_command = "pip install -r "
base_python_compile_command = "python3 "
base_cpp_compile_command = "g++ -o "
cpp_run_command = "./program"

output_dorectory = ''

client = docker.from_env()

for container in client.containers.list():
        print(container)
        idle_containers.append(container)
        containers_lock[container] = threading.Lock()
        container.exec_run(cmd="mkdir /app/bonus")


def handle_input(input):
        global output_directory
        global library_file
        n = len(input)-1
        commands = []
        for i in input[1:n-1].split('>, '):
                commands.append(i.replace('<', ''))
        output_directory = commands.pop(len(commands)-1)
        library_file = commands.pop(len(commands)-1)

        add_to_queue(commands)
        return output_directory , library_file


def add_to_queue(commands):
        for command in commands:
                queue.append(command.replace(',',''))


def dispatch(output_dir, lib_file):
        global commands_counter
        print("in dispatch")

        while len(queue) > 0:
                command = queue.pop(0)
                print(commands_counter)
                if '.py' in command:
                        t = threading.Thread(target=running_command, args=(command,commands_counter, lib_file, ))
                else:
                        t = threading.Thread(target=running_cpp_command, args=(command,commands_counter, lib_file, ))
                t.start()
                command_counter_lock.acquire()
                commands_counter += 1
                command_counter_lock.release()




def running_command(command, command_id, lib_file):
        global output_directory
        while len(idle_containers) == 0:
                continue
        #lock.acquire()
        container = idle_containers.pop(0)
        containers_lock[container].acquire()
        #lock.release()

        try:
                print('{} : {} command running on container {}'.format(command_id, command.split(' ')[0], container.name))
                data_file = command.split(' ')[1]
                program_file = command.split(' ')[0]
                print('data file : {}'.format(data_file))
                os.system('sudo docker cp {} '.format(lib_file)+container.name+':/app/bonus')
                os.system('sudo docker cp {} '.format(data_file)+container.name+':/app/bonus')
                os.system('sudo docker cp {} '.format(program_file)+container.name+':/app/bonus')
                print("library installation",lib_file)
                exit_code, output = container.exec_run(cmd=base_python_install_command +"bonus/"+ lib_file)
                print(output[0],output[1])
                print("install finished")
                exit_code, output = container.exec_run(cmd=base_python_compile_command + "/app/bonus/" + program_file + " " + data_file, demux=True)
                print(base_python_compile_command + "/app/bonus/"+program_file+" " + data_file)
                print(output[0],output[1])
                write_to_file(output_directory+str(command_id)+'_'+command.split(' ')[0]+'_output', 'command {} :'.format(command_id)+output[0].decode("utf-8"))
                print('command id {} is finished'.format(command_id))


        except Exception as e:
                print("Container is not healthy")

        finally:
                print('____________________________________________________')
                container.exec_run(cmd="pip uninstall -r " +"bonus/"+ lib_file)
                container.exec_run(cmd="rm -r /app/bonus/*")
                containers_lock[container].release()
                lock.acquire()
                idle_containers.append(container)
                lock.release()




def running_cpp_command(command, command_id, lib_file):
        global output_directory
        while len(idle_containers) == 0:
                continue
        #lock.acquire()
        container = idle_containers.pop(0)
        containers_lock[container].acquire()
        #lock.release()

        try:
                print('{} : {} command running on container {}'.format(command_id, command.split(' ')[0], container.name))
                data_file = command.split(' ')[1]
                program_file = command.split(' ')[0]
                print('data file : {}'.format(data_file))
#                os.system('sudo docker cp {} '.format(lib_file)+container.name+':/app/bonus')
                os.system('sudo docker cp {} '.format(data_file)+container.name+':/app/bonus')
                os.system('sudo docker cp {} '.format(program_file)+container.name+':/app/bonus')
 #               print("library installation",lib_file)
 #               exit_code, output = container.exec_run(cmd=base_python_install_command +"bonus/"+ lib_file)
 #               print(output[0],output[1])
 #              print("install finished")
                exit_code, output = container.exec_run(cmd=base_cpp_compile_command + "/app/bonus/"+program_file.split('.')[0] +" /app/bonus/" + program_file, demux=True)
                print(output[0],output[1],"here")
                exit_code, output = container.exec_run(cmd="/app/bonus/" + program_file.split('.')[0] + " " + data_file, demux=True)
                print(output,"here2")
                write_to_file(output_directory+str(command_id)+'_'+command.split(' ')[0]+'_output', 'command {} :'.format(command_id)+output[0].decode("utf-8"))
                os.system('sudo docker cp '+container.name+':/app/bonus/' + program_file.split('.')[0] + ' ' +output_directory + program_file.split('.')[0])
                print('command id {} is finished'.format(command_id))


        except Exception as e:
                print("Container is not healthy")

        finally:
                print('____________________________________________________')
                container.exec_run(cmd="rm -r /app/bonus/*")
                containers_lock[container].release()
                lock.acquire()
                idle_containers.append(container)
                lock.release()



def write_to_file(output_name,input):
        f = open(output_name+".txt", "a")
        f.write(input)
        f.close()


inp = input('enter input or x (for exit)')
while (inp != 'x'):

        output_dir, lib_file = handle_input(inp)
#       print(queue)
        t = threading.Thread(target=dispatch, args=(output_dir, lib_file, ))
        t.start()
        inp = input()
