import datetime, os, binascii, hashlib
import base58, ecdsa, winsound
from tabulate import tabulate

def privateKey(): # Generates random 256 bit private key in hex format
    return binascii.hexlify(os.urandom(32)).decode('utf-8')


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
    print("RANDOM 32 BYTES")
    print("Generate wallets from random private key")
    print("Check database for collisions\n")

    # Read winner file to list
    with open('winner/small.txt', mode='r') as file:
        lines = file.read().splitlines()

    # start counter and timer
    i = 1
    start_time = datetime.datetime.now().replace(microsecond=0)

    while True:

        # Generate key pair
        priv = privateKey()
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

            # Raise alarm
            for _ in range(15):
                winsound.Beep(2000, 150)
            input("")

        runtime = (datetime.datetime.now().replace(microsecond=0) - start_time)
        print(f"{i:,} generated in {runtime}.", end='')
        print('\r', end='')
        i += 1


if __name__ == '__main__':
	main()
