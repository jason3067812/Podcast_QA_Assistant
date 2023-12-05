# steps to add embedding
0. make sure embedding is modularized and takes the correct input
1. copy paste the embedding.py file into airflow_ci (maybe not necessary)
2. upload to airflow/dags/
3. update _embed_and_save in ci_transcribe.py
4. uncomment line 38 in ci_transcribe.py
5. run ci_dag.py in airflow once to populate EMBEDDED_DIR
6. run airflow db init after (should see move to cloud for embedded)
7. run and check