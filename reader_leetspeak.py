import os, binascii, hashlib, base58, ecdsa, winsound, string, copy, re
from itertools import product
from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm

print("LEETSPEAK TEXT READER")
print("Read all unique combinations of LeetSpeak code.")
print("With punctuation and without punctuation.")
print("With space and without space.")
print("Both uppercase and lowercase.")
print("Original text omitted.")
print("Auto-save progress.\n")

# Read winner file
while True:
    try:
        lines = []
        winner = input("Enter winner file: ")
        with open(f"winner/{winner}", 'r') as f:
            lines = f.read().splitlines()
        break
    except FileNotFoundError:
        print("Invalid winner file, try again...\n")

# Initialize found list
found = []

# Letter map
low = {
        'a': ['4', '@'],
        'b': ['8', '13'],
        'e': ['3'],
        'g': ['6', '9'],
        'h': ['#'],
        'i': ['1', '!'],
        'o': ['0'],
        'r': ['2'],
        's': ['5', '$'],
        't': ['7'],
    }

medium = {
        'a': ['4', '@'],
        'b': ['8', '13'],
        'c': ['(', '<', '['],
        'e': ['3'],
        'g': ['6', '9', '&'],
        'h': ['#'],
        'i': ['1', '!'],
        'l': ['1_'],
        'o': ['0', '()', '[]'],
        'r': ['2', '|2'],
        's': ['5', '$'],
        't': ['7', '+'],
    }

high = {
        'a': ['4', '@',],
        'b': ['8', '13', '|3'],
        'c': ['(', '<', '[', '¢', '©'],
        'e': ['3', '€'],
        'f': ['|=', '/='],
        'g': ['6', '9', '&'],
        'h': ['#', ']-[', ')-(', '|-|', '}{'],
        'i': ['1', '!'],
        'l': ['1_', '|_'],
        'm': ['|v|'],
        'n': ['|v', '/v', '[\]', '|\|'],
        'o': ['0', '()', '[]'],
        'q': ['()_', '0_'],
        'r': ['2', '|2', 'Я'],
        's': ['5', '$', '§'],
        't': ['7', '+', '†'],
        'u': ['µ', '(_)', '|_|'],
        'v': ['\/', '|/'],
        'w': ['vv', '\/\/'],
        'x': ['><', ')('],
        'y': ['¥'],
        'z': ['7_']
    }


def publicKey(privatekey): # Private Key -> Public Key
    
    privatekey = binascii.unhexlify(privatekey)
    s = ecdsa.SigningKey.from_string(privatekey, curve = ecdsa.SECP256k1)
    
    return '04' + binascii.hexlify(s.verifying_key.to_string()).decode('utf-8')


def address(publickey): # Public Key -> Wallet Address
    
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    c = '0'; byte = '00'; zero = 0
    var = hashlib.new('ripemd160')
    var.update(hashlib.sha256(binascii.unhexlify(publickey.encode())).digest())
    a = (byte + var.hexdigest())
    doublehash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(a.encode())).digest()).hexdigest()
    address = a + doublehash[0:8]
    for char in address:
        if (char != c):
            break
        zero += 1
    zero = zero // 2
    n = int(address, 16)
    output = []
    while (n > 0):
        n, remainder = divmod (n, 58)
        output.append(alphabet[remainder])
    count = 0
    while (count < zero):
        output.append(alphabet[0])
        count += 1
        
    return ''.join(output[::-1])


def toWIF(privatekey): # Hex Private Key -> WIF format
    
    var80 = "80" + str(privatekey) 
    var = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(var80)).hexdigest())).hexdigest()

    return base58.b58encode(binascii.unhexlify(str(var80) + str(var[0:8])))


def split_into_sentences(text):
    
    # Sentence splitter variables
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov)"
    digits = "([0-9])"
    
    # Sentence splitter
    text = text.replace('“', '"').replace('‘', "'").replace('’', "'").replace('”', '"')
    text = text.replace('     ', '')
    text = text.replace('    ', '')
    text = text.replace('   ', '')
    text = text.replace('  ', '')
    text = text.replace('.)', ').')
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub("\d+:\d+", '', text)
    text = re.sub("\(\d+\)", '', text)
    text = re.sub("\[\d+\]", '', text)
    text = re.sub("\(\*\d+\)", '', text)
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    text = text.replace('  ', ' ')
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    
    return sentences


