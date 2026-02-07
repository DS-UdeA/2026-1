// This program displays the contents of the inventory file.
#include <iostream>
#include <fstream>

using namespace std;

const int DESC_SIZE = 31; // Description size

// Declaration of InventoryItem structure
struct InventoryItem
{
    char desc[DESC_SIZE];
    int qty;
    double price;
};

int main()
{
    InventoryItem record; // To hold an inventory record

    // Open the file for binary input.
    fstream inventory("Inventory.dat", ios::in | ios::binary);
    if (!inventory)
    {
        cerr << "ERROR: Cannot open Inventory.dat\n";
        return 1;
    }

    // Now read and display the records.
    while (inventory.read(reinterpret_cast<char*>(&record), sizeof(record)))
    {
        cout << "Description: " << record.desc << endl;
        cout << "Quantity: " << record.qty << endl;
        cout << "Price: " << record.price << endl << endl;
    }

    // Close the file.
    inventory.close();
    return 0;
}
