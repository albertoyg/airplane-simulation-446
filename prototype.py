import random
import matplotlib.pyplot as plt


def draw_plane(num_rows, num_cols, aisle_positions, seated_passengers, tickets):
    str_len = 7
    def seated_pass_str(passenger):
        if passenger == -1:
            return "".ljust(str_len)+"|"
        else:
            return str(passenger).ljust(str_len)+"|"
    def aisle_pass_str(passenger, ticket):
        if passenger == -1:
            return "".ljust(str_len)+"|"
        else:
            return f"{passenger}:{ticket['row']},{ticket['seat']}".ljust(str_len)+"|"
    # Print the row numbers
    print("_" * (num_rows * (str_len+1) + 19))
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
    for i in range(num_cols, num_cols*2):
        print(f"Column {i}: ".ljust(18), end="")
        for j in range(num_rows):
            print(f"{seated_pass_str(seated_passengers[j][i])}", end="")
        print()
    print("_" * (num_rows * (str_len+1) + 19))


def run_simulation(num_rows, num_cols, draw=False):
    # TODO: Take ordering in as a simulation parameter
    num_passengers = num_rows * num_cols * 2

    aisle_rows = [-1 for i in range(num_rows)]
    occupied_seats = [[-1, -1]*num_cols for i in range(num_rows)]
    passengers = [i for i in range(num_passengers)]
    tickets = [{'row':i,'seat':j} for i in range(num_rows) for j in range(num_cols*2)]
    random.shuffle(passengers)
    queue = passengers.copy()
    # Passenger i is assigned seat tickets[i]

    storing_baggage = [0 for i in range(num_rows)]
    num_seated = 0

    time_steps = 0
    # Loop until all passengers are seated
    while num_seated < num_passengers:
        # Loop through each row from the back to the front, moving passengers up the aisle if possible
        for aisle_row in range(len(aisle_rows)-1, -1, -1):
            # Skip empty aisle rows
            if aisle_rows[aisle_row] == -1:
                continue
            passenger = aisle_rows[aisle_row]
            ticket = tickets[passenger]
            # Check if passenger is in the row of their assigned seat
            if ticket['row'] == aisle_row:
                # Start storing baggage timer
                if storing_baggage[aisle_row] == 0:
                    storing_baggage[aisle_row] = 3
                else:
                    storing_baggage[aisle_row] -= 1
                    # If timer is up then seat the passenger
                    if storing_baggage[aisle_row] == 0:
                        occupied_seats[ticket['row']][ticket['seat']] = passenger
                        aisle_rows[aisle_row] = -1
                        num_seated += 1
            else:
                # Check if next aisle row is empty
                if aisle_rows[aisle_row + 1] == -1:
                    aisle_rows[aisle_row + 1] = passenger
                    aisle_rows[aisle_row] = -1

        if len(queue) > 0 and aisle_rows[0] == -1:
            passenger = queue.pop(0)
            aisle_rows[0] = passenger
        if draw == True:
            draw_plane(num_rows, num_cols, aisle_rows, occupied_seats, tickets)
        time_steps += 1
    return time_steps, passengers

times = []
best_time = 0
best_ordering = []
worst_time = 0
worst_ordering = []
for i in range(10000):
    time, ordering = run_simulation(15, 5, draw=False)
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

