# Virtual selection that is based on SearchX Backend

To run the evaluation script:

1. Set-up SearchX backend, instructions can be found here: https://github.com/searchx-framework/searchx-backend
2. Add a BingApi key to the .env file that you created in the previous step as follows:
   `BING_ACCESS_KEY=<your_api_Key>`. This is required because the vertical selection relies on the BingApi to retrieve
   results.
3. Startup the SearchX Backend, after the server is up you should see some messages about queries and verticals being
   imported, and their results retrieved
4. Install Python 3.7 locally using a virtual or a system environment.
5. Install the requirements listed in the file `requirements.txt` using the command `pip install -r requirements.txt`
6. Run the `main.py` located in the `python` directory using the command: `python python/main.py`. If using a virtual
   environment, make sure that you are running the script in it.
