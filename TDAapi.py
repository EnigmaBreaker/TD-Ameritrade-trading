from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
import urllib
import json

class TDAapis:
	def __init__(self, config_file):

		with open(config_file, 'r') as f:
			data = json.load(f)
			username = data['username']
			password = data['password']
			self.consumer_key = data['consumer_key']
			self.redirect_uri = data['redirect_uri']

		self.authorize(username, password)


	def get_built_url(self):
		url = "https://auth.tdameritrade.com/auth?"
		client_id = self.consumer_key + "@AMER.OAUTHAP"
		method = 'GET'
		payload = {'response_type' : 'code', "redirect_uri" : self.redirect_uri, "client_id" : client_id}

		built_url = requests.Request(method, url, params = payload).prepare()
		built_url = built_url.url

		return built_url

	def get_parse_url(self, built_url, username, password):
		chrome_options = Options()
		chrome_options.add_argument("--headless")

		browser = webdriver.Chrome(chrome_options = chrome_options)
		browser.get(built_url)

		browser.find_element_by_id('username').send_keys(username)
		browser.find_element_by_id('password').send_keys(password)

		browser.find_element_by_id('accept').click()
		time.sleep(1)
		browser.find_element_by_id('accept').click()
		time.sleep(1)
		new_url = browser.current_url
		browser.close()

		parse_url = urllib.parse.unquote(new_url.split('code=')[1])
		return parse_url

	def get_auth_response(self, parse_url):
		url = "https://api.tdameritrade.com/v1/oauth2/token"
		headers = {'Content-Type' : "application/x-www-form-urlencoded"}
		payload = {'grant_type' : 'authorization_code',
				   'access_type' : 'offline',
				   'code' : parse_url,
				   'client_id' : self.consumer_key,
				   'redirect_uri' : self.redirect_uri}

		response = requests.post(url, headers = headers, data = payload)

		return response.json()

	def authorize(self, username, password):
		built_url = self.get_built_url()
		parse_url = self.get_parse_url(built_url, username, password)
		auth_response = self.get_auth_response(parse_url)
		self.access_token = auth_response['access_token']
		self.refresh_token = auth_response['refresh_token']
		self.token_type = auth_response['token_type']
		


if __name__ == "__main__":
	api = TDAapis("config.json")
