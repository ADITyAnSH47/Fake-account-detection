;; ITBP Fake Account Registry - Clarity Smart Contract
;; Smart contract for recording fake social media accounts on Stacks blockchain

;; Constants
(define-constant CONTRACT_OWNER tx-sender)
(define-constant ERR_UNAUTHORIZED (err u100))
(define-constant ERR_INVALID_RISK_SCORE (err u101))
(define-constant ERR_EMPTY_FIELDS (err u102))
(define-constant ERR_REPORT_EXISTS (err u103))
(define-constant ERR_REPORT_NOT_FOUND (err u104))
(define-constant ERR_ALREADY_VERIFIED (err u105))
(define-constant ERR_CANNOT_VERIFY_OWN (err u106))
(define-constant ERR_NOT_VERIFIED (err u107))

;; Data structures
(define-map fake-account-reports
  { report-id: (string-ascii 64) }
  {
    platform: (string-ascii 20),
    username: (string-ascii 50),
    risk-score: uint,
    evidence: (string-ascii 500),
    timestamp: uint,
    reporter: principal,
    is-verified: bool,
    is-action-taken: bool,
    block-height: uint
  }
)

(define-map reporting-agencies
  { agency-address: principal }
  {
    name: (string-ascii 50),
    is-authorized: bool,
    total-reports: uint,
    verified-reports: uint
  }
)

(define-map platform-counts
  { platform: (string-ascii 20) }
  { count: uint }
)

;; Data variables
(define-data-var report-counter uint u0)
(define-data-var contract-paused bool false)

;; Initialize contract with default agency
(map-set reporting-agencies
  { agency-address: CONTRACT_OWNER }
  {
    name: "ITBP",
    is-authorized: true,
    total-reports: u0,
    verified-reports: u0
  }
)

;; Helper functions
(define-private (is-authorized-agency (agency principal))
  (default-to false
    (get is-authorized
      (map-get? reporting-agencies { agency-address: agency }))))

(define-private (increment-platform-count (platform (string-ascii 20)))
  (let ((current-count (default-to u0 
    (get count (map-get? platform-counts { platform: platform })))))
    (map-set platform-counts
      { platform: platform }
      { count: (+ current-count u1) })))

(define-private (increment-agency-reports (agency principal))
  (match (map-get? reporting-agencies { agency-address: agency })
    current-agency
    (map-set reporting-agencies
      { agency-address: agency }
      (merge current-agency { total-reports: (+ (get total-reports current-agency) u1) }))
    false))

(define-private (increment-agency-verified (agency principal))
  (match (map-get? reporting-agencies { agency-address: agency })
    current-agency
    (map-set reporting-agencies
      { agency-address: agency }
      (merge current-agency { verified-reports: (+ (get verified-reports current-agency) u1) }))
    false))

;; Public functions

;; Register a new reporting agency (only owner)
(define-public (register-agency (agency-address principal) (agency-name (string-ascii 50)))
  (begin
    (asserts! (is-eq tx-sender CONTRACT_OWNER) ERR_UNAUTHORIZED)
    (map-set reporting-agencies
      { agency-address: agency-address }
      {
        name: agency-name,
        is-authorized: true,
        total-reports: u0,
        verified-reports: u0
      })
    (print { event: "agency-registered", agency: agency-address, name: agency-name })
    (ok true)))

;; Report a fake social media account
(define-public (report-fake-account 
    (platform (string-ascii 20))
    (username (string-ascii 50))
    (risk-score uint)
    (evidence (string-ascii 500))
    (report-id (string-ascii 64)))
  (begin
    (asserts! (not (var-get contract-paused)) ERR_UNAUTHORIZED)
    (asserts! (is-authorized-agency tx-sender) ERR_UNAUTHORIZED)
    (asserts! (<= risk-score u100) ERR_INVALID_RISK_SCORE)
    (asserts! (> (len platform) u0) ERR_EMPTY_FIELDS)
    (asserts! (> (len username) u0) ERR_EMPTY_FIELDS)
    (asserts! (is-none (map-get? fake-account-reports { report-id: report-id })) ERR_REPORT_EXISTS)
    
    (let ((is-high-risk (>= risk-score u70)))
      (map-set fake-account-reports
        { report-id: report-id }
        {
          platform: platform,
          username: username,
          risk-score: risk-score,
          evidence: evidence,
          timestamp: stacks-block-height,
          reporter: tx-sender,
          is-verified: is-high-risk,
          is-action-taken: false,
          block-height: stacks-block-height
        })
      
      ;; Update counters
      (increment-platform-count platform)
      (increment-agency-reports tx-sender)
      (var-set report-counter (+ (var-get report-counter) u1))
      
      ;; Auto-verify if high risk
      (if is-high-risk
        (increment-agency-verified tx-sender)
        true)
      
      (print {
        event: "fake-account-reported",
        platform: platform,
        username: username,
        risk-score: risk-score,
        reporter: tx-sender,
        report-id: report-id,
        auto-verified: is-high-risk
      })
      
      (ok (var-get report-counter)))))

