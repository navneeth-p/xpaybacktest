import requests

url = "http://127.0.0.1:8000/register/"

data = {
  'full_name': 'test7',
  'email': 'test7@test.com',
  'password': '1234',
  'phone': '7777',
}

files = {'my_file': ('ICC-14.png', open('ICC-14.png', 'rb'))}


response = requests.post(url,data=data, files=files)
print(response)
print(response.json())
