nohup streamlit run main.py > logs.txt  2>&1 & echo $! > run.pid
nohup streamlit run test.py > logs_test.txt 2>&1 & echo $! > run_test.pid