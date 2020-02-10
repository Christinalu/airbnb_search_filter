#Christina Zhu

import pyodbc
import time
import pandas as pd

print('\n\t****** Welcome to our new Airbnb searching system!! ******')
flag = 1

while flag:
    #######################################################################
    # Main menu
    conn = pyodbc.connect('driver={SQL Server};Server=cypress.csil.sfu.ca;Trusted_Connection=yes;uid=uid;pwd=password')
    cur = conn.cursor()
    time.sleep(1)
    print('\n\t\t\t\tMain Menu\n')
    time.sleep(1)
    choice = int(input('Enter 1: to start a new booking\t\tEnter 2: to write a review for your previous bookings\n'))
    #######################################################################

    if choice == 1:
        # Search Listings
        shown_listing_id = []

        while True:
            # Input the minimum price and the maximum price
            minimumPrice = float(input("Please enter the minimum price you can accept: "))
            maximumPrice = float(input("Please enter the maximum price you can accept: "))

            # The number of bedrooms
            roomNumber = int(input("Please enter the number of bedrooms you are looking for: "))

            # Start date and End date
            start_date = str(input("Please enter your arrivial date in format YYYY-MM-DD: "))
            end_date = str(input("Please enter your leaving date in format YYYY-MM-DD: "))

            SQLcommand = ('''SELECT DISTINCT L.id, LEFT(description, 25) AS description, number_of_bedrooms, total_price
                            FROM Listings AS L JOIN Calendar AS C ON L.id = C.listing_id AND C.available = 1 AND L.number_of_bedrooms = %d,
                                (SELECT L2.id AS id_num, SUM(validNum) AS valid_num, SUM(totalPrice) AS total_price
                                FROM Listings AS L2 JOIN
                                    (SELECT L.id, COUNT(*) AS validNum, SUM(C.price) AS totalPrice
                                    FROM Listings AS L JOIN Calendar AS C ON L.id = C.listing_id
                                    WHERE C.available = 1 AND C.date BETWEEN '%s' AND '%s' AND C.price BETWEEN %d AND %d AND L.number_of_bedrooms = %d
                                    GROUP BY L.id, C.price) AS W ON W.id = L2.id
                                GROUP BY L2.id
                                HAVING SUM(validNum) = DATEDIFF(day, '%s','%s') + 1) AS S
                            WHERE L.id = id_num
                            AND C.date BETWEEN '%s' AND '%s' 
                            AND C.price BETWEEN %d AND %d'''
            % (roomNumber, start_date, end_date, minimumPrice, maximumPrice, roomNumber, start_date, end_date, start_date, end_date, minimumPrice, maximumPrice))

            cur.execute(SQLcommand)
            fetch = cur.fetchall()
            
            if fetch:
                for rows in fetch:
                    shown_listing_id.append(rows[0])
                ################ CREATE A TABLE ###################
                print()
                columnDes = cur.description
                columnNames = [columnDes[i][0] for i in range(len(columnDes))]
                df = pd.DataFrame([list(i) for i in fetch], columns=columnNames)
                print(df)
                break

            else:
                print("\n**********No match rooms found! Please re-enter your search criteria**********\n")


        # Book Listing
        cur.execute('SELECT COUNT(*) FROM Bookings')
        count = cur.fetchone()
        idNum = int(count[0])+1

        while True:
            listing_id = int(input("\nPlease enter the listing ID of room that you want to book: "))
            if listing_id not in shown_listing_id:
                print("\n********Listing ID Wrong. Please enter the ID shown in the List before********\n")
                continue
            else:
                break

        number_of_guests = int(input("Cool! How many of you are going to the trip? "))
        guest_name = str(input("Next, may we have your name in order to finish booking? Name: "))

        trigger = '''
                    CREATE TRIGGER updatedCalendar ON Bookings
                    AFTER INSERT AS BEGIN
                    UPDATE Calendar SET available = 0
                    WHERE listing_id IN (
                    SELECT B.listing_id FROM Bookings AS B
                    WHERE available = 1 AND listing_id = B.listing_id
                    AND date >= B.stay_from
                    AND date <= B.stay_to)
                    END '''

        # cur.execute(trigger)

        # print(idNum, listing_id, guest_name, start_date, end_date, number_of_guests)
        SQLcommand = ("INSERT INTO Bookings(id, listing_id, guest_name, stay_from, stay_to, number_of_guests) VALUES (?,?,?,?,?,?)")
        Values = [idNum, listing_id, guest_name, start_date, end_date, number_of_guests]

        cur.execute(SQLcommand, Values)

        print("\nCONGRATULATIONS! You have finish your booking! Enjoy your coming trip!\n")
        conn.commit()
        conn.close()

        time.sleep(2)
        
        finish = str(input("Now, if you wanna quit the system, plase enter Q. Otherwise, press any button and enter: "))
        if finish == 'Q':
            flag = 0

    else:
        # Write review
        trigger2 = '''  CREATE TRIGGER cannotReviewBeforeLeaving
                        ON Reviews AFTER INSERT
                        AS BEGIN
                        IF EXISTS (select *
                        From Bookings as B INNER JOIN inserted as i
                        on B.listing_id = i.listing_id where B.stay_to > GETDATE())
                        BEGIN
                            RAISERROR ('Can only review the listing after the stay', 10, 1)
                            ROLLBACK TRANSACTION
                        END
                        END '''

        guest_name = str(input("To write your review, please offer your name to the system: "))
        cur.execute("SELECT * FROM Bookings WHERE guest_name = '%s'" % guest_name)
        review_id = []

        fetch2 = cur.fetchall()         
        if fetch2:
            for rows in fetch2:
                review_id.append(rows[1])
            ################ CREATE A TABLE ###################
            print()
            columnDescrip = cur.description
            column_names = [columnDescrip[i][0] for i in range(len(columnDescrip))]
            df = pd.DataFrame([list(i) for i in fetch2], columns=column_names)
            print(df)
        else:
            print("\n**********You don't have any booking in the list yet, go back and book and a new room for ya?**********\n")
            continue
        
        while True:
            review_list_id = int(input("\nNow enter the listing id of shown rooms you want to review: "))
            if review_list_id not in review_id:
                print("\n********Listing ID Wrong. Please enter the ID shown in the List before********\n")
                continue
            else:
                break
   
        # cur.execute(trigger2)

        reviewText = str(input("Now you are available to write anything you want about your trip!\nMy review: "))

        cur.execute('SELECT COUNT(*) FROM Reviews')
        count = cur.fetchone()
        reviewNum = int(count[0])+1

        reviewCommand = ('INSERT INTO Reviews(id, listing_id, comments, guest_name) VALUES (?,?,?,?)')
        Values = [reviewNum, review_list_id, reviewText, guest_name]

        cur.execute(reviewCommand, Values)
        # print(cur.withhold)
        
        try:
            conn.commit()
            print("Your review has been update, Thank you!")
        except pyodbc.Error:
            print("\nSorry! You Can only review the listing after the stay.\n")
        
        conn.close()
        time.sleep(1)
        finish = str(input("\nNow, if you wanna quit the system, plase enter Q. Otherwise, press any button and enter: "))
        if finish == 'Q':
            flag = 0
        

print("\n\t****** Thank you for using the Airbnb searching system!! Bye ~ ******\n")
