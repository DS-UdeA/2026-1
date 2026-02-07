#include <iostream>
#include <fstream>

using namespace std;

// This program uses the << operator to write information to a file.

int main()
{
    fstream dataFile;
    dataFile.open("demofile.txt", ios::out);
    if (!dataFile)
    {
        cout << "File open error!" << endl;
        return -1;
    }
    cout << "File opened successfully.\n";
    cout << "Now writing information to the file.\n";
    dataFile << "Jones\n";
    dataFile << "Smith\n";
    dataFile << "Willis\n";
    dataFile << "Davis\n";
    dataFile.close();
    cout << "Done.\n";
    return 0;
}
