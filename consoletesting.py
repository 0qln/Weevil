import sys, os

while True:
    user_input = input("Enter your input (type 'exit' to quit): ")

    if user_input.lower() == 'exit':
        print("Exiting the program...")
        break  # Exit the loop if the user types 'exit'

    else:
        # Clear the input line
        print("\033[A" + " " * os.get_terminal_size().columns, end="\r")  

        print("output")