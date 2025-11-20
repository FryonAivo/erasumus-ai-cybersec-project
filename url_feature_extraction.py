# extract_features.py
import tldextract
from urllib.parse import urlparse
import re
import math

def url_entropy(s: str) -> float:
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def extract_features(url: str) -> dict:
    parsed = urlparse(url)
    ext = tldextract.extract(url)

    domain = ext.registered_domain or ""
    sub = ext.subdomain or ""
    tld = ext.suffix or ""

    URLLength = len(url)
    DomainLength = len(domain)
    SubdomainCount = len(sub.split(".")) if sub else 0

    letters = sum(c.isalpha() for c in url)
    digits  = sum(c.isdigit() for c in url)
    specials = sum(not c.isalnum() for c in url)

    entropy = url_entropy(url)

    risky_tlds = {
        "tk","ml","ga","cf","gq","xyz","top","club","fun","rest","pw",
        "click","link","kim","work","live","fit","host","icu"
    }

    contains_unicode = any(ord(c) > 127 for c in url)

    return {
        "URLLength": URLLength,
        "DomainLength": DomainLength,
        "TLD": tld,
        "IsRiskyTLD": int(tld in risky_tlds),
        "IsDomainIP": int(bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain))),
        "SubdomainCount": SubdomainCount,

        "LetterCount": letters,
        "DigitCount": digits,
        "SpecialCharCount": specials,
        "LetterRatio": letters / max(1, URLLength),
        "DigitRatio": digits / max(1, URLLength),
        "SpecialCharRatio": specials / max(1, URLLength),

        "DotCount": url.count("."),
        "HyphenCount": url.count("-"),
        "AtCount": url.count("@"),
        "ParamCount": url.count("?"),
        "EqCount": url.count("="),
        "AmpCount": url.count("&"),

        "HasHTTPS": int(url.lower().startswith("https://")),
        "HasWWW": int("www." in url.lower()),
        "HasAtSymbol": int("@" in url),
        "ContainsUnicode": int(contains_unicode),
        "HasEncoded": int("%" in url),

        "PathDepth": len([p for p in parsed.path.split("/") if p]),
        "QueryLength": len(parsed.query),

        "Entropy": entropy,

        "ContainsLogin": int("login" in url.lower()),
        "ContainsVerify": int("verify" in url.lower()),
        "ContainsSecure": int("secure" in url.lower()),
        "ContainsUpdate": int("update" in url.lower()),
        "ContainsAccount": int("account" in url.lower()),
        "ContainsFree": int("free" in url.lower()),
        "ContainsPromo": int("promo" in url.lower()),
        "ContainsClick": int("click" in url.lower()),
        "ContainsWallet": int("wallet" in url.lower()),
    }
