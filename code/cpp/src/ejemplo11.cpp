// This program demonstrates the put member function.
#include <iostream>
#include <fstream>

using namespace std;

int main()
{
    char ch; // To hold a character

    // Open the file for output.
    ofstream dataFile("sentence.txt", ios::out);
    if (!dataFile)
    {
        cerr << "ERROR: Cannot open file.\n";
        return 1;
    }

    cout << "Type a sentence and be sure to end it with a ";
    cout << "period.\n";

    // Get a sentence from the user one character at a time
    // and write each character to the file.
    cin.get(ch);
    while (ch != '.')
    {
        dataFile.put(ch);
        cin.get(ch);
    }
    dataFile.put(ch); // Write the period.

    // Close the file.
    dataFile.close();
    return 0;
}
