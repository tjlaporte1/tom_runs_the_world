# tom_runs_the_world
Analyze Tom's run data

Setting up permissions
Fill in the login.py with your client_id & client_secret values from the API settings on strava's site
use the code below to generate the authorization link to click on
f'http://www.strava.com/oauth/authorize?client_id={login.client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read_all,activity:read_all'

Once clicked and authorized the access, it will send you to a web page that says it can't connect to the server. In the url, copy the value after 'code='. 
Save the code in login.py as authorization_code. Then use the code below to build the url below. (a restart of the kernal may be needed to grab the new values in login.py)

requests.post(f'https://www.strava.com/oauth/token?client_id={login.client_id}&client_secret={login.client_secret}&code={login.authorization_token}&grant_type=').json()

In the output you will grab the 'refresh_token' and add this value to login.py. (restarting the kernal an additional time will be needed to get this new value from login.py)

Now that we have the correct refresh token for the proper permissions, we do not need to do this process again.