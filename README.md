# airbnb_search_filter

Airbnb Searching System

1. The program is run under Python language, just simply run the python file in terminal and it will start.
2. You will see the main menu once you start runnig it, enter 1 for going into our "Search Listings" and "Book Listing" functions
	i. For vaild searhing, simply enter all dates during year 2016-2017 and some proper price range.
	ii. For invaild searching, system will ask for user input all the messages again.
	iii. Follow all the steps and you will successfully book the room (I didn't throw exception for input data type, assumed the user enters all valid input)
3. However, if you wanna test the trigger for second function "Write Review":
	i. You need to enter the arrival and leaving dates as 2019-11-30 to 2019-12-8
	ii. And only the listing_id has to be '6606'  since those are the only vaild dates and room in my database that around our recent dates.

After successfully book a room, we can go to "Write Review" function:

4. For writing the review of stayed rooms, just enter the name you firstly enter in the "Book Listing" function that dates around year 2016-2017
	i. if user enter a non-exist booked name, system will print error message and suggest user to create a new booking
	ii. and it will loop back to our main menu
5. For testing the second trigger, use our case from step 3 that the leaving date is 2019-12-8
(if  the date you are testing this system is < 12-8), then the system will print error message and ask user if want to quit system.

NOTE: Since the trigger has already been create when I first running this program, so I comment out the cur.execute(trigger).
	Which means two trigger are already in my database and no need to re-create again. 
	But I still left the content of two triggers in the code for easier cheking.
