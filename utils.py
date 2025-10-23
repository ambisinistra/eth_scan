def validate_block_numbers(start_block, end_block):
    """
    Validates that block numbers are correct.
    
    Args:
        start_block: Starting block number
        end_block: Ending block number
        
    Returns:
        tuple: (bool, str or None) - (is_valid, error_message)
               Returns (True, None) if validation passes
               Returns (False, error_message) if validation fails
    """
    # Check if values are integers
    if not isinstance(start_block, int) or not isinstance(end_block, int):
        return False, f"Block numbers must be integers, got start_block: {type(start_block).__name__}, end_block: {type(end_block).__name__}"
    
    # Check for negative values
    if start_block < 0:
        return False, f"Start block cannot be negative, got: {start_block}"
    
    if end_block < 0:
        return False, f"End block cannot be negative, got: {end_block}"
    
    # Check logical order
    if start_block > end_block:
        return False, f"Start block ({start_block}) must be less than or equal to end block ({end_block})"
    
    return True, None

def determine_transaction_type(tx):
    """
    Determine a transaction type based on its data
    
    Args:
        tx (dict): Dictionary with transaction data
        
    Returns:
        str: Transactions type ('simple_eth_transfer', 'token_transfer', 
             'smart_contract_call', 'unknown')
    """
    # check for a simple ETH transfer
    if (tx.get('input') == '0x' and
        tx.get('methodId') == '0x' and
        tx.get('functionName') == '' and
        int(tx.get('value', 0)) > 0):
        return 'simple_eth_transfer'
    
    # check for token transfers
    if (tx.get('methodId') in ['0xa9059cbb', '0x23b872dd'] and
        'transfer' in tx.get('functionName', '').lower()):
        return 'token_transfer'
    
    # check for a smart contract call
    if (tx.get('input') != '0x' and
        tx.get('methodId') != '0x' and
        tx.get('functionName') != ''):
        return 'smart_contract_call'
    
    # Если ни один из типов не подошёл
    return 'unknown'