def save_winner(add, WIF, phrase):  
    
    # Create table for output
    header = ["Found on", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    table = [["Address", add], ["WIF", WIF], ["Seed", phrase]]
    output = tabulate(table, header, tablefmt = "grid")
    print('\n\n')
    print(output)

    # Write wallet to file
    with open('found.txt', 'a') as f:
        f.write(output)
        f.write('\n')
    winsound.Beep(2000, 1000)


def check(text):

    # Generate key pair
    priv = hashlib.sha256(text.encode('utf-8')).hexdigest()
    pub = publicKey(priv)
    add = address(pub)
    WIF = toWIF(priv).decode()

    # Save winner wallet
    if add in lines: 
        if not add in found:  

            # Add item to found list
            found.append(add)

            # Save winner to file
            save_winner(add, WIF, text)
            print("Winner successfully saved!\n")


def reader(text, x):

    # Key level
    if x == 1: lettermap = low
    if x == 2: lettermap = medium
    if x == 3: lettermap = high

    # Check for possible replacement letters
    letters = set()
    for char in text:
        if char.lower() in list(lettermap.keys()):
            letters.add(char.lower())

    # Get list of possible combinations
    arrays = []
    for letter in letters:
        arrays.append(lettermap[letter])
    combos = list(product(*arrays))

    check(text)

    # Check replaced text
    for j in tqdm(range(len(combos)), desc='Comb', ascii=' >=', leave=False):

        for i in range(12):

            if i == 0: replaced_text = text
            if i == 1: replaced_text = text.lower()
            if i == 2: replaced_text = text.upper()
            if i == 3: replaced_text = text.translate(str.maketrans('', '', string.punctuation))
            if i == 4: replaced_text = text.translate(str.maketrans('', '', string.punctuation)).lower()
            if i == 5: replaced_text = text.translate(str.maketrans('', '', string.punctuation)).upper()
            if i == 6: replaced_text = text.replace(' ', '')
            if i == 7: replaced_text = text.lower().replace(' ', '')
            if i == 8: replaced_text = text.upper().replace(' ', '')
            if i == 9: replaced_text = text.translate(str.maketrans('', '', string.punctuation)).replace(' ', '')
            if i == 10: replaced_text = text.translate(str.maketrans('', '', string.punctuation)).lower().replace(' ', '')
            if i == 11: replaced_text = text.translate(str.maketrans('', '', string.punctuation)).upper().replace(' ', '')

            for k in range(len(letters)):
                replaced_text = replaced_text.replace(list(letters)[k], combos[j][k])
                replaced_text = replaced_text.replace(list(letters)[k].upper(), combos[j][k])

            check(replaced_text)


def main():

    while True:

        # Choose key level
        while True:
            try:
                x = int(input("Choose key level (1. low, 2. medium, 3. high): "))
                if x in [1, 2, 3]:
                    break
                raise ValueError
            except ValueError:
                print("Not an option, try again...\n")

        # Enter input text file
        while True:
            try:
                entry = input("Enter text file to be processed: ")
                if f"{entry.replace('.txt', '')}_leetspeak_saved.txt" in os.listdir('text'):
                    load = input("Detected save file, want to continue from save file (y/n)? ")
                    if load == 'n':
                        pass
                    else:
                        entry = f"{entry.replace('.txt', '')}_leetspeak_saved.txt"
                with open(os.path.join('text', entry), 'r') as f:
                    text = f.read()
                break
            except FileNotFoundError:
                print(f"Couldn't open {entry}, try again...\n") 


        # Get file name
        entry = entry.replace('.txt', '').replace('_leetspeak_saved', '')
        
        # Split text into sentences
        sentences = split_into_sentences(text)

        # Make a deep copy of sentences
        save_file = copy.deepcopy(sentences)

        # Start loading bar and processing data
        print(f"\nProcessing {entry}...")
        for i in tqdm(range(len(sentences)), desc='Text', ascii=' >='):
            reader(sentences[i], x)
            save_file.pop(0)
            with open(f'text/{entry}_leetspeak_saved.txt', 'w') as f:
                f.write(' '.join(save_file))

        # Delete saved file once finished reading
        try:
            os.remove(f'text/{entry}_leetspeak_saved.txt')
        except OSError:
            pass

        # Finished reading notification
        for _ in range(8):
            winsound.Beep(1800, 100)
        print(f"Finished reading <{entry}.txt>, found {len(found)} items.")

        # Prompt for reading another file
        if input(f"\nRead other files (y/n)? ") == 'y':
            pass
        else:
            break


if __name__ == '__main__':
	main()
