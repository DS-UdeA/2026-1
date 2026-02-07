// This program uses the write and read functions.
#include <iostream>
#include <fstream>

using namespace std;

int main()
{
    const int SIZE = 4;
    char data[SIZE] = { 'A', 'B', 'C', 'D' };
    fstream file;

    // Open the file for output in binary mode.
    file.open("test.dat", ios::out | ios::binary);
    if (!file)
    {
        cerr << "ERROR: Cannot open test.dat for output.\n";
        return 1;
    }

    // Write the contents of the array to the file.
    cout << "Writing the characters to the file.\n";
    file.write(data, sizeof(data));

    // Close the file.
    file.close();

    // Open the file for input in binary mode.
    file.open("test.dat", ios::in | ios::binary);
    if (!file)
    {
        cerr << "ERROR: Cannot open test.dat for input.\n";
        return 1;
    }

    // Read the contents of the file into the array.
    cout << "Now reading the data back into memory.\n";
    file.read(data, sizeof(data));
    if (!file)
    {
        cerr << "ERROR: Could not read expected bytes from test.dat.\n";
        return 1;
    }

    // Display the contents of the array.
    for (int count = 0; count < SIZE; count++)
        cout << data[count] << " ";
    cout << endl;

    // Close the file.
    file.close();
    return 0;
}
