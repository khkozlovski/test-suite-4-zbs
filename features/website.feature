Feature: Z Biegiem Szyn website navigation
  As a visitor of https://zbs.net.pl
  I want to browse the magazine archive
  So that I can find and read past issues

  Scenario: User opens the website
    Given Website is online
    When User visits the Website
    Then The Main page is loaded correctly

  Scenario: User opens the Contact page
    Given The Main page is loaded correctly
    When User clicks/taps the "Kontakt" banner
    Then The User is navigated to the Contact page

  Scenario: User returns to the Main page from the Contact page
    Given The User is navigated to the Contact page
    When User clicks/taps the "Archiwum" banner
    Then The Main page is loaded correctly

  Scenario: User opens a newer issue by clicking on the cover
    Given The Main page is loaded correctly
    When User clicks/taps on an issue cover
    Then The pdf containing the issue is opened

  Scenario: User opens a newer issue by clicking on the summary
    Given The Main page is loaded correctly
    When User clicks/taps on an issue summary
    Then The pdf containing the issue is opened

  Scenario: User navigates to issues displayed without a summary
    Given The Main page is loaded correctly
    When User scrolls down
    Then User encounters issues displayed without a summary

  Scenario: User opens an issue displayed without a summary
    Given User encounters issues displayed without a summary
    When User clicks/taps on an issue cover
    Then The pdf containing the issue is opened

  Scenario: User navigates to issues displayed without a cover
    Given User encounters issues displayed without a summary
    When User scrolls down
    Then User encounters issues displayed without a cover

  Scenario: User opens an issue displayed without a cover
    Given User encounters issues displayed without a cover
    When User clicks/taps on an issue number
    Then The pdf containing the issue is opened

  Scenario: User returns to the Main page from a pdf containing an issue
    Given The pdf containing the issue is opened
    When User uses browser navigation to go back
    Then The Main page is loaded correctly
