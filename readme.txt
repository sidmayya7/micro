1. I have integrated with satviks host microservice. Our original application had direct access to the user view and admin view.
Now, using their microservice, I have put that behind a host login, where you enter the details of the current host before making the changes. It is pretty rudimentary but does work fairly well.
/hosts endpoint to put host details in postgresql database. /hosts/id to get current host details.

2. Loyalty points service. Integrated with smeras teams loyalty points service. It is called when doing payment. Also loyalty points displayed on homepage.
Endpoints used:
 Before Payment – Use Loyalty Points:
Endpoint: POST /wallet/use
Call this when the user wants to apply points for a discount.
This will deduct the points and return how much money it’s worth.

After Successful Payment – Add Points:
Endpoint: POST /wallet/add
Once a booking is confirmed, hit this endpoint to add new points to the user's wallet based on how much they spent.

 To Show Current Wallet Balance:
Endpoint: GET /wallet/{user_id}
You can use this to show users how many points they have during checkout.


Our workflow:
When the payment page loads, it shows the available loyalty points
User can enter points they want to use
When points are applied:
Points are deducted from the wallet
Discount is calculated (100 points = $10)
Final amount is updated
After successful payment:
Points are added based on the payment amount (10% of payment amount)
Booking is created with the discounted price

