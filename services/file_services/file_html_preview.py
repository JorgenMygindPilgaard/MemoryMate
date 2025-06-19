from configuration.paths import Paths
import os

current_image_html = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden; /* This prevents scroll bars */
        }

        img {
            max-width: 100%;
            height: 100vh; /* Set image height to 100% of viewport height */
            display: block;
            margin: 0 auto;
        }
    </style>
</head>
<body>
    <img src="current_image.jpg">
</body>
</html>
'''

if not os.path.isfile(Paths.get('current_image_html')):
    with open(Paths.get('current_image_html'), "w") as outfile:
        outfile.write(current_image_html)
