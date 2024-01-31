# Keys
1. Which relations have natural keys?
Everything expect performance has natural keys. Even Ticket has a natural key even though it will be a random number.
For movies we could use a composite key using title and year, or the unique imdb-key.

2. Is there a risk that any of the natural keys will ever change?
A movie theater could consievably change name and a customer could possibly change their username.

3. Are there any weak entity sets?
Yes, perfomance is a weak entity set. It is defined by the foreign keys of its movie and theater

4. In which relations do you want to use an invented key. Why?
We'd like to use an invented key for the performance relation so that a ticket stays valid for a given perfomance even if the performance is changed in any way. It could perhaps be changed if the theater changes name.

# Relational model

theaters(_name_, capacity)
customers(_user_name_, full_name, password)
movies(_imdb_, title, year, runtime)
performances(_performance_id_, start_time, /theater_name/, /imdb/)
tickets(_ticket_id_, /user_name/, /performance_id/)

# Tracking performance number of seats
## Method one, Locking
We could add a *seats_left* attribute to performance that would initialize to the theater capacity and get decremented every ticket purchase. It would be easy to see how many seats are left, but we would need to lock performance every time we made a purchase in order to update the value.
## Method two, event sourcing
We know the theater capacity and every time we want to make a ticket purchase, sum the amount of tickets for that given performance and compare it to the capacity.