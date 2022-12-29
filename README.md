# IdentityCleaner

## About
A web app that utilizes neural networks to perform state-of-the-art anonymization of human faces and vehicle license plates.

## Setup
All of the following commands assume that you are located in the project root directory.

### Running locally
1. Create a virtual Python environment using your preferred tool (venv, virtualenv, conda) to avoid conflicts:
```
python -m venv .venv
```

2. Activate the previously created environment:
    - bash (Linux): 
    ```
    source .venv/bin/activate
    ``` 
    - pwsh (Windows):
    ```
    .venv\Scripts\Activate.ps1
    ```

2. Install requirements from ```requirements.txt```:
```
python -m pip install -r requirements.txt
```

3. Download [the model files](https://drive.google.com/file/d/1gWCbS5V1ojQWLAVHSEHHVNj3ziiXmB_N/view?usp=share_link), extract the ```anonymizer``` folder and place it in ```models```.

4. Start the server by running ```main.py``` or issuing the following command:
```
uvicorn main:app --host 0.0.0.0 --port 9999
```
The frontend should be accessible from [http://localhost:9999/](http://localhost:9999/).

# Demo
![Demo](./frontend//assets/img/demo.gif)