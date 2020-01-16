import boto3
import json
import re
import requests
import shutil
import urllib.request

def lambda_handler(event, context):

    # Open file online
    print("Running")
    try:
        fp = urllib.request.urlopen("https://m-selig.ae.illinois.edu/ads/coord_database.html")    
        rawData = fp.read().decode("utf8")
        fp.close()
    except Exception as e:
        print("Failed to get website from server.")
        return {
            'count': 0,
            'status': False
        }

    print("Fetched. Uploading now...")

    # Keep track of number of airfoils
    count = 0
    
    # Loop through all the lines
    for line in rawData.splitlines():

        # If this line is an airfoil
        airfoil = re.search("^\s*<a href=\"coord/", line)
        if airfoil:
            #Try to upload airfoil
            if parseAirfoil(line):
                # If airfoil uploaded successfully, add one to count
                count += 1

    # Return airfoil count and a successful status
    return {
        'count': count,
        'status': True
    }


def parseAirfoil(str):

    # Get the name, tag, coordinate name, and gif
    coord = re.search("^\s*<a href=\"coord/(.+?)\"", str).group(1)
    tag = re.search("(.+?)\.", coord).group(1)
    coord = "coord/" + coord
    gif = "afplots/" + tag + ".gif"
    name = re.search('^\s*<a href=\"coord/.+?</a>\s+?\\\\\s+?(.+?)\s+?\\\\\s+?', str).group(1)

    # Print the data
    # print("Coord: " + coord + ", Tag: " + tag + ", gif: " + gif)
    # print(name)

    # Upload the airfoil
    return uploadAirfoil(name, tag, coord, gif)


def uploadAirfoil(name, tag, coord, gif):

    # If the airfoil is not wanted, don't upload it.
    if checkBlacklist(name, tag, coord, gif):
        return False


    url = "https://m-selig.ae.illinois.edu/ads/"
    directory = "C:\\Users\\Pilot\\Desktop\\"

    # Connect to the bucket
    bucketName = 'pilotairfoils'
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketName)

    #Check if this file already exists on server
    try:
        s3.Object(bucketName, tag + '/points.dat').load()
        s3.Object(bucketName, tag + '/pic.gif').load()


        # If we get to this point, then the files didn't throw an error.
        # That means that they exist on the server
        print("Already in server: " + tag + ", " + name)
        return False
    except Exception as e:
        pass

    try:
        print("Uploading: " + tag + ", " + name)

        # Get the airfoil data points and GIF from the server
        urllib.request.urlretrieve(url + coord, directory + 'localdat.dat')
        urllib.request.urlretrieve(url + gif, directory + 'localgif.gif')

        # Upload the data points and the GIF
        s3.Object(bucketName, tag + '/points.dat').put(Body=open(directory + 'localdat.dat', 'rb'))
        s3.Object(bucketName, tag + '/pic.gif').put(Body=open(directory + 'localgif.gif', 'rb'))
        
    # If getting the airfoil data points or GIF fails,
    # That means that most likely, the airfoil is incorrect.
    # If so, skip it.
    except Exception as e:
        print("Skipping: " + name)
        return False

    # Airfoil was uploaded successfully
    return True
        
    


def checkBlacklist(name, tag, coord, gif):

    # If the airfoil name contains a link
    if "<a" in name:
        return True
    
    # If the airfoil is called something in particular

    if "Ashok Gopalarathnam SA702" in name:
        return True

    if "continued" in name:
        return True

    if "Martin Hepperle MH 33" in name:
        return True

    if "NACA 0010-34 a=0.8" in name:
        return True

    if "NACA 0012-64 a=0.8" in name:
        return True

    # Airfoil is not on blacklist.
    return False

print(lambda_handler(0, 0))