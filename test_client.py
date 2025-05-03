import requests

# Define the API endpoint
url = 'http://localhost:5000/match'

# Paths to your test images
lost_image_path = 'test_images/lost_watch.jpg'
found_image_paths = [
    'test_images/found_watch1.jpg',
    'test_images/found_bag.jpg',
    'test_images/found_watch2.jpg'
]

# Prepare files for upload
files = {
    'lost_image': open(lost_image_path, 'rb'),
    'found_images': [open(path, 'rb') for path in found_image_paths]
}

# Use requests to post the form-data
response = requests.post(url, files={
    'lost_image': files['lost_image'],
    'found_images': tuple((os.path.basename(f.name), f) for f in files['found_images'])
})

# Print the response
print(response.status_code)
print(response.json())

# Close file handlers
files['lost_image'].close()
for f in files['found_images']:
    f.close()
