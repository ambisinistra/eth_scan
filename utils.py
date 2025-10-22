def validate_block_numbers(start_block, end_block):
    """
    Validates that block numbers are correct.
    
    Args:
        start_block: Starting block number
        end_block: Ending block number
        
    Raises:
        ValueError: If block numbers are invalid
        TypeError: If block numbers are not integers
    """
    # Check if values are integers
    if not isinstance(start_block, int) or not isinstance(end_block, int):
        raise TypeError(f"Block numbers must be integers, got start_block: {type(start_block).__name__}, end_block: {type(end_block).__name__}")
    
    # Check for negative values
    if start_block < 0:
        raise ValueError(f"Start block cannot be negative, got: {start_block}")
    
    if end_block < 0:
        raise ValueError(f"End block cannot be negative, got: {end_block}")
    
    # Check logical order
    if start_block > end_block:
        raise ValueError(f"Start block ({start_block}) must be less than or equal to end block ({end_block})")
    
    return True