;; Verify a report (by other authorized agencies)
(define-public (verify-report (report-id (string-ascii 64)))
  (begin
    (asserts! (is-authorized-agency tx-sender) ERR_UNAUTHORIZED)
    (match (map-get? fake-account-reports { report-id: report-id })
      report-data
      (begin
        (asserts! (not (get is-verified report-data)) ERR_ALREADY_VERIFIED)
        (asserts! (not (is-eq (get reporter report-data) tx-sender)) ERR_CANNOT_VERIFY_OWN)
        
        ;; Update report as verified
        (map-set fake-account-reports
          { report-id: report-id }
          (merge report-data { is-verified: true }))
        
        ;; Update reporter's verified count
        (increment-agency-verified (get reporter report-data))
        
        (print {
          event: "report-verified",
          report-id: report-id,
          verifier: tx-sender
        })
        
        (ok true))
      ERR_REPORT_NOT_FOUND)))

;; Mark action taken on a report
(define-public (mark-action-taken (report-id (string-ascii 64)) (action (string-ascii 200)))
  (begin
    (asserts! (is-authorized-agency tx-sender) ERR_UNAUTHORIZED)
    (match (map-get? fake-account-reports { report-id: report-id })
      report-data
      (begin
        (asserts! (get is-verified report-data) ERR_NOT_VERIFIED)
        
        ;; Update report with action taken
        (map-set fake-account-reports
          { report-id: report-id }
          (merge report-data { is-action-taken: true }))
        
        (print {
          event: "action-taken",
          report-id: report-id,
          action: action,
          agency: tx-sender
        })
        
        (ok true))
      ERR_REPORT_NOT_FOUND)))

;; Emergency pause contract (only owner)
(define-public (toggle-pause)
  (begin
    (asserts! (is-eq tx-sender CONTRACT_OWNER) ERR_UNAUTHORIZED)
    (var-set contract-paused (not (var-get contract-paused)))
    (print { event: "contract-paused", paused: (var-get contract-paused) })
    (ok (var-get contract-paused))))

;; Transfer ownership
(define-public (transfer-ownership (new-owner principal))
  (begin
    (asserts! (is-eq tx-sender CONTRACT_OWNER) ERR_UNAUTHORIZED)
    (print { event: "ownership-transferred", old-owner: CONTRACT_OWNER, new-owner: new-owner })
    (ok true))) ;; Note: In Clarity, contract ownership is immutable after deployment

;; Read-only functions

;; Get report details
(define-read-only (get-report (report-id (string-ascii 64)))
  (map-get? fake-account-reports { report-id: report-id }))

;; Get agency information
(define-read-only (get-agency-info (agency-address principal))
  (map-get? reporting-agencies { agency-address: agency-address }))

;; Get platform count
(define-read-only (get-platform-count (platform (string-ascii 20)))
  (default-to u0 (get count (map-get? platform-counts { platform: platform }))))

;; Get total reports
(define-read-only (get-total-reports)
  (var-get report-counter))

;; Check if contract is paused
(define-read-only (is-paused)
  (var-get contract-paused))

;; Get contract owner
(define-read-only (get-owner)
  CONTRACT_OWNER)

;; Check if address is authorized agency
(define-read-only (is-agency-authorized (agency principal))
  (is-authorized-agency agency))

;; Get basic statistics
(define-read-only (get-basic-statistics)
  {
    total-reports: (var-get report-counter),
    contract-paused: (var-get contract-paused),
    block-height: stacks-block-height
  })