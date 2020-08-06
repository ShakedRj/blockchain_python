from constants import *
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
import os
import subprocess
import json
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account

from web3.middleware import geth_poa_middleware

load_dotenv()

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

w3.middleware_onion.inject(geth_poa_middleware, layer=0)

mnemonic = os.getenv('MNEMONIC')



def derive_wallets(coin):
    command='php .\derive -g --mnemonic="'+mnemonic+'" --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --format=json --numderive=3 --coin='+coin
    print (command)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    return json.loads(output)
    

coins={'btc-test':derive_wallets(BTCTEST),'eth':derive_wallets(ETH)}

print(coins)


def priv_key_to_account(coin,priv_key):
   
    if coin==ETH:
        return Account.privateKeyToAccount(priv_key)
    if coin==BTCTEST:
        return PrivateKeyTestnet(priv_key)

def create_tx(coin,account, recipient, amount):
    
    if coin==ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
    )
        return {
            "from": account.address,
            "to": recipient,
            "value": amount,
            "gasPrice": round(w3.eth.gasPrice*1.55),
            "gas": gasEstimate,
            "nonce": w3.eth.getTransactionCount(account.address),
            #"chainID": w3.eth.chainId
        }

    
    
    if coin==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)]) 


def send_tx(coin,account, recipient, amount):
    
     if coin==ETH:
        raw_tx = create_tx(ETH,account, recipient, amount)
        signed = account.sign_transaction(raw_tx)
        return w3.eth.sendRawTransaction(signed.rawTransaction)
        
    
    
     if coin==BTCTEST:
        raw_tx = create_tx(BTCTEST,account, recipient, amount)
        signed = account.sign_transaction(raw_tx)
        return NetworkAPI.broadcast_tx_testnet(signed)
        