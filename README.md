# Tom Runs The World
#### Strava Data Analysis

---

This Python project receives data from the Strava API and builds a web app using streamlit. The project is designed to explore Strava data in a way that is not done by Strava already on their website. It specifically focuses on gear, performance metrics, and activity timing. To run this analysis, one would need:

- A Strava account
- At least one activity recorded on Strava
- A persoanl Strava API Application (instructions below)

## Streamlit App

[View the final result](tom-runs-the-world.streamlit.app)

---

## Creation and Setup of Strava API Application

1. **Use the [Strava API Documentation](https://developers.strava.com) to create your application** on their website. Once created, locate the `Client ID` and `Client Secret` in the details section of your Application.

2. **Use `login_example.py`** to create your own `login.py` file. In this file paste `client_id` and `client_secret` values from your Application settings on Strava's site.

3. **Generate the authorization link** to click on. The purpose of this step is to ensure the scope of the access is `read_all` and `activity:read_all` at the end of the url:
   ```python
   f'http://www.strava.com/oauth/authorize?client_id={login.client_id}&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read_all,activity:read_all'
   ```

3. **Click on the generated link and authorize the app.** Once authorized, the page will display an error that it can't connect to the server. In the URL on the page, **copy the value after 'code='**.

4. **Save the copied code** in `login.py` as `authorization_token`.

5. **Use the code below** to build the URL and POST to it:
   ```python
   requests.post(f'https://www.strava.com/oauth/token?client_id={login.client_id}&client_secret={login.client_secret}&code={login.authorization_token}&grant_type=authorization_code').json()
   ```

6. In the output, **copy the `refresh_token`** and add this value to `login.py`. 

7. **Restart the kernel** to get the new values from `login.py`.

## Important Notes:
- Now that you have the correct `refresh_token` for the proper permissions, you **do not need to repeat this process again**.
- When using Streamlit, create a file in the project `.streamlit/secrets.toml` and input the values from `login.py`