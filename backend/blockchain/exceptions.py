class BlockchainError(Exception):
    pass
class EconomyError(BlockchainError): 
    pass
class SecurityError(BlockchainError): 
    pass