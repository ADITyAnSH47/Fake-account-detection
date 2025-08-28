// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FakeAccountRegistry
 * @dev Smart contract for recording fake social media accounts on blockchain
 * @author ITBP Cybersecurity Team
 */
contract FakeAccountRegistry {
    
    // Structure to store fake account reports
    struct FakeAccountReport {
        string platform;           // Social media platform (Facebook, Instagram, etc.)
        string username;           // Username of the fake account
        uint256 riskScore;         // Risk score (0-100)
        string evidence;           // Evidence or reasoning
        uint256 timestamp;         // Block timestamp
        address reporter;          // Address of the reporting entity
        bool isVerified;           // Whether the report is verified
        bool isActionTaken;        // Whether action was taken by platform
        string reportId;           // Unique report identifier
    }
    
    // Structure for reporting agencies
    struct ReportingAgency {
        string name;               // Agency name (ITBP, CyberCrime, etc.)
        bool isAuthorized;         // Authorization status
        uint256 totalReports;      // Total reports submitted
        uint256 verifiedReports;   // Number of verified reports
    }
    
    // Storage
    FakeAccountReport[] public reports;
    mapping(address => ReportingAgency) public agencies;
    mapping(string => uint256) public platformCounts;
    mapping(string => bool) public reportExists;
    
    // Events
    event FakeAccountReported(
        uint256 indexed reportIndex,
        string platform,
        string username,
        uint256 riskScore,
        address indexed reporter
    );
    
    event ReportVerified(
        uint256 indexed reportIndex,
        address indexed verifier
    );
    
    event ActionTaken(
        uint256 indexed reportIndex,
        string action
    );
    
    event AgencyRegistered(
        address indexed agencyAddress,
        string agencyName
    );
    
    // Modifiers
    modifier onlyAuthorizedAgency() {
        require(agencies[msg.sender].isAuthorized, "Not an authorized agency");
        _;
    }
    
    modifier validReportIndex(uint256 _index) {
        require(_index < reports.length, "Invalid report index");
        _;
    }
    
    // Owner address (can be multi-sig for security)
    address public owner;
    
    constructor() {
        owner = msg.sender;
        
        // Register default agencies
        _registerAgency(msg.sender, "ITBP");
    }
    
    /**
     * @dev Register a new reporting agency
     * @param _agencyAddress Address of the agency
     * @param _agencyName Name of the agency
     */
    function registerAgency(address _agencyAddress, string memory _agencyName) 
        external 
    {
        require(msg.sender == owner, "Only owner can register agencies");
        _registerAgency(_agencyAddress, _agencyName);
    }
    
    function _registerAgency(address _agencyAddress, string memory _agencyName) 
        internal 
    {
        agencies[_agencyAddress] = ReportingAgency({
            name: _agencyName,
            isAuthorized: true,
            totalReports: 0,
            verifiedReports: 0
        });
        
        emit AgencyRegistered(_agencyAddress, _agencyName);
    }
    
    /**
     * @dev Report a fake social media account
     * @param _platform Social media platform
     * @param _username Username of the fake account
     * @param _riskScore Risk score (0-100)
     * @param _evidence Evidence or reasoning for the report
     * @param _reportId Unique report identifier
     */
    function reportFakeAccount(
        string memory _platform,
        string memory _username,
        uint256 _riskScore,
        string memory _evidence,
        string memory _reportId
    ) 
        external 
        onlyAuthorizedAgency 
        returns (uint256) 
    {
        require(_riskScore <= 100, "Risk score must be <= 100");
        require(bytes(_platform).length > 0, "Platform cannot be empty");
        require(bytes(_username).length > 0, "Username cannot be empty");
        require(!reportExists[_reportId], "Report ID already exists");
        
        // Create new report
        FakeAccountReport memory newReport = FakeAccountReport({
            platform: _platform,
            username: _username,
            riskScore: _riskScore,
            evidence: _evidence,
            timestamp: block.timestamp,
            reporter: msg.sender,
            isVerified: false,
            isActionTaken: false,
            reportId: _reportId
        });
        
        // Add to storage
        reports.push(newReport);
        uint256 reportIndex = reports.length - 1;
        
        // Update mappings
        reportExists[_reportId] = true;
        platformCounts[_platform]++;
        agencies[msg.sender].totalReports++;
        
        // Auto-verify if high risk score from authorized agency
        if (_riskScore >= 70) {
            reports[reportIndex].isVerified = true;
            agencies[msg.sender].verifiedReports++;
            emit ReportVerified(reportIndex, msg.sender);
        }
        
        emit FakeAccountReported(
            reportIndex,
            _platform,
            _username,
            _riskScore,
            msg.sender
        );
        
        return reportIndex;
    }
    
    /**
     * @dev Verify a report (can be done by other agencies)
     * @param _reportIndex Index of the report to verify
     */
    function verifyReport(uint256 _reportIndex) 
        external 
        onlyAuthorizedAgency 
        validReportIndex(_reportIndex) 
    {
        require(!reports[_reportIndex].isVerified, "Report already verified");
        require(reports[_reportIndex].reporter != msg.sender, "Cannot verify own report");
        
        reports[_reportIndex].isVerified = true;
        agencies[reports[_reportIndex].reporter].verifiedReports++;
        
        emit ReportVerified(_reportIndex, msg.sender);
    }
    
    /**
     * @dev Mark that action has been taken on a report
     * @param _reportIndex Index of the report
     * @param _action Description of action taken
     */
    function markActionTaken(uint256 _reportIndex, string memory _action) 
        external 
        onlyAuthorizedAgency 
        validReportIndex(_reportIndex) 
    {
        require(reports[_reportIndex].isVerified, "Report must be verified first");
        
        reports[_reportIndex].isActionTaken = true;
        
        emit ActionTaken(_reportIndex, _action);
    }
    
    /**
     * @dev Get report details by index
     * @param _reportIndex Index of the report
     */
    function getReport(uint256 _reportIndex) 
        external 
        view 
        validReportIndex(_reportIndex) 
        returns (
            string memory platform,
            string memory username,
            uint256 riskScore,
            string memory evidence,
            uint256 timestamp,
            address reporter,
            bool isVerified,
            bool isActionTaken,
            string memory reportId
        ) 
    {
        FakeAccountReport memory report = reports[_reportIndex];
        return (
            report.platform,
            report.username,
            report.riskScore,
            report.evidence,
            report.timestamp,
            report.reporter,
            report.isVerified,
            report.isActionTaken,
            report.reportId
        );
    }
    
    /**
     * @dev Get reports by platform
     * @param _platform Platform name
     * @param _offset Starting index
     * @param _limit Number of reports to return
     */
    function getReportsByPlatform(
        string memory _platform, 
        uint256 _offset, 
        uint256 _limit
    ) 
        external 
        view 
        returns (uint256[] memory) 
    {
        require(_limit > 0 && _limit <= 100, "Limit must be 1-100");
        
        uint256[] memory matchingReports = new uint256[](_limit);
        uint256 count = 0;
        uint256 found = 0;
        
        for (uint256 i = 0; i < reports.length && count < _limit; i++) {
            if (keccak256(bytes(reports[i].platform)) == keccak256(bytes(_platform))) {
                if (found >= _offset) {
                    matchingReports[count] = i;
                    count++;
                }
                found++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = matchingReports[i];
        }
        
        return result;
    }
    
    /**
     * @dev Get high-risk reports (risk score >= 70)
     * @param _limit Number of reports to return
     */
    function getHighRiskReports(uint256 _limit) 
        external 
        view 
        returns (uint256[] memory) 
    {
        require(_limit > 0 && _limit <= 100, "Limit must be 1-100");
        
        uint256[] memory highRiskReports = new uint256[](_limit);
        uint256 count = 0;
        
        // Start from most recent reports
        for (uint256 i = reports.length; i > 0 && count < _limit; i--) {
            uint256 index = i - 1;
            if (reports[index].riskScore >= 70) {
                highRiskReports[count] = index;
                count++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = highRiskReports[i];
        }
        
        return result;
    }
    
    /**
     * @dev Get statistics
     */
    function getStatistics() 
        external 
        view 
        returns (
            uint256 totalReports,
            uint256 verifiedReports,
            uint256 highRiskReports,
            uint256 actionTakenReports
        ) 
    {
        totalReports = reports.length;
        
        for (uint256 i = 0; i < reports.length; i++) {
            if (reports[i].isVerified) {
                verifiedReports++;
            }
            if (reports[i].riskScore >= 70) {
                highRiskReports++;
            }
            if (reports[i].isActionTaken) {
                actionTakenReports++;
            }
        }
    }
    
    /**
     * @dev Get agency information
     * @param _agencyAddress Address of the agency
     */
    function getAgencyInfo(address _agencyAddress) 
        external 
        view 
        returns (
            string memory name,
            bool isAuthorized,
            uint256 totalReports,
            uint256 verifiedReports
        ) 
    {
        ReportingAgency memory agency = agencies[_agencyAddress];
        return (
            agency.name,
            agency.isAuthorized,
            agency.totalReports,
            agency.verifiedReports
        );
    }
    
    /**
     * @dev Get total number of reports
     */
    function getTotalReports() external view returns (uint256) {
        return reports.length;
    }
    
    /**
     * @dev Get platform count
     * @param _platform Platform name
     */
    function getPlatformCount(string memory _platform) 
        external 
        view 
        returns (uint256) 
    {
        return platformCounts[_platform];
    }
    
    /**
     * @dev Emergency function to pause contract (only owner)
     */
    bool public paused = false;
    
    function togglePause() external {
        require(msg.sender == owner, "Only owner can pause/unpause");
        paused = !paused;
    }
    
    modifier whenNotPaused() {
        require(!paused, "Contract is paused");
        _;
    }
    
    /**
     * @dev Transfer ownership
     * @param _newOwner Address of the new owner
     */
    function transferOwnership(address _newOwner) external {
        require(msg.sender == owner, "Only owner can transfer ownership");
        require(_newOwner != address(0), "Invalid new owner address");
        owner = _newOwner;
    }
}