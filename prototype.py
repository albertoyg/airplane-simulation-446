import random
import matplotlib.pyplot as plt


# Prints a visual representation of the plane
# TODO: Draw the plane with colors and shapes instead of ASCII
def draw_plane(num_rows, num_cols, aisle_positions, seated_passengers, tickets):
    str_len = 7

    def seated_pass_str(passenger):
        if passenger == -1:
            return "".ljust(str_len) + "|"
        else:
            return str(passenger).ljust(str_len) + "|"

    def aisle_pass_str(passenger, ticket):
        if passenger == -1:
            return "".ljust(str_len) + "|"
        else:
            return f"{passenger}:{ticket['row']},{ticket['seat']}".ljust(str_len) + "|"

    # Print the row numbers
    print("_" * (num_rows * (str_len + 1) + 19))
    print("Row number: ".ljust(18), end="")
    for i in range(0, num_rows):
        print(f"{str(i).ljust(str_len)}|", end="")
    print()
    # Print seats above the aisle
    for i in range(num_cols):
        print(f"Column {i}: ".ljust(18), end="")
        for j in range(num_rows):
            print(f"{seated_pass_str(seated_passengers[j][i])}", end="")
        print()
    # Print aisle positions
    print("Aisle positions: ".ljust(18), end="")
    for i in range(num_rows):
        passenger = aisle_positions[i]
        print(f"{aisle_pass_str(passenger, tickets[passenger])}", end="")
    print()
    # Print seats below the aisle
    for i in range(num_cols, num_cols * 2):
        print(f"Column {i}: ".ljust(18), end="")
        for j in range(num_rows):
            print(f"{seated_pass_str(seated_passengers[j][i])}", end="")
        print()
    print("_" * (num_rows * (str_len + 1) + 19))


def run_simulation(num_rows, num_cols, queue, draw=False):
    # TODO: Track simulation stats such as the following
    # Time each passenger spends standing on the plane
    # Time each passenger spends storing baggage
    # Time each passenger spends accessing their seat
    # Average number of passengers standing on the plane at any one time
    # Total time to seat all passengers

    num_passengers = len(queue)
    max_seat_num = num_rows * num_cols * 2
    assert max_seat_num >= max(queue), \
        f"Passenger has number {max(queue)} but only {max_seat_num} seats are available"

    # Tracks which aisle positions are occupied by which passengers
    aisle_rows = [-1 for i in range(num_rows)]
    """
    TODO: 
        -Currently hard-coded to take 3 time steps to store baggage
        -Should be change to exponential distribution
        -Only some passengers should store baggage, this could be a parameter of the simulation 
            eg. % of passengers storing baggage"""
    # Timers for which aisle positions are blocked by passengers storing baggage
    storing_baggage = [0 for i in range(num_rows)]
    """
    TODO:
        -Should take additional time to get in their seat, idependent of whether they have stored baggage or not
        -Should take longer depending on the number of seated passengers between the aisle and their seat
            eg. passenger has middle seat, but someone is already seated in the aisle seat
        -My intuition is this timer should be set according to an exponential distribution 
            with a mean of 1+2*(number of passengers seated between aisle and desired seat) time steps

        accessing_seat array is currently unused
    """
    # Timers for which aisle positions are blocked by passengers accessing their seat
    accessing_seat = [0 for i in range(num_rows)]

    # Tracks which seats are occupied by which passengers
    occupied_seats = [[-1, -1] * num_cols for i in range(num_rows)]
    # Passenger i is assigned seat tickets[i]
    tickets = [
        {'row': i, 'seat': j}
        for i in range(num_rows)
        for j in range(num_cols * 2)
    ]

    num_seated = 0
    time_steps = 0
    # Loop until all passengers are seated
    while num_seated < num_passengers:
        # Loop through each row from the back to the front, moving passengers up the aisle if possible
        for aisle_row in range(len(aisle_rows) - 1, -1, -1):
            # Skip empty aisle rows
            if aisle_rows[aisle_row] == -1:
                continue
            passenger = aisle_rows[aisle_row]
            ticket = tickets[passenger]
            # Check if passenger is in the row of their assigned seat
            if ticket['row'] == aisle_row:
                # TODO: Check if passenger has to store baggage
                # TODO: Set timer using exponential distribution
                # If storing baggage timer is zero, set it
                if storing_baggage[aisle_row] == 0:
                    storing_baggage[aisle_row] = 3
                else:
                    # Decrement timer
                    storing_baggage[aisle_row] -= 1
                    # If timer is up then seat the passenger
                    if storing_baggage[aisle_row] == 0:
                        # TODO: Start accessing seat timer once done storing baggage
                        occupied_seats[ticket['row']][ticket['seat']] = passenger
                        aisle_rows[aisle_row] = -1
                        num_seated += 1
            # Passenger is not in the row of their assigned seat
            else:
                # Check if next aisle row is empty
                if aisle_rows[aisle_row + 1] == -1:
                    # Move passenger up the aisle
                    aisle_rows[aisle_row + 1] = passenger
                    aisle_rows[aisle_row] = -1

        # If aisle has space, the next passenger in queue enters the plane
        if len(queue) > 0 and aisle_rows[0] == -1:
            passenger = queue.pop(0)
            aisle_rows[0] = passenger
        if draw:
            draw_plane(num_rows, num_cols, aisle_rows, occupied_seats, tickets)
        time_steps += 1
    return time_steps


plane_rows = 10
plane_cols = 1

times = []
best_time = 0
best_ordering = []
worst_time = 0
worst_ordering = []

"""
TODO: Instead of orderings being completely random, they should be generated using 
rules by which passengers could realistically be ordered. For example:

-Passengers are ordered by "zone", where the rows are broken up into zones and we 
    select which zones go first. Row & column orderings within zones would still be random.
-Passengers are ordered by seat column eg. windows seats first, then middle, then aisle. 
    Row orderings would still be random.

Ultimately we will be comparing the metrics of different orderings, so we want several methods
of generating orderings to test.
"""

for i in range(10000):
    ordering = [i for i in range(plane_rows * plane_cols * 2)]
    random.shuffle(ordering)
    time = run_simulation(plane_rows, plane_cols, ordering.copy(), draw=False)
    times.append(time)
    if time > worst_time:
        worst_time = time
        worst_ordering = ordering
    elif time < best_time or best_time == 0:
        best_time = time
        best_ordering = ordering

print(f"Average time steps: {sum(times) / len(times)}")
print(f"Best time steps: {best_time}")
print(f"Best ordering: {best_ordering}")
print(f"Worst time steps: {worst_time}")
print(f"Worst ordering: {worst_ordering}")
