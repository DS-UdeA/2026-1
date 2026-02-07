// list.cpp
// program using C streams to read characters from a file
// and write them to the terminal screen
#include <stdio.h>
#include <string.h>

int main() {
    char ch;
    FILE *file; // pointer to file descriptor
    char filename[20];

    printf("Enter the name of the file: ");   // Step 1
    fgets(filename, 20, stdin);               // Step 2
    
    filename[strcspn(filename, "\n")] = 0; // remove newline character from the end of the filename

    file = fopen(filename, "r");              // Step 3: open the file for reading

    while (fread(&ch, 1, 1, file) != 0)       // Step 4a: read characters from the file
        fwrite(&ch, 1, 1, stdout);            // Step 4b: write characters to the screen 

    fclose(file);                             // Step 5: close the file
    return 0;
}
