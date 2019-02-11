# Worldwide fm - spotify bot
bot to create playlist of tracks played on wwfm 

## dependencies:
creds.py has been omitted - require personal api keys & user logins
##### format of creds.py:

```python
twitter_basic = "xyz" # base64 encoded 'client_id:client_secret'
spotify_basic = "jkl" # base64 encoded 'client_id:client_secret'
spotify_client_id = "plaintext_client_id"
spotify_uname = "some_username_99"
spotify_passw = "some_passord_123"
```
### designed to run on Windows
other machines in the pipeline for development - dependency on js loading for spotify user login (current solution is using Selenium webdriver, any help/ideas to remove dependency on webdriver much appreciated)
