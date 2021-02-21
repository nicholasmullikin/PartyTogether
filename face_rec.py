#! /usr/bin/python

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
from time import sleep
import random
import json

def main():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="54735820284c4380ac403bb4ae089d9c",
                                                       client_secret="3ccbf7901668460e80a03015d5f12da0",
                                                       redirect_uri="http://localhost:1337/callback",
                                                       scope="user-read-recently-played user-read-playback-state "
                                                             "user-top-read playlist-modify-public "
                                                             "user-modify-playback-state playlist-modify-private "
                                                             "user-follow-modify user-read-currently-playing "
                                                             "user-follow-read user-library-modify "
                                                             "user-read-playback-position playlist-read-private "
                                                             "user-read-email user-read-private user-library-read "
                                                             "playlist-read-collaborative",
                                                       open_browser=False))
    # Shows playing devices
    res = sp.devices()

    # Gets the device with the name below
    device_id = ""
    for d in res['devices']:
        if d['name'] == 'Web Player (Chrome)':
            device_id = d['id']

    # Name -> Spotify mapping
    user_list = {"nick": '5sq0472fjzjxdx70quovzgcy7', "yale": 'yaleduffy'}

    #Initialize 'currentname' to trigger only when a new person is identified.
    currentname = "unknown"
    #Determine faces from encodings.pickle file model created from train_model.py
    encodingsP = "encodings.pickle"
    #use this xml file
    #https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
    cascade = "haarcascade_frontalface_default.xml"

    # load the known faces and embeddings along with OpenCV's Haar
    # cascade for face detection
    print("[INFO] loading encodings + face detector…")
    data = pickle.loads(open(encodingsP, "rb").read())
    detector = cv2.CascadeClassifier(cascade)

    # initialize the video stream and allow the camera sensor to warm up
    print("[INFO] starting video stream…")
    vs = VideoStream(src=0).start()
    #vs = VideoStream(usePiCamera=True).start()

    # start the FPS counter
    fps = FPS().start()
    print("[INFO] starting")
    # loop over frames from the video file stream
    while True:
        #with picamera.PiCamera() as camera:
        #    camera.resolution = (1280,720)
        #    camera.capture(f"faces/new_img.jpg")
        #    time.sleep(5.0)
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speedup processing)
        frame = vs.read()
        #frame = face_recognition.load_image_file(f"faces/new_img.jpg")
        frame = imutils.resize(frame, width=500)

        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1,
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"],
                encoding)
            name = "Unknown" #if face is not recognized, then print Unknown

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                print("Matched")
                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

                #If someone in your dataset is identified, print their name on the screen
                if currentname != name:
                    currentname = name
                    print(currentname)
                    #output to text file
                    outfile = open('name.txt','w')
                    outfile.write(currentname)
                    outfile.close()

            # update the list of names
            names.append(name)

            # users_in_scene = ["nick"]
            songs = []
            for i in range(0, len(names)):
                if names[i] != 'Unknown':
                    songs += get_songs(sp, user_list[names[i]])

            if len(songs) > 0:
                random.shuffle(songs)
                print(songs)
                sp.start_playback(uris=songs, device_id=device_id)




        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            # draw the predicted face name on the image – color is in BGR
            cv2.rectangle(frame, (left, top), (right, bottom),
                (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                .8, (255, 0, 0), 2)

        # display the image to our screen
        cv2.imshow("Facial Recognition is Running", frame)
        key = cv2.waitKey(1) & 0xFF

        # quit when 'q' key is pressed
        if key == ord("q"):
            break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    #fps.stop()
    #print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    #print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

def get_songs(sp, username):
    playlists = sp.user_playlists(username)
    playlist_id = get_playlists(sp, playlists, "Party")
    print(playlist_id)
    results = sp.playlist_items(playlist_id, additional_types=['track'])
    tracks = []
    for x in range(0, len(results['items'])):
        tracks += [results['items'][x]['track']['uri']]
    return tracks


def get_playlists(sp, playlists, playlist_name):
    current_playlist_id = ""
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print(
                "%4d %s %s" %
                (i +
                 1 +
                 playlists['offset'],
                 playlist['uri'],
                 playlist['name']))
            if playlist['name'] == playlist_name:
                current_playlist_id = playlist['uri']
        # gets next page
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return current_playlist_id



if __name__ == "__main__":
    main()
