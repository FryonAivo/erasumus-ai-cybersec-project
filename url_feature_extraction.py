import tldextract
from urllib.parse import urlparse
import re

def extract_features(url: str) -> dict:
    """
    FAST, heuristic-only extractor.
    Generates EXACTLY the features present in the real training dataset.
    No HTML parsing, no web requests.
    """

    parsed = urlparse(url)
    ext = tldextract.extract(url)

    domain = ext.registered_domain or ""
    subdomain = ext.subdomain or ""
    tld = ext.suffix or ""

    # Basic URL components
    URLLength = len(url)
    DomainLength = len(domain)
    TLDLength = len(tld)

    # Subdomain count
    NoOfSubDomain = len(subdomain.split(".")) if subdomain else 0

    # Detect IP domains
    is_ip = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain))

    # Obfuscation characters
    NoOfObfuscatedChar = sum(c in "%@=?" for c in url)
    HasObfuscation = int(NoOfObfuscatedChar > 0)
    ObfuscationRatio = NoOfObfuscatedChar / max(1, URLLength)

    # Letter/digit analysis
    letters = sum(c.isalpha() for c in url)
    digits  = sum(c.isdigit() for c in url)

    NoOfLettersInURL = letters
    NoOfDegitsInURL = digits

    LetterRatioInURL = letters / max(1, URLLength)
    DegitRatioInURL  = digits  / max(1, URLLength)

    # Special characters
    NoOfEqualsInURL = url.count("=")
    NoOfQMarkInURL  = url.count("?")
    NoOfAmpersandInURL = url.count("&")

    # Count ALL non-alphanumeric symbols
    NoOfOtherSpecialCharsInURL = sum(not c.isalnum() for c in url)

    SpacialCharRatioInURL = NoOfOtherSpecialCharsInURL / max(1, URLLength)

    # HTTPS flags
    IsHTTPS = int(url.startswith("https://"))

    # Text-based heuristics (no HTML)
    LineOfCode = 0
    LargestLineLength = 0
    HasTitle = 0
    Title = 0  # STRING FIELD, MUST BE DROPPED BEFORE MODEL
    DomainTitleMatchScore = 0.0
    URLTitleMatchScore = 0.0
    HasFavicon = 0
    Robots = 0
    IsResponsive = 0

    # Redirects
    NoOfURLRedirect = 0
    NoOfSelfRedirect = 0

    # Page description
    HasDescription = 0

    # Popups, iframes
    NoOfPopup = 0
    NoOfiFrame = 0

    # Forms
    HasExternalFormSubmit = 0

    # Social network indicator
    lower = url.lower()
    HasSocialNet = int(any(x in lower for x in ["facebook", "linkedin", "instagram", "twitter"]))

    HasSubmitButton = 0
    HasHiddenFields = 0
    HasPasswordField = 0

    # Finance keywords
    Bank = int(any(x in lower for x in ["bank", "secure", "account"]))
    Pay = int(any(x in lower for x in ["pay", "payment", "checkout"]))
    Crypto = int(any(x in lower for x in ["crypto", "btc", "eth", "wallet"]))

    # Copyright
    HasCopyrightInfo = 0

    # HTML element counts (heuristic = zero)
    NoOfImage = 0
    NoOfCSS = 0
    NoOfJS = 0

    # Link counts (no HTML parsing)
    NoOfSelfRef = 0
    NoOfEmptyRef = 0
    NoOfExternalRef = 0

    # Required ML dataset heuristic placeholders
    URLSimilarityIndex = 0.0
    CharContinuationRate = 0.0
    TLDLegitimateProb = 0.5
    URLCharProb = 0.5

    # Output dictionary (all columns except removed ones)
    return {
        "URLLength": URLLength,
        "DomainLength": DomainLength,
        "IsDomainIP": int(is_ip),
        "TLD": tld,
        "URLSimilarityIndex": URLSimilarityIndex,
        "CharContinuationRate": CharContinuationRate,
        "TLDLegitimateProb": TLDLegitimateProb,
        "URLCharProb": URLCharProb,
        "TLDLength": TLDLength,
        "NoOfSubDomain": NoOfSubDomain,
        "HasObfuscation": HasObfuscation,
        "NoOfObfuscatedChar": NoOfObfuscatedChar,
        "ObfuscationRatio": ObfuscationRatio,
        "NoOfLettersInURL": NoOfLettersInURL,
        "LetterRatioInURL": LetterRatioInURL,
        "NoOfDegitsInURL": NoOfDegitsInURL,
        "DegitRatioInURL": DegitRatioInURL,
        "NoOfEqualsInURL": NoOfEqualsInURL,
        "NoOfQMarkInURL": NoOfQMarkInURL,
        "NoOfAmpersandInURL": NoOfAmpersandInURL,
        "NoOfOtherSpecialCharsInURL": NoOfOtherSpecialCharsInURL,
        "SpacialCharRatioInURL": SpacialCharRatioInURL,
        "IsHTTPS": IsHTTPS,
        "LineOfCode": LineOfCode,
        "LargestLineLength": LargestLineLength,
        "HasTitle": HasTitle,
        # DO NOT RETURN THE STRING COLUMN Title (model does not accept it)
        "DomainTitleMatchScore": DomainTitleMatchScore,
        "URLTitleMatchScore": URLTitleMatchScore,
        "HasFavicon": HasFavicon,
        "Robots": Robots,
        "IsResponsive": IsResponsive,
        "NoOfURLRedirect": NoOfURLRedirect,
        "NoOfSelfRedirect": NoOfSelfRedirect,
        "HasDescription": HasDescription,
        "NoOfPopup": NoOfPopup,
        "NoOfiFrame": NoOfiFrame,
        "HasExternalFormSubmit": HasExternalFormSubmit,
        "HasSocialNet": HasSocialNet,
        "HasSubmitButton": HasSubmitButton,
        "HasHiddenFields": HasHiddenFields,
        "HasPasswordField": HasPasswordField,
        "Bank": Bank,
        "Pay": Pay,
        "Crypto": Crypto,
        "HasCopyrightInfo": HasCopyrightInfo,
        "NoOfImage": NoOfImage,
        "NoOfCSS": NoOfCSS,
        "NoOfJS": NoOfJS,
        "NoOfSelfRef": NoOfSelfRef,
        "NoOfEmptyRef": NoOfEmptyRef,
        "NoOfExternalRef": NoOfExternalRef,
    }
