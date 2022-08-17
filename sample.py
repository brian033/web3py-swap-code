from web3 import Web3
import abis
import os
import time

#take sushiswap for example
#connect to the rpc
RPC_URL = "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

#constants
SUSHI_ROUTER_ADDRESS = "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
#in case it's not checksumed 
SUSHI_ROUTER_ADDRESS = Web3.toChecksumAddress(SUSHI_ROUTER_ADDRESS)
#get this from etherscan, basically you can use this on every univ2 fork 
SUSHI_ROUTER_ABI = abis.SUSHI_ROUTER_ABI
#create a uniV2 router contract object with address and abi
sushi_router_contract = w3.eth.contract(SUSHI_ROUTER_ADDRESS, abi = SUSHI_ROUTER_ABI)

def approve(_w3, _tokenAddr, _to, _amount):
    TOKEN_ABI = abis.ERC20_TOKEN_ABI
    token_contract = _w3.eth.contract(Web3.toChecksumAddress(_tokenAddr), abi = TOKEN_ABI)
    #gets the symbol by a simple call
    symbol = token_contract.functions.symbol().call()
    decimals = token_contract.functions.decimals().call()
    print(f"Approving spending limit to {_amount} {symbol} for {_to}...")
    #you need to export it first
    private_key = os.environ.get("p")
    signer_address = _w3.eth.account.privateKeyToAccount(private_key).address
    #estimate gas first 
    tx = token_contract.functions.approve(
        Web3.toChecksumAddress(_to), _amount
        )
    gas_estimate = tx.estimateGas(
            {'from': signer_address}
        )
    print(f"gas approximation: {gas_estimate}")
    #build tx
    tx = tx.buildTransaction(
        {
            'chainId': _w3.eth.chain_id,
            'gas': gas_estimate,
            #only estimation
            'maxFeePerGas': _w3.toWei(100, 'gwei'),
            'maxPriorityFeePerGas': _w3.toWei(2, 'gwei'),
            'nonce': _w3.eth.get_transaction_count(signer_address)
        }
    )
    signed_tx = _w3.eth.account.sign_transaction(tx, private_key=private_key)
    _w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    tx_hash = w3.toHex(w3.keccak(signed_tx.rawTransaction))
    print(f"Txhash:{tx_hash}")
    
def swap(_w3, _tokenFrom, _tokenTo, _amountIn, _slipperage):
    print("Aping...")
    getamountsOut = sushi_router_contract.functions.getAmountsOut(
        _amountIn,
        [_tokenFrom, _tokenTo]
    ).call()
    minOut = int(getamountsOut[1] * (1 - _slipperage * 0.01))
    private_key = os.environ.get("p")
    signer_address = _w3.eth.account.privateKeyToAccount(private_key).address

    tx = sushi_router_contract.functions.swapExactTokensForTokens(
            _amountIn,#amountIn
            minOut,#amountOutMin
            [_tokenFrom, _tokenTo],#path
            signer_address,#to
            (int(time.time() )+ 3000),#deadline
        )
    gas_estimate = tx.estimateGas(
            {'from': signer_address}
        )
    print(f"gas approximation: {gas_estimate}")
    tx = tx.buildTransaction(
        {
            'chainId': _w3.eth.chain_id,
            'gas': gas_estimate,
            #only estimation
            'maxFeePerGas': _w3.toWei(100, 'gwei'),
            'maxPriorityFeePerGas': _w3.toWei(2, 'gwei'),
            'nonce': _w3.eth.get_transaction_count(signer_address)
        }
    )
    signedTx = w3.eth.account.sign_transaction(tx, private_key = private_key)
    w3.eth.send_raw_transaction(signedTx.rawTransaction)
    tx_hash = w3.toHex(w3.keccak(signedTx.rawTransaction))
    print(f"Swap txhash:{tx_hash}")

DAI_TOKEN_ADDRESS = "0x5592EC0cfb4dbc12D3aB100b257153436a1f0FEa"
USDC_TOKEN_ADDRESS = "0x4DBCdF9B62e891a7cec5A2568C3F4FAF9E8Abe2b"

approve(w3, USDC_TOKEN_ADDRESS, SUSHI_ROUTER_ADDRESS, 1000000000)
#wait for 10 secs in case of the nonce problem
time.sleep(10)

swap(w3, USDC_TOKEN_ADDRESS, DAI_TOKEN_ADDRESS, 1000000000, 10)