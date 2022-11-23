import datetime, os, binascii, hashlib, base58, ecdsa, winsound, random
from tabulate import tabulate


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


def main():

    # Print program banner
    print("N-WORDS SEED PHRASE")
    print("Generate wallet from n-words in BIP39 wordlist")
    print("Check database for collisions\n")

    # Prompt user for input file
    while True:
        try:
            lines = []
            data = input("Enter winner file: ")
            with open(os.path.join('winner', data)) as f:
                lines = f.read().splitlines()
            break
        except FileNotFoundError:
            print("File not found, try again...\n")

    # Prompt user for number of words
    while True:
        try:
            n = int(input("Enter number of words in seed phrase: "))
            break
        except ValueError:
            print("Only accept numbers as input, try again...\n")

    # Load wordlist
    with open('wordlist/bip39.txt', 'r') as f:
        words = f.read().splitlines()

    # Initializing counter
    i = 1
    start_time = datetime.datetime.now().replace(microsecond=0)

    while True:

        # Generate key pair
        priv = hashlib.sha256(' '.join(random.sample(words, n)).encode('utf-8')).hexdigest()
        pub = publicKey(priv)
        add = address(pub)
        WIF = toWIF(priv).decode()

        if add in lines:
            
            # Create table for output
            header = ["Found on", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            table = [["Address", add], ["Key", WIF]]
            output = tabulate(table, header, tablefmt = "grid")
            print('')
            print(output)
            print('')

            # Write wallet to file
            with open('found.txt', 'a') as f:
                f.write(output)
                f.write('\n')
            winsound.Beep(2000, 1000)

        runtime = (datetime.datetime.now().replace(microsecond=0) - start_time)
        print(f"{i:,} generated in {runtime}.", end='')
        print('\r', end='')
        i += 1


if __name__ == '__main__':
	main()
