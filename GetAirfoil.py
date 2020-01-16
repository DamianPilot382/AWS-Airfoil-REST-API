import json
import boto3
import tempfile
import re


def lambda_handler(event, context):

    # Check if a tag was provided
    try:
        tag = event['tag']
    except:
        # If not, return an error
        return {
            'statusCode' : 500,
            'info' : "Invalid request. Provide an airfoil"
        }


    try:

        # Get the coordinates from the S3 bucket
        s3 = boto3.client('s3')
        coords = s3.get_object(Bucket='pilotairfoils', Key=tag + '/points.dat')['Body'].read(amt=1024).decode()

        # Initialize an x list and a y list
        xPoints = []
        yPoints = []

        # Initialize the name.
        # Should be instantiated when extracting name from coordinates.
        name = None

        # Loop through every line of the points file
        for point in coords.splitlines():

            # If the name is not initialized,
            # Initialize it with the first line of the points file.
            if name is None:
                name = point
                continue

            # If the line is just empty space, ignore it.
            if re.search('^\s*$', point):
                continue

            # Separate the two points.
            xyPoints = re.findall('(-?[0-9]\.[0-9][0-9][0-9][0-9]*)', point)
            
            # If 2 points exist from the line, add them to their lists.
            if len(xyPoints) == 2:
                xPoints.append(float(xyPoints[0]))
                yPoints.append(float(xyPoints[1]))

        # Add all the points from the lists to one JSON object.        
        pointsJSON = {
            'x': [x for x in xPoints],
            'y': [y for y in yPoints],
        }

        # Get the GIF URL
        gifURL = "https://pilotairfoils.s3-us-west-1.amazonaws.com/" + tag + "/pic.gif"

        # Return the information with a successful completion code.
        return {
            'statusCode': 200,
            'name' : name,
            'coords' : pointsJSON,
            'photo' : gifURL
        }
    
    except Exception as e:
        # Getting the coordinates failed, so that means
        # That the provided tag was invalid.
        # Return an error
        return {
            'statusCode' : 500,
            'info' : "Airfoil not found."
        }