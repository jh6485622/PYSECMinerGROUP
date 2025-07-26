import rich
import time
import nukehashing
import secrets
import multiprocessing
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os

ACCOUNT_LOG = "account.log" # need to already have one when use
AES_KEY = b'################################' # 16, 24, or 32 bytes long

def encrypt_amount(amount):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded = pad(str(amount).encode(), AES.block_size)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(encrypted).decode()

def decrypt_amount(encrypted_line):
    raw = base64.b64decode(encrypted_line)
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    decrypted = cipher.decrypt(raw)
    unpadded = unpad(decrypted, AES.block_size)
    return int(unpadded.decode())

def add_money(amount):
    current_amount = 0
    if not os.path.exists(ACCOUNT_LOG) or os.path.getsize(ACCOUNT_LOG) == 0:
        with open(ACCOUNT_LOG, 'w') as f:
            f.write(encrypt_amount(0))
    with open(ACCOUNT_LOG, 'r') as f1:
        try:
            current_amount = decrypt_amount(f1.read())
        except Exception:
            current_amount = 0
    new_amount = current_amount + amount
    with open(ACCOUNT_LOG, 'w') as f2:
        f2.write(encrypt_amount(new_amount))

styles = {
    'log':      "[{ts}] {}",
    'info':     "[{ts}] [blue]{}[/blue]",
    'error':    "[{ts}] [red]{}[/red]",
    'success':  "[{ts}] [green]{}[/green]",
    'warning':  "[{ts}] [yellow]{}[/yellow]",
    'debug':    "[{ts}] [magenta]{}[/magenta]",
    'critical': "[{ts}] [bold red]{}[/bold red]",
}

def send_block_look(block_look):
    server = "localhost:17884"
    payload = {"block_look": block_look}
    try:
        response = requests.post('http://' + server + '/block_mining', json=payload)
        if response.ok:
            msg(f"Server response: {response.json()}", 'info')
            if response.json().get('status') == 'duplicate':
                msg("Block already exists on the server.", 'warning')
            else:
                msg("Block successfully sent to the server.", 'success')
                add_money(coin)
        else:
            msg(f"Failed to send block look: {response.text}", 'error')
    except Exception as e:
        msg(f"Error on AES or connecting: {e}", 'error')

def msg(info, Types='log', **kwargs):
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if Types == 'define':
        color = kwargs.get('color', 'white')
        icon = kwargs.get('icon', ':')
        rich.print(f"[{color}][{icon}] {info}[/{color}]")
    else:
        style = styles.get(Types, "[{ts}] [white]{}[/white]")
        rich.print(style.format(info, ts=ts))

def mine_worker(args):
    block_data, difficulty, rnd, start_nonce, step = args
    prefix = '0' * difficulty
    nonce = start_nonce
    while True:
        text = f"{block_data}{nonce}"
        hash_result = nukehashing.zerobumpnuke(text + rnd, 'salt').digest()
        if hash_result.startswith(prefix):
            return nonce, hash_result
        nonce += step

def mine_parallel(block_data, difficulty=2, workers=2):
    global coin
    t1 = time.time()
    msg("Starting parallel mining...", 'info')
    msg(f"Block data: {block_data}", 'debug')
    msg(f"Difficulty: {difficulty}", 'debug')
    msg(f"Workers: {workers}", 'debug')
    rnd = secrets.token_hex(8)
    pool = multiprocessing.Pool(workers)
    args = [(block_data, difficulty, rnd, i, workers) for i in range(workers)]
    result = pool.map(mine_worker, args)
    pool.terminate()
    for res in result:
        if res:
            t2 = time.time()
            elapsed = t2 - t1
            msg(f"Block mined! Nonce: {res[0]}", 'success')
            msg(f"Time taken: {elapsed:.2f} seconds", 'info')
            msg(f"Hash: {res[1]}", 'info')
            msg(f"Random value used: {rnd}", 'debug')
            msg(f"Difficulty: {difficulty}", 'debug')
            msg(f"Workers used: {workers}", 'debug')
            msg(f"Block data: {block_data}", 'debug')
            block_look = res[1] + str(res[0]) + rnd
            coin = difficulty * 1000 + int(difficulty * 10000 / (res[0] + 1))+ (16 - len(rnd.removeprefix('0'))) + int(int((elapsed + 1) * 10) * difficulty / (elapsed / 10)) - workers + 1
            msg(f"Block look: {block_look}", 'debug')
            msg(f"Block reward: {coin}", 'debug')
            msg(f"Adding {coin} PYSEC to the wallet", 'info')
            send_block_look(block_look)
            return res[0], res[1]

if __name__ == "__main__":
    block_data = "example_block_data"
    difficulty = 2
    workers = 2
    msg("Starting NukeHash mining...", 'info')
    for i in range(3):
        mine_parallel(block_data, difficulty, workers)
    msg(f"{decrypt_amount(open("account.log", 'r').read())} PYSEC in the account", 'info')
