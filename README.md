Project for the Course UMC 301 - Applied Data Science and Artificial Intelligence
To run the pipeline, you need to be the test user of the project. Please drop a message to us at teams so that we can add you as a test user.
To run this pipeline, first install the requirements by running the following command:
```bash
pip install -r requirements.txt
```

Then, run the following command to execute the pipeline:
```python   
python app.py
```

app.py is present in PythonScripts folder. The pipeline will run and generate the output in the ExtractedEmails folder. The output will be a csv file named 'emails_metadata.csv' which will contain the required information about the emails.

To run the UI, run the following command:
```python
streamlit run streamlitapp.py
```

streamlitapp.py is also present in PythonScripts folder. The UI will run on the localhost and will display the extracted emails and their metadata.

We also have React and Next JS Based UI, which can be started by commands available in firebase geniebox folder. After starting the development server, the csv file which is generated from above steps has to be uploaded in the UI to display the extracted emails and their metadata.

Contributions
- [Ayush Raina](Backend Code Development)
- [Savya Sachi](Prompt Engineering)
- [Anushka Dassi](React Based Frontend)
- [Sanidhya Kaushik](Data Collection and OCR)