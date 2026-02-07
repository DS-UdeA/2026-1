// This program demonstrates the tellg function.
#include <iostream>
#include <fstream>

using namespace std;

int main()
{
    long offset;     // To hold an offset amount
    long numBytes;   // To hold the file size
    char ch;         // To hold a character
    char again;      // To hold Y or N

    // Open the file for input.
    fstream file("letters.txt", ios::in);
    if (!file)
    {
        cerr << "ERROR: Cannot open letters.txt\n";
        return 1;
    }

    // Determine the number of bytes in the file.
    file.seekg(0L, ios::end);
    numBytes = static_cast<long>(file.tellg());
    cout << "The file has " << numBytes << " bytes.\n";

    // Go back to the beginning of the file.
    file.seekg(0L, ios::beg);

    // Let the user move around within the file.
    do
    {
        // Display the current read position.
        cout << "Currently at position " << file.tellg() << endl;

        // Get a byte number from the user.
        cout << "Enter an offset from the beginning of the file: ";
        cin >> offset;

        // Move the read position to that byte, read the
        // character there, and display it.
        if (offset >= numBytes || offset < 0) // Past the end or negative?
            cout << "Cannot read past the end of the file.\n";
        else
        {
            file.seekg(offset, ios::beg);
            if (file.get(ch))
                cout << "Character read: " << ch << endl;
            else
                cout << "Read error.\n";
        }

        // Does the user want to try this again?
        cout << "Do it again? ";
        cin >> again;

    } while (again == 'Y' || again == 'y');

    // Close the file.
    file.close();
    return 0;
}
