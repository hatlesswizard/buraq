import argparse
import random
import string
import urllib.parse
import requests
import re
import time
import concurrent.futures
import sys
from pyfiglet import figlet_format
from colorama import Fore, Style, init


def random_string(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def replace_params_keys_and_values(url, special, post_data=None):
    parsed_url = urllib.parse.urlparse(url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    post_params = urllib.parse.parse_qs(post_data) if isinstance(post_data, str) else {}

    new_urls = []
    random_params_list = []

    for key in query_params.keys():
        if special is not None:
            random_value = random_string() + special + random_string()
        else:
            random_value = random_string()

        random_params = {key: random_value}
        
        new_query_params = query_params.copy()
        new_query_params[key] = [random_value]
        
        new_query = urllib.parse.urlencode({k: v[0] for k, v in new_query_params.items()}, doseq=True)

        new_url = urllib.parse.urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment)
        )
        
        new_urls.append((new_url, post_data))
        random_params_list.append(random_params)

    for key in list(query_params.keys()):
        if special is not None:
            random_key = random_string() + special + random_string()
        else:
            random_key = random_string()

        random_params = {query_params[key][0]: random_key}
        
        new_query_params = query_params.copy()
        new_query_params[random_key] = new_query_params.pop(key)
        
        new_query = urllib.parse.urlencode({k: v[0] for k, v in new_query_params.items()}, doseq=True)

        new_url = urllib.parse.urlunparse(
            (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, new_query, parsed_url.fragment)
        )
        
        new_urls.append((new_url, post_data))
        random_params_list.append(random_params)

    if post_params:
        for key in post_params.keys():
            if special is not None:
                random_value = random_string() + special + random_string()
            else:
                random_value = random_string()

            random_params = {key: random_value}
            
            new_post_params = post_params.copy()
            new_post_params[key] = [random_value]
            new_post_data = urllib.parse.urlencode({k: v[0] for k, v in new_post_params.items()}, doseq=True)

            new_urls.append((url, new_post_data))
            random_params_list.append(random_params)
        
        for key in list(post_params.keys()):
            if special is not None:
                random_key = random_string() + special + random_string()
            else:
                random_key = random_string()

            random_params = {post_params[key][0]: random_key}
            
            new_post_params = post_params.copy()
            new_post_params[random_key] = new_post_params.pop(key)
            new_post_data = urllib.parse.urlencode({k: v[0] for k, v in new_post_params.items()}, doseq=True)

            new_urls.append((url, new_post_data))
            random_params_list.append(random_params)

    return new_urls, random_params_list


def monitor_log(log_file, random_strings, second, timeout):
    patterns = {key: re.compile(re.escape(value)) for key, value in random_strings.items()}
    
    start_time = time.time()
    with open(log_file, 'r') as f:
        while True:
            current_time = time.time()
            if current_time - start_time > timeout:
                break
            
            line = f.readline()
            if not line:
                time.sleep(0.5) 
                continue

            for key, pattern in patterns.items():
                if pattern.search(line):
                    location = find_string_location(line, random_strings[key], second)
                    if location is not None:
                        print(f"Found {key} ({random_strings[key]}) in query: {line.strip()} -> {location}")

def find_string_location(query, random_string, second):
    inside_single_quotes = False
    inside_double_quotes = False
    inside_backticks = False
    inside_round_brackets = False
    if second is not None:
        if random_string in query:
            red_text = "\033[91m"
            reset_text = "\033[0m"
            return f"{red_text}Vulnerable{reset_text}"
        else:
            return second
        
    for i, char in enumerate(query):
        if char == "'" and not inside_double_quotes and not inside_backticks:
            inside_single_quotes = not inside_single_quotes
        elif char == '"' and not inside_single_quotes and not inside_backticks:
            inside_double_quotes = not inside_double_quotes
        elif char == '`' and not inside_single_quotes and not inside_double_quotes:
            inside_backticks = not inside_backticks
        elif char == '(' and not inside_single_quotes and not inside_double_quotes and not inside_backticks:
            inside_round_brackets = True
        elif char == ')' and not inside_single_quotes and not inside_double_quotes and not inside_backticks:
            inside_round_brackets = False
        elif not inside_single_quotes and not inside_double_quotes and not inside_backticks and not inside_round_brackets:
            nada = True
        
        if query[i:i + len(random_string)] == random_string:
            if inside_single_quotes and inside_double_quotes:
                args = parse_arguments()
                method, url, headers, post_data = get_request_data(args)
                new_urls, random_params_list = replace_params_keys_and_values(url, "'", post_data)
                send_requests(method, url, headers, new_urls, random_params_list, "Inside double quotes enclosing single quotes")
            elif inside_single_quotes:
                args = parse_arguments()
                method, url, headers, post_data = get_request_data(args)
                new_urls, random_params_list = replace_params_keys_and_values(url, "'", post_data)
                send_requests(method, url, headers, new_urls, random_params_list, "Inside single quotes")
            elif inside_double_quotes:
                args = parse_arguments()
                method, url, headers, post_data = get_request_data(args)
                new_urls, random_params_list = replace_params_keys_and_values(url, '"', post_data)
                send_requests(method, url, headers, new_urls, random_params_list, "Inside double quotes")
            elif inside_backticks:
                args = parse_arguments()
                method, url, headers, post_data = get_request_data(args)
                new_urls, random_params_list = replace_params_keys_and_values(url, "`", post_data)
                send_requests(method, url, headers, new_urls, random_params_list, "Inside backticks")
            elif inside_round_brackets:
                args = parse_arguments()
                method, url, headers, post_data = get_request_data(args)
                new_urls, random_params_list = replace_params_keys_and_values(url, "()", post_data)
                send_requests(method, url, headers, new_urls, random_params_list, "Inside round brackets")
            elif nada is True:
                return "Not enclosed in quotes or backticks"

