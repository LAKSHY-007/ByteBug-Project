pragma solidity ^0.8.0;

contract VotingSystem {
    struct Voter {
        bytes32 faceHash;
        bytes32 fingerprintHash;
        bool hasVoted;
    }

    mapping(address => Voter) public voters;
    mapping(string => uint256) public votes;
    address public admin;

    constructor() {
        admin = msg.sender;
    }

    function registerVoter(
        bytes32 _faceHash,
        bytes32 _fingerprintHash
    ) external {
        require(voters[msg.sender].faceHash == 0, "Already registered");
        voters[msg.sender] = Voter(_faceHash, _fingerprintHash, false);
    }

    function vote(string memory candidate) external {
        require(!voters[msg.sender].hasVoted, "Already voted");
        voters[msg.sender].hasVoted = true;
        votes[candidate]++;
    }

    function getResults(string memory candidate) public view returns (uint256) {
        return votes[candidate];
    }
}
