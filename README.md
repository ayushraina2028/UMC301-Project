Project for the Course UMC 301 - Applied Data Science and Artificial Intelligence

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