def parse_http_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()

    method, url, _ = lines[0].split(" ")
    headers = {}
    post_data = None
    body_started = False
    
    for line in lines[1:]:
        if line == "":
            body_started = True
            continue
        if body_started:
            post_data = line.strip()
        else:
            key, value = line.split(": ", 1)
            headers[key] = value

    if url.startswith("/"):
        if "Host" in headers:
            url = f"http://{headers['Host']}{url}"
        else:
            raise ValueError("Host header is missing in the request file")

    return method, url, headers, post_data

def parse_arguments():
    parser = argparse.ArgumentParser(description="Send request with random query parameters and monitor MySQL log")
    parser.add_argument('-u', '--url', type=str, help="URL to send request to")
    parser.add_argument('-f', '--file', type=str, help="File containing HTTP request data")
    return parser.parse_args()

def get_request_data(args):
    if args.file:
        return parse_http_file(args.file)
    elif args.url:
        return "GET", args.url, {}, None
    else:
        return None, None, None, None

import concurrent.futures

def send_requests(method, original_url, headers, new_urls, random_params_list, second):
    global log_file, timeout

    def handle_request(new_url, new_post_data, random_params):
        try:
            if original_url != new_url:
                print(f"Modified URL: {new_url.strip()}")
            elif new_post_data:
                print(f"Modified Data: {new_post_data}")
            print(f"Random strings for this request: {str(random_params).strip()}")
            response = send_request(method, new_url, headers, new_post_data)
            monitor_log(log_file, random_params, second, timeout)
        except KeyboardInterrupt:
            print("Stopped monitoring.")
        except Exception as e:
            print(f"Error during request handling: {e}")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(handle_request, new_url, new_post_data, random_params)
            for (new_url, new_post_data), random_params in zip(new_urls, random_params_list)
        ]
        concurrent.futures.wait(futures)

        
def send_request(method, url, headers, post_data):
    if method == "POST":
        return requests.post(url, data=post_data, headers=headers)
    else:
        return requests.get(url, headers=headers)

def main():
    init(autoreset=True)

    wing_art = """
⠀⠀⠀⠀⢀⣴⢿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⡾⠁⡞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⢺⠃⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢠⠏⢸⡄⠈⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢸⡀⢸⡄⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⡜⡇⠈⣿⡀⠀⠙⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⠀⢳⠄⠹⣿⡄⠀⠈⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣸⠆⢸⣧⡄⢸⣿⣶⠀⢠⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠷⡀⠹⣷⣄⣻⣿⡟⠺⣷⡀⠉⠓⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⢧⠀⣶⣄⡘⢿⣦⣽⣿⣄⠈⢱⡦⠀⠀⠉⠓⢤⡀⠀⠀⠀⠀⠀
⠘⣇⠈⠻⣷⡜⢻⣧⠉⠻⣄⠈⢻⣶⣴⠶⡄⠀⠙⡆⠀⠀⠀⠀
⠀⢻⠉⣄⠈⢿⣿⣿⣷⠀⠀⣶⣤⣀⣷⣀⠀⠀⠀⣸⠀⠀⠀⠀
⠀⠀⢧⡈⢿⣥⣍⣿⠉⠉⠃⢶⣦⣿⠀⠀⠀⠀⡚⠋⠀⠀⠀⠀
⠀⠀⠈⠳⣤⣈⠛⠻⢷⣦⣤⡄⣶⣾⣿⠃⠀⠀⠛⢦⡄⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠒⠒⣾⠋⠁⠀⣈⣽⣿⣷⡆⠀⠀⠀⠘⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠹⠦⢴⠋⠁⠀⠹⣿⣿⣿⠀⠀⠀⠙⣄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢤⠴⠋⠀⡀⠛⠿⠟⡇⠠⠤⠤⠷
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠤⠴⣇⣠⣏⣰⠁⠀⠀⠀⠀
    """
    wing_lines = wing_art.splitlines()
    banner_text = figlet_format("Buraq SQLi Detector", font="slant")
    banner_lines = banner_text.splitlines()

    max_lines = max(len(wing_lines), len(banner_lines))
    for i in range(max_lines):
        wing_line = wing_lines[i] if i < len(wing_lines) else ""
        banner_line = banner_lines[i] if i < len(banner_lines) else ""
        sys.stdout.write(f"{Fore.GREEN}{wing_line:<30}{banner_line}{Style.RESET_ALL}\n")
        sys.stdout.flush()
        time.sleep(0.05)

    args = parse_arguments()
    global log_file, timeout
    log_file = '/var/log/mysql/mysql.log'
    timeout = 5
    method, url, headers, post_data = get_request_data(args)
    if not url:
        print("You must provide either a URL or a file containing the HTTP request data.")
        return

    new_urls, random_params_list = replace_params_keys_and_values(url, None, post_data)
    print(f"Original URL: {url}")
    send_requests(method, url, headers, new_urls, random_params_list, None)

if __name__ == '__main__':
    main()
