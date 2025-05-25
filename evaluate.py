import requests


def evaluate(filename):
    filepath = f"output_files/{filename}.out"

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return

    url = f"https://xdcu75czxyvf6wmjtgfqh2d72y0gejag.lambda-url.eu-central-1.on.aws/?filename={filename}"
    response = requests.post(
        url,
        headers={"Content-Type": "text/plain"},
        data=content
    )

    print(response.text)

if __name__ == "__main__":
    evaluate('02')
