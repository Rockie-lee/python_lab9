import os
import json
import random
import re

HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
pages = {}
page_number = 0
line_window = {}
line_number = 0
char_window = []


def clean_line(line):
    return line.strip().replace('-', '') + ' '

def read_book(file_path):
    global char_window
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    with open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = clean_line(line)
            if line.strip():
                for c in line:
                    process_char(c)
    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()


def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()


def add_line():
    global char_window, line_number
    line_number += 1
    process_page(''.join(char_window), line_number)
    char_window.clear()


def process_page(line, line_num):
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()


def add_page():
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0


def process_books(*paths):
    for path in paths:
        read_book(path)


def generate_code_book():
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                code_book.setdefault(char, []).append(f'{page}-{num}-{pos}')
    return code_book


def save(file_path, book):
    with open(file_path, 'w') as fp:
        json.dump(book, fp)


def load(file_path, *key_books, reverse=False):
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp:
            return json.load(fp)
    else:
        process_books(*key_books)
        if reverse:
            save(file_path, pages)
            return pages
        else:
            code_book = generate_code_book()
            save(file_path, code_book)
            return code_book


def encrypt(code_book, message):
    cipher_text = []
    missing_chars = []

    for char in message:
        if char in code_book and code_book[char]:
            index = random.randint(0, len(code_book[char]) - 1)
            cipher_text.append(code_book[char].pop(index))
        else:
            missing_chars.append(char)

    if missing_chars:
        print(f"Error: The following characters are missing in the codebook: {', '.join(missing_chars)}")
        print("Please ensure your book files contain these characters or try a different message.")
        return None

    return '-'.join(cipher_text)


def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+-\d+-\d+', ciphertext):
        page, line, char = cc.split('-')
        plaintext.append(rev_code_book[page][line][int(char)])
    return ''.join(plaintext)


def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""")
    return int(input("Make a selection [1,2,3]: "))


def main():
    base_dir = os.path.dirname(__file__)
    key_books = (
        os.path.join(base_dir, 'books', 'War_and_Peace.txt'),
        os.path.join(base_dir, 'books', 'Moby_Dick.txt'),
        os.path.join(base_dir, 'books', 'Dracula.txt')
    )
    code_book_path = os.path.join(base_dir, 'code_books', 'dmdwp.txt')
    rev_code_book_path = os.path.join(base_dir, 'code_books', 'dmdwp_r.txt')

    os.makedirs(os.path.dirname(code_book_path), exist_ok=True)
    while True:
        try:
            choice = main_menu()
            if choice == 1:
                code_book = load(code_book_path, *key_books)
                message = input("Please enter your secret message: ")
                cipher_text = encrypt(code_book, message)
                if cipher_text:
                    print("Cipher text:", cipher_text)
            elif choice == 2:
                rev_code_book = load(rev_code_book_path, *key_books, reverse=True)
                message = input("Please enter your cipher text: ")
                print("Plain text:", decrypt(rev_code_book, message))
            elif choice == 3:
                break
        except ValueError as ve:
            print("Improper selection or error:", ve)
        except FileNotFoundError as fe:
            print("File not found error:", fe)


if __name__ == '__main__':
    main()


