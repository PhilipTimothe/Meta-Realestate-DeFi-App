// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.5.0;
import "node_modules/@openzeppelin/contracts/token/ERC721/ERC721Full.sol";

contract RealEstateToken is ERC721Full {
    address public admin;
    enum  TokenStatus { Pending, Approved, Rejected }
    mapping(uint256 => TokenStatus) public tokenStatuses;
    mapping(uint256 => bool) public tokensForSale;
    mapping(uint256 => uint256) public tokenPrice;
    
    event pendingTokens(uint256[] tokens);
    event approvedTokens(uint256[] resultTokens, uint256[] resultPrices);
    event NFTPurchased(address indexed buyer, uint256 tokenId, uint256 value);
    
    constructor() public ERC721Full("RealEstateToken", "RET") {
        admin = msg.sender;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only the admin can call this function");
        _;
    }
    
    function setTokenStatus(uint256 tokenId, TokenStatus status) external onlyAdmin {
        require(tokenId < totalSupply(), "Invalid token ID");
        tokenStatuses[tokenId] = status;
    }
    
    function registerHouse(string memory tokenURI) public returns (uint256) {
        uint256 tokenId = totalSupply();
        _mint(msg.sender, tokenId);
        tokenStatuses[tokenId] == TokenStatus.Pending;
        _setTokenURI(tokenId, tokenURI);
        return tokenId;
    }
    
    function addTokenForSale(uint256 tokenId, uint256 price) external {
        require(ownerOf(tokenId) == msg.sender, "You don't own this token");
        require(tokenStatuses[tokenId] == TokenStatus.Approved, "Token must be approved for sale");
        tokensForSale[tokenId] = true;
        tokenPrice[tokenId] = price;
    }
    
    function getTokensForSale() external returns (uint256[] memory, uint256[] memory) {
        uint256 totalTokens = totalSupply();
        uint256[] memory tokensForSaleList = new uint256[](totalTokens);
        uint256[] memory pricesForSaleList = new uint256[](totalTokens);
        uint256 count = 0;
        for (uint256 tokenId = 0; tokenId < totalTokens; tokenId++) {
            if (tokensForSale[tokenId]) {
                tokensForSaleList[count] = tokenId;
                pricesForSaleList[count] = tokenPrice[tokenId];
                count++;
            }
        }
    
        uint256[] memory resultTokens = new uint256[](count);
        uint256[] memory resultPrices = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            resultTokens[i] = tokensForSaleList[i];
            resultPrices[i] = pricesForSaleList[i];
        }
            emit approvedTokens(resultTokens, resultPrices);
            return (resultTokens, resultPrices);
        }
 
    function getPendingTokens() external onlyAdmin returns (uint256[] memory) {
        uint256 totalTokens = totalSupply();
        uint256[] memory pendingTokenIds = new uint256[](totalTokens);
        uint256 count = 0;
        for (uint256 tokenId = 0; tokenId < totalTokens; tokenId++) {
            if (tokenStatuses[tokenId] == TokenStatus.Pending) {
                pendingTokenIds[count] = tokenId;
                count++;
            }
        }
        uint256[] memory resultIds = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            resultIds[i] = pendingTokenIds[i];
        }
        emit pendingTokens(resultIds);
        return (resultIds);
    }

    function getUserTokens(address user) external view returns (uint256[] memory) {
            uint256 userBalance = balanceOf(user);
            uint256[] memory userTokens = new uint256[](userBalance);
            uint256 count = 0;
            for (uint256 tokenId = 0; tokenId < totalSupply(); tokenId++) {
                if (ownerOf(tokenId) == user) {
                    userTokens[count] = tokenId;
                    count++;
                }
            }
        return userTokens;
    }

    function _isApprovedOwner(address owner, uint256 tokenId) internal view returns (bool) {
        return ownerOf(tokenId) == owner;
    }

    function getApprovedTokensForAddress(address user) external view returns (uint256[] memory) {
        uint256 totalTokens = totalSupply();
        uint256[] memory approvedTokenIds = new uint256[](totalTokens);
        uint256 count = 0;
        for (uint256 tokenId = 0; tokenId < totalTokens; tokenId++) {
            if (tokenStatuses[tokenId] == TokenStatus.Approved && ownerOf(tokenId) == user) {
                approvedTokenIds[count] = tokenId;
                count++;
            }
        }
        uint256[] memory resultIds = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            resultIds[i] = approvedTokenIds[i];
        }
        return resultIds;
    }

    function purchaseNFT(uint256 tokenId) public payable {
        require(tokensForSale[tokenId], "Token is not listed for sale");
        require(tokenPrice[tokenId] > 0, "Token price must be greater than zero");
        require(msg.value > tokenPrice[tokenId], "Insufficient Ether sent");
        
        // Calculate the extra amount sent
        // uint256 extraAmount = msg.value - tokenPrice[tokenId];
        
        // Get the current owner of the NFT
        address payable seller = address(uint160(ownerOf(tokenId)));
        
        // Transfer the NFT from the seller to the buyer using safeTransferFrom
        super.safeTransferFrom(seller, msg.sender, tokenId);
        // Transfer the listed price to the seller
        bool sellerTransferSuccess = seller.send(msg.value);
        require(sellerTransferSuccess, "Transfer to seller failed");
        
        
        // Refund the extra amount to the buyer
        // if (extraAmount > 0) {
        //     bool refundSuccess = msg.sender.send(extraAmount);
        //     require(refundSuccess, "Refund to buyer failed");
        // }
        
        // Mark the token as sold and remove it from the sale list
        tokensForSale[tokenId] = false;
        tokenPrice[tokenId] = 0;
        
        // Emit an event to log the purchase
        emit NFTPurchased(msg.sender, tokenId, msg.value);
    }
}