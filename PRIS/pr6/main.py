import requests

def main():
    # headers = {"Accept":"text/html"}
    headers = {"Accept":"array"}
    r = requests.get('http://127.0.0.1:8888/?id=2&vx=15&va=15', headers=headers)
    # r = requests.get('https://google.com', headers=headers)
    print(r.text)

main()