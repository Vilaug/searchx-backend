# Virtual selection that is based on SearchX Backend

How to setup corpus collection if not using the data collected:

1. Set-up SearchX backend, instructions can be found here: https://github.com/searchx-framework/searchx-backend
2. Add a BingApi key to the .env file that you created in the previous step as follows:
   `BING_ACCESS_KEY=<your_api_Key>`. This is required because the vertical selection relies on the BingApi to retrieve
   results.
3. Startup the SearchX Backend, after the server is up you should see some messages about queries and verticals being
   imported, and their results retrieved
  

How to import corpus collected data:

1. Download and extract the data, it can be found here: https://drive.google.com/uc?id=1utMND5IPfTkNGDlEyMjm-aZJ9rpQt4t1&export=download
2. Use the command `mongorestore --host <your_db_host> --port <your_db_port> --db aggregated-search dump/aggregated-search` to import the data into the database.

   
To run the evaluation script:
   
1. Install Python 3.7 locally using a virtual or a system environment.
2. Install the requirements listed in the file `requirements.txt` using the command `pip install -r requirements.txt`
3. Run the `main.py` located in the `python` directory using the command: `python python/main.py`. If using a virtual
   environment, make sure that you are running the script in it.
   

