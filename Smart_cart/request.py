import requests
PyTorch_REST_API_URL = 'http://7c605c99.ngrok.io/predict'

def predict_result(image_path):
    # Initialize image path
    image = open(image_path, 'rb').read()
    payload = {'image': image}

    # Submit the request.
    r = requests.post(PyTorch_REST_API_URL, files=payload).json()

    # Ensure the request was successful.
    if r['success']:
        # Loop over the predictions and display them.
        for (i, result) in enumerate(r['predictions']):
            print('{}. {}: {:.4f}'.format(i + 1, result['label'],
                                          result['probability']))
        print(result['label'])
    # Otherwise, the request failed.
    else:
        print('Request failed')

predict_result('image.jpg')
