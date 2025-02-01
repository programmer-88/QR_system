QR code generating sysgem
Generates QR code after prompting a upi code and saves it and print it
Can verify active QR codes by scanning 
Can delete the QR code to past records and store their upi code,QR code, date and time generated and date and time removed from active records
When deleting a records from active to archived the user should be prompted to scan the qr code, the program will give the upi code which can be copied and used to verify the patient has gone past all steps
when it is verified the program will remove the record from active to inactive section keep upi,QR code, time and date generated and time and date deleted

The program should be modified to prompt the user to log in via a username and password to interact with the program

when generating a QR code the upi, QR code,upi,date and time upon creating should include the user who is signed in

The same should happen when deleting a user from active 
The data should be moved to inactive with the username of user who generated the qr code, upi, date and time generated, date and time removed form active and user who removed it from active


Create ssl certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

install opencv and pyzbar pip modules

ok