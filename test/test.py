from flask import Flask
import requests
app = Flask(__name__)

#IP address and port number of front end server.
frontendIp = "172.16.233.136"
frontendPort = 5000
# Lookup (URL)
@app.route('/lookup/<int:itemNumber>', methods=['GET'])
def lookup(itemNumber):
    t = requests.get('http://{}:{}/lookup/{}'.format(frontendIp, frontendPort, itemNumber))
    return t.json()

# Search by topics  (URL) :
# 1- distributed_systems
# 2- graduate_school
@app.route('/search/<topic>', methods=['GET'])
def search(topic):
    r = requests.get('http://{}:{}/search/{}'.format(frontendIp, frontendPort, topic))
    return r.json()

# Buy (URL)
@app.route('/buy/<int:itemNumber>', methods=['GET'])
def buy(itemNumber):
    b = requests.get('http://{}:{}/buy/{}'.format(frontendIp, frontendPort, itemNumber))
    print("Bought book {}".format(itemNumber))
    return b.json()

@app.route('/')
def main():
    return "Test Server"

if __name__ == '__main__':
    app.run()
