// listcpp.cpp
// list contents of file using C++ stream classes
#include <iostream>
#include <fstream>
#include <string>

int main() {
    char ch;
    std::ifstream file;        // flujo de entrada
    std::string filename;

    std::cout << "Enter the name of the file: " << std::flush;  // Step 1
    std::cin >> filename;                                       // Step 2

    file.open(filename, std::ios::in);                          // Step 3
    if (!file.is_open()) {
        std::cerr << "Error: cannot open file '" << filename << "'\n";
        return 1;
    }

    file >> std::noskipws;                                      // include whitespace

    while (true) {
        file >> ch;                                             // Step 4a
        if (file.fail()) break;
        std::cout << ch;                                        // Step 4b
    }

    file.close();                                               // Step 5
    return 0;
}
