import re
import socket
import dns.resolver
import dns.exception
import whois
import requests
import ssl
import urllib.parse
from datetime import datetime
import time
from urllib.parse import urlparse, parse_qs
import tldextract

class URLFeatureExtractor:
    def __init__(self):
        self.special_chars = ['.', '-', '_', '/', '?', '=', '@', '&', '!', ' ', '~', ',', '+', '*', '#', '$', '%']
        self.vowels = 'aeiouAEIOU'
        
    def count_char_in_string(self, string, char):
        """Count occurrences of a character in a string"""
        return string.count(char)
    
    def extract_url_components(self, url):
        """Extract and parse URL components"""
        parsed = urlparse(url)
        extracted = tldextract.extract(url)
        
        domain = parsed.netloc
        directory = parsed.path
        params = parsed.query
        file_part = parsed.path.split('/')[-1] if parsed.path else ''
        
        return {
            'full_url': url,
            'domain': domain,
            'directory': directory,
            'file': file_part,
            'params': params,
            'tld': extracted.suffix,
            'subdomain': extracted.subdomain,
            'registered_domain': extracted.top_domain_under_public_suffix
        }
    
    def extract_special_char_features(self, text, prefix):
        """Extract special character counts for a given text and prefix"""
        features = {}
        for char in self.special_chars:
            char_name = {
                '.': 'dot', '-': 'hyphen', '_': 'underline', '/': 'slash',
                '?': 'questionmark', '=': 'equal', '@': 'at', '&': 'and',
                '!': 'exclamation', ' ': 'space', '~': 'tilde', ',': 'comma',
                '+': 'plus', '*': 'asterisk', '#': 'hashtag', '$': 'dollar',
                '%': 'percent'
            }[char]
            features[f'qty_{char_name}_{prefix}'] = self.count_char_in_string(text, char)
        return features
    
    def get_domain_info(self, domain):
        """Get domain-related information"""
        try:
            # Check if domain is IP
            socket.inet_aton(domain)
            domain_in_ip = 1
        except socket.error:
            domain_in_ip = 0
        
        # Check server/client domain pattern
        server_client_pattern = re.compile(r'\b(server|client|srv|cli)\b', re.IGNORECASE)
        server_client_domain = 1 if server_client_pattern.search(domain) else 0
        
        return domain_in_ip, server_client_domain
    
    def get_dns_info(self, domain):
        """Get DNS-related information"""
        try:
            # Get IP addresses
            answers = dns.resolver.resolve(domain, 'A')
            qty_ip_resolved = len(answers)
        except:
            qty_ip_resolved = 0
        
        try:
            # Get nameservers
            answers = dns.resolver.resolve(domain, 'NS')
            qty_nameservers = len(answers)
        except:
            qty_nameservers = 0
        
        try:
            # Get MX servers
            answers = dns.resolver.resolve(domain, 'MX')
            qty_mx_servers = len(answers)
        except:
            qty_mx_servers = 0
        
        try:
            # Get TTL for hostname
            answers = dns.resolver.resolve(domain, 'A')
            ttl_hostname = answers.rrset.ttl if answers.rrset else 0
        except:
            ttl_hostname = 0
        
        try:
            # Check SPF record
            answers = dns.resolver.resolve(domain, 'TXT')
            domain_spf = 1 if any('spf' in str(record).lower() for record in answers) else 0
        except:
            domain_spf = 0
        
        return qty_ip_resolved, qty_nameservers, qty_mx_servers, ttl_hostname, domain_spf
    
    def get_whois_info(self, domain):
        """Get WHOIS information"""
        try:
            w = whois.whois(domain)
            
            creation_date = w.get('creation_date')
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            expiration_date = w.get('expiration_date')
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            
            if creation_date:
                time_domain_activation = int((datetime.now() - creation_date).days)
            else:
                time_domain_activation = -1
            
            if expiration_date:
                time_domain_expiration = int((expiration_date - datetime.now()).days)
            else:
                time_domain_expiration = -1
                
        except:
            time_domain_activation = -1
            time_domain_expiration = -1
        
        return time_domain_activation, time_domain_expiration
    
    def get_ssl_info(self, domain):
        """Check SSL certificate"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    tls_ssl_certificate = 1
        except:
            tls_ssl_certificate = 0
        
        return tls_ssl_certificate
    
    def get_http_info(self, url):
        """Get HTTP-related information"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10, allow_redirects=True)
            time_response = int((time.time() - start_time) * 1000)  # in milliseconds
            
            # Count redirects
            qty_redirects = len(response.history)
            
        except:
            time_response = -1
            qty_redirects = 0
        
        return time_response, qty_redirects
    
    def check_google_index(self, url, domain):
        """Check if URL/domain is indexed by Google (simplified)"""
        # This is a simplified version - actual implementation would use Google Search API
        # For now, returning default values
        url_google_index = 0  # Would need Google Search API
        domain_google_index = 0  # Would need Google Search API
        return url_google_index, domain_google_index
    
    def check_url_shortening(self, url):
        """Check if URL uses shortening service"""
        shortening_services = [
            'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'short.link',
            'ow.ly', 'buff.ly', 'is.gd', 'v.gd', 'tiny.cc'
        ]
        domain = urlparse(url).netloc.lower()
        return 1 if any(service in domain for service in shortening_services) else 0
    
    def get_asn_info(self, domain):
        """Get ASN information (simplified)"""
        # This would typically require an ASN lookup service
        # Returning default value for now
        return 0
    
    def extract_all_features(self, url, is_phishing=None):
        """Extract all features from a URL"""
        features = {}
        
        # Parse URL components
        components = self.extract_url_components(url)
        
        # URL-level features
        url_features = self.extract_special_char_features(url, 'url')
        features.update(url_features)
        
        # Count TLD occurrences in URL
        features['qty_tld_url'] = url.lower().count(f".{components['tld'].lower()}") if components['tld'] else 0
        features['length_url'] = len(url)
        
        # Domain-level features
        domain = components['domain']
        domain_features = self.extract_special_char_features(domain, 'domain')
        features.update(domain_features)
        
        features['qty_vowels_domain'] = sum(1 for char in domain if char in self.vowels)
        features['domain_length'] = len(domain)
        
        domain_in_ip, server_client_domain = self.get_domain_info(domain)
        features['domain_in_ip'] = domain_in_ip
        features['server_client_domain'] = server_client_domain
        
        # Directory-level features
        directory = components['directory']
        directory_features = self.extract_special_char_features(directory, 'directory')
        features.update(directory_features)
        features['directory_length'] = len(directory)
        
        # File-level features
        file_part = components['file']
        file_features = self.extract_special_char_features(file_part, 'file')
        features.update(file_features)
        features['file_length'] = len(file_part)
        
        # Parameters-level features
        params = components['params']
        params_features = self.extract_special_char_features(params, 'params')
        features.update(params_features)
        features['params_length'] = len(params)
        
        # Check if TLD is present in params
        features['tld_present_params'] = 1 if components['tld'] and components['tld'].lower() in params.lower() else 0
        
        # Count parameters
        parsed_params = parse_qs(params)
        features['qty_params'] = len(parsed_params)
        
        # Check for email in URL
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        features['email_in_url'] = 1 if email_pattern.search(url) else 0
        
        # Network and domain info (these might take time or fail)
        try:
            time_response, qty_redirects = self.get_http_info(url)
            features['time_response'] = time_response
            features['qty_redirects'] = qty_redirects
        except:
            features['time_response'] = -1
            features['qty_redirects'] = 0
        
        try:
            qty_ip_resolved, qty_nameservers, qty_mx_servers, ttl_hostname, domain_spf = self.get_dns_info(domain)
            features['qty_ip_resolved'] = qty_ip_resolved
            features['qty_nameservers'] = qty_nameservers
            features['qty_mx_servers'] = qty_mx_servers
            features['ttl_hostname'] = ttl_hostname
            features['domain_spf'] = domain_spf
        except:
            features['qty_ip_resolved'] = 0
            features['qty_nameservers'] = 0
            features['qty_mx_servers'] = 0
            features['ttl_hostname'] = 0
            features['domain_spf'] = 0
        
        try:
            time_domain_activation, time_domain_expiration = self.get_whois_info(components['registered_domain'])
            features['time_domain_activation'] = time_domain_activation
            features['time_domain_expiration'] = time_domain_expiration
        except:
            features['time_domain_activation'] = -1
            features['time_domain_expiration'] = -1
        
        try:
            features['tls_ssl_certificate'] = self.get_ssl_info(domain)
        except:
            features['tls_ssl_certificate'] = 0
        
        # ASN info
        features['asn_ip'] = self.get_asn_info(domain)
        
        # Google indexing (simplified)
        url_google_index, domain_google_index = self.check_google_index(url, domain)
        features['url_google_index'] = url_google_index
        features['domain_google_index'] = domain_google_index
        
        # URL shortening
        features['url_shortened'] = self.check_url_shortening(url)
        
        # Phishing label (if provided)
        if is_phishing is not None:
            features['phishing'] = is_phishing
        
        return features

# Usage example
if __name__ == "__main__":
    extractor = URLFeatureExtractor()
    
    # Example URL
    url = "https://www.example.com/path/to/file.html?param1=value1&param2=value2"
    
    features = extractor.extract_all_features(url)
    
    for feature, value in features.items():
        print(f"{feature}: {value}")