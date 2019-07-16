# image-labeller

Very simple Flask app that collects image labels for [`auto-hasler`](https://github.com/annarailton/auto-hasler).  

## Setup Python environment

```bash
conda env create -f environment.yml
conda activate flask
```
To deactivate:
```bash
conda deactivate
```

## Start the site

Do
```bash
python3 image_labeller.py
```
then navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## TODO

* Add keyboard event mapping to voting page (less clicking!!)