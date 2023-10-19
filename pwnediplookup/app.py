from flask import Flask, render_template, request, redirect, url_for, flash
import shodan
import requests

app = Flask(__name__)
app.secret_key = 'some_secret_key'

SHODAN_API_KEY = ''
SEARCH_TERM = "GoAhead-http country:NG"

def find_ip_on_shodan(ip_address):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        results = api.search(SEARCH_TERM)
        for result in results['matches']:
            if result['ip_str'] == ip_address:
                return result.get('org', 'Unknown organization')
        return None
    except shodan.APIError as e:
        return None

def attempt_https_connection(ip_address):
    url = f"https://{ip_address}"
    try:
        response = requests.get(url, verify=False, timeout=5)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        ip_address = request.form['ip_address']
        org_name = find_ip_on_shodan(ip_address)
        
        if org_name:
            message += f"Your home router with the IP address {ip_address} on {org_name} is publicly exposed and likely configured with a default password. \n"
            if attempt_https_connection(ip_address):
                message += f"visit https://{ip_address} to update your default router password immediately"
            else:
                message += f"Failed to make an HTTPS connection to {ip_address}."
        else:
            message = f"IP address {ip_address} not found on Shodan with {SEARCH_TERM}."
        
        flash(message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

