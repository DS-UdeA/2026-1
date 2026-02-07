// This program asks the user for a file name. The file is
// opened and its contents are displayed on the screen.
#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main()
{
    string fileName; // To hold the file name
    char ch;         // To hold a character
    fstream file;    // File stream object

    // Get the file name
    cout << "Enter a file name: ";
    cin >> fileName;

    // Open the file.
    file.open(fileName, ios::in);

    // If the file was successfully opened, continue.
    if (file)
    {
        // Get characters from the file and display them.
        while (file.get(ch))
        {
            cout << ch;
        }

        // Close the file.
        file.close();
    }
    else
    {
        cout << fileName << " could not be opened.\n";
    }

    return 0;
}
