# NLPA-polling
A pusher based polling app for web based judging of photographs. 

Setup the inital sqlite db with 'python dbsetup.py'

Create a directory called photos under static and place a sub folder 1 (and 2,3,4 if you want more projects). Add photos to be judged in here

Once the flask app is running, you can access the voting system by the initials and names setup in app.py (e.g. /home/V).
In our setup, organisers have half a vote each so you can either ignore the organiser votes (i.e. don't vote with them or delete them from code)

Clicking on the 1,2,3,4 under the photos scores the images with 4 points for a 1st, 3 for 2nd etc. 

If you're an organiser, you can switch folders by clicking on numbers, sort photos by score (only on your browser) or reset the scores. 

You can also toggle 'show' which shows the scores to your judges (once judging is over). 

The database persists scores as you move from folder to folder. 

You can hide images (useful for eliminating some images) by double clicking on the percentage score bar. 

Feel free to contact me with any questions
