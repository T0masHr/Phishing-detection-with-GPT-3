# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import readEmail


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    path = input("Enter the path to email file: ") # comment out when using hardcoded poath below
    print("Using the following path: " + path) # comment out when using hardcoded poath below
    # path = r"C:\Users\tomas\OneDrive - Duale Hochschule Baden-Württemberg Stuttgart\Projekt\EmailFiles\Gremienwahlen.txt" # hardcoded path for dev
    readEmail.open_message(path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
