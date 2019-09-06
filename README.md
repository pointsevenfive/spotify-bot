# Worldwide fm - spotify bot
bot to create playlist of tracks played on wwfm 

## dependencies:
creds.py has been omitted - require personal api keys & user logins
##### format of creds.py:

```python
twitter_id = "target_twitter_id" # Track retrieval
twitter_basic = "client_id:client_secret" # base64 

spotify_basic = "client_id:client_secret" # base64 
spotify_uname = "some_username_99"
spotify_passw = "some_passord_123"

callback_url = "https%3A%2F%2Fsome-escaped-url-here.com
```
### designed to run on Windows
other machines in the pipeline for development - dependency on js loading for spotify user login (current solution is using Selenium webdriver)
