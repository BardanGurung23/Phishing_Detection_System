import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

class FeatureExtractor:
    def __init__(self, url):
        self.url = url
        if not re.match(r"^https?", url):
            self.url = "http://" + url
            
        try:
            self.parsed_url = urlparse(self.url)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}
            self.response = requests.get(self.url, timeout=4, headers=headers)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            self.response = None
            self.soup = None
        
        # Pre-calculate Hostname for Lexical Features
        self.hostname = self.parsed_url.netloc
    # LENGTH FEATURES ---
    def get_length_url(self): return len(self.url)
    def get_length_hostname(self): return len(self.hostname)

    # SYMBOL COUNTS---
    def get_nb_dots(self): return self.url.count('.')
    def get_nb_hyphens(self): return self.url.count('-')
    def get_nb_at(self): return self.url.count('@')
    def get_nb_qm(self): return self.url.count('?')
    def get_nb_and(self): return self.url.count('&')
    def get_nb_eq(self): return self.url.count('=')
    def get_nb_underscore(self): return self.url.count('_')
    def get_nb_tilde(self): return self.url.count('~')
    def get_nb_percent(self): return self.url.count('%')
    def get_nb_slash(self): return self.url.count('/')
    def get_nb_star(self): return self.url.count('*')
    def get_nb_colon(self): return self.url.count(':')
    def get_nb_comma(self): return self.url.count(',')
    def get_nb_semicolumn(self): return self.url.count(';')
    def get_nb_dollar(self): return self.url.count('$')
    def get_nb_space(self): return self.url.count(' ')
    def get_nb_www(self): return self.url.count('www')
    def get_nb_com(self): return self.url.count('.com')
    def get_nb_dslash(self): return self.url.count('//')

    # KEYWORD/TOKEN CHECKS 
    def get_http_in_path(self):
        return self.url.count('http')
    
    def get_https_token(self):
        # 0 if HTTPS, 1 if HTTP
        return 0 if self.parsed_url.scheme == 'https' else 1

    def get_ip(self):
        # Check if domain matches standard IPv4
        return 1 if re.search(r"^(\d{1,3}\.){3}\d{1,3}$", self.hostname) else 0

    def get_shortening_service(self):
        # List of top shorteners
        tiny_list = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                    r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                    r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                    r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                    r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                    r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                    r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                    r"tr\.im|link\.zip\.net"
        return 1 if re.search(tiny_list, self.url) else 0

    def get_prefix_suffix(self):
        return 1 if '-' in self.hostname else 0

    # RATIOS
    def get_ratio_digits_url(self):
        chars = len(self.url)
        digits = sum(c.isdigit() for c in self.url)
        return digits / chars if chars > 0 else 0

    def get_ratio_digits_host(self):
        chars = len(self.hostname)
        digits = sum(c.isdigit() for c in self.hostname)
        return digits / chars if chars > 0 else 0

    # CONTENT FEATURES 
    def get_iframe(self):
        if not self.soup: return 0
        return len(self.soup.find_all('iframe'))

    def get_nb_hyperlinks(self):
        if not self.soup: return 0
        return len(self.soup.find_all('a'))
    
    def get_empty_title(self):
        if not self.soup: return 1 
        if not self.soup.title or not self.soup.title.string:
            return 1
        return 0

    # MASTER EXTRACTOR 
    def extract_features(self):
        return [
            self.get_length_url(),      
            self.get_length_hostname(),
            self.get_ip(),             
            self.get_nb_dots(),         
            self.get_nb_hyphens(),      
            self.get_nb_at(),           
            self.get_nb_qm(),           
            self.get_nb_and(),          
            self.get_nb_eq(),           
            self.get_nb_underscore(),   
            self.get_nb_tilde(),       
            self.get_nb_percent(),      
            self.get_nb_slash(),       
            self.get_nb_star(),         
            self.get_nb_colon(),     
            self.get_nb_comma(),     
            self.get_nb_semicolumn(), 
            self.get_nb_dollar(),       
            self.get_nb_space(),
            self.get_nb_www(),          
            self.get_nb_com(),          
            self.get_nb_dslash(),      
            self.get_http_in_path(),    
            self.get_https_token(),     
            self.get_ratio_digits_url(),
            self.get_ratio_digits_host(),
            self.get_prefix_suffix(),   
            self.get_shortening_service(),
            self.get_iframe(),     
            self.get_nb_hyperlinks(),   
            self.get_empty_title()     
        ]