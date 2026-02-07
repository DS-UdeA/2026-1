// This program demonstrates reading from one file and writing
// to a second file.
#include <iostream>
#include <fstream>
#include <string>
#include <cctype>   // Needed for the toupper function.

using namespace std;

int main()
{
    string fileName;   // To hold the file name
    char ch;           // To hold a character
    ifstream inFile;   // Input file

    // Open a file for output.
    ofstream outFile("out.txt");
    if (!outFile)
    {
        cerr << "ERROR: Cannot open out.txt\n";
        return 1;
    }

    // Get the input file name.
    cout << "Enter a file name: ";
    cin >> fileName;

    // Open the file for input.
    inFile.open(fileName);
    if (!inFile)
    {
        cout << "Cannot open " << fileName << endl;
        return 1;
    }

    // Read from file 1 and write uppercase to file 2.
    while (inFile.get(ch))
    {
        outFile.put(static_cast<char>(toupper(static_cast<unsigned char>(ch))));
    }

    // Close the two files.
    inFile.close();
    outFile.close();

    cout << "File conversion done.\n";
    return 0;
}

