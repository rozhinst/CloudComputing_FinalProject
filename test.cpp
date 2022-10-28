#include <iostream>
#include <fstream>
#include <string>
using namespace std;
int main(int argc, char* argv[]){
   printf("hello world!");
   fstream newfile;
   newfile.open(argv[1],ios::out);  // open a file to perform write operation using file object
   if (newfile.is_open()){   //checking whether the file is open
      string tp;
      while(getline(newfile, tp)){ //read data from file object and put it into string.
         cout << "hello world";
         std::cout << tp << "\n"; //print the data of the string
      }
      newfile.close(); //close the file object.
   }
}