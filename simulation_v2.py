import random
import statistics as stat
from prettytable import PrettyTable


def getAvg_p_in_aisle(p_in_aisle_for_this_long):
    total_people = 0
    total_time = 0

    for num_people, elapsed_time in p_in_aisle_for_this_long:
        total_people += num_people * elapsed_time
        total_time += elapsed_time

    return total_people / total_time


def create_orderings(plane_rows, plane_cols):
    all_orders = []
    # create back to front ordering
    back_to_front = [i for i in range(plane_rows * plane_cols * 2)]
    back_to_front = sorted(back_to_front, reverse=True)

    # create front to back ordering
    front_to_back = [i for i in range(plane_rows * plane_cols * 2)]

    # create random order
    random_order = list(range(plane_rows * plane_cols * 2))
    random.shuffle(random_order)

    # create window seats first ordering
    window_seats_first = []
    for row in range(plane_rows):
        window_seats_first.append(row * (plane_cols * 2))
        window_seats_first.append(row * (plane_cols * 2) + ((plane_cols * 2) - 1))
    # shuffle to be random
    random.shuffle(window_seats_first)
    # if plane has 3 cols 
    if plane_cols >= 2:
        nextCol = []
        # fill in middle col
        for row in range(plane_rows):
            nextCol.append((row * (plane_cols * 2)+1))
            nextCol.append((row * (plane_cols * 2) + ((plane_cols * 2) - 1)-1))
        random.shuffle(nextCol)
        # add it in so window_Seats_first = [window seats + middle seats]
        window_seats_first.extend(nextCol)
        # get rest of seats
        rest_of_seats = [x for x in front_to_back if x not in window_seats_first]
        random.shuffle(rest_of_seats)
        # add it in so window_Seats_first = [window seats + middle seats + rest of seats]
        window_seats_first.extend(rest_of_seats)
    # plane has 2 cols 
    else:
        # get the rest of the seats
        rest_of_seats = [x for x in front_to_back if x not in window_seats_first]
        # shuffle to be random
        random.shuffle(rest_of_seats)
        # merge as [windows first + rest of seats]
        window_seats_first.extend(rest_of_seats)

    all_orders.append(back_to_front)
    all_orders.append(front_to_back)
    all_orders.append(random_order)
    all_orders.append(window_seats_first)

    return all_orders


def draw_plane(num_rows, num_cols, aisle_positions, seated_passengers, tickets, clock, future_events):
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

    print(f"Time: {clock}")
    print(f"Future events: {future_events}")
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


def get_num_seated(occupied_seats, ticket):
    num_seated = 0
    cols = len(occupied_seats[0])
    # Passenger is seated on the top side
    if ticket['seat'] < cols // 2:
        # Count the number of seated passengers from the aisle to the passenger's seat
        for i in range((cols // 2)-1, ticket['seat'], -1):
            if occupied_seats[ticket['row']][i] != -1:
                num_seated += 1
    # Passenger is seated on the bottom side
    else:
        # Count the number of seated passengers from the aisle to the passenger's seat
        for i in range(cols // 2, ticket['seat']):
            if occupied_seats[ticket['row']][i] != -1:
                num_seated += 1
    return num_seated


def run_simulation(num_rows, num_cols, queue, draw=False):
    num_passengers = len(queue)
    arrival_time = [ 0 for i in range(num_passengers)]
    service_start_time = [ 0 for i in range(num_passengers)]
    service_end_time = [ 0 for i in range(num_passengers)]
    # (num of customers in queue, for time x)
    p_in_aisle_for_this_long = []

    max_seat_num = num_rows * num_cols * 2
    assert max_seat_num >= max(queue), \
        f"Passenger has number {max(queue)} but only {max_seat_num} seats are available"

    # Initialize the plane
    aisle_rows = [-1 for i in range(num_rows)]
    occupied_seats = [[-1 for i in range(num_cols * 2)] for j in range(num_rows)]
    # Passenger i is assigned seat tickets[i]
    tickets = [
        {'row': i, 'seat': j}
        for i in range(num_rows)
        for j in range(num_cols * 2)
    ]
    # Mean service time for loading and accessing seat
    loading_mu = 3
    seating_mu = 2

    future_events = []
    num_seated = 0
    clock = 0
    # Loop until all passengers are seated
    while num_seated < num_passengers:
        # Add passengers to the plane until the aisle is full
        while aisle_rows[0] == -1:
            if len(queue) == 0:
                break
            next_passenger = queue.pop(0)
            arrival_time[next_passenger] = clock
            ticket = tickets[next_passenger]
            cur_row = 0
            while cur_row <= ticket['row']:
                if cur_row == ticket['row']:
                    # Passenger is in the row of their assigned seat
                    # Create service event
                    service_time = random.expovariate(1 / loading_mu)
                    # Get the number of seated passengers in the way of this passenger
                    num_blocking = get_num_seated(occupied_seats, ticket)
                    access_time = random.expovariate(1 / ((num_blocking + 1) * seating_mu))
                    future_events.append(
                        (clock + service_time + access_time, 'baggage', cur_row, next_passenger)
                    )
                    service_start_time[next_passenger] = clock
                    service_end_time[next_passenger] = clock + service_time + access_time
                    aisle_rows[cur_row] = next_passenger
                    break
                # Check if next row is available
                elif aisle_rows[cur_row + 1] == -1:
                    # Move to next row
                    cur_row += 1
                else:
                    # Next row is occupied, so stop at this row
                    aisle_rows[cur_row] = next_passenger
                    break
        if draw:
            draw_plane(num_rows, num_cols, aisle_rows, occupied_seats, tickets, clock, future_events)
        # Plane loading is now in gridlock

        # Get number of passengers in aisle (# pas standing at time x)
        number_of_p_in_aisle = len([x for x in aisle_rows if x != -1])

        # Sort future events and get next event
        future_events.sort()
        next_event = future_events.pop(0)

        # the amount of time the passengers in the aisle have been standing for
        time_elapsed = next_event[0] - clock
        # print("These many Passengers been standing for this much time: ", time_elapsed)

        # add tuple of (Passengers in aisle, elapsed time) to list
        p_in_aisle_for_this_long.append((number_of_p_in_aisle, time_elapsed))

        clock = next_event[0]
        event_type = next_event[1]
        event_row = next_event[2]
        # Process the event
        if event_type == 'baggage':
            # Passenger is done storing baggage
            # Seat the passenger and vacate the aisle row
            passenger = aisle_rows[event_row]
            assert tickets[passenger]['row'] == event_row
            occupied_seats[event_row][tickets[passenger]['seat']] = passenger
            aisle_rows[event_row] = -1
            num_seated += 1
        if draw:
            draw_plane(num_rows, num_cols, aisle_rows, occupied_seats, tickets, clock, future_events)

        # Now update the aisle positions
        for aisle_row in range(len(aisle_rows) - 1, -1, -1):
            # Skip empty aisle rows
            if aisle_rows[aisle_row] == -1:
                continue
            next_passenger = aisle_rows[aisle_row]
            ticket = tickets[next_passenger]
            cur_row = aisle_row
            if cur_row == ticket['row']:
                continue
            while cur_row <= ticket['row']:
                if cur_row == ticket['row']:
                    # Passenger is in the row of their assigned seat
                    # Create service event
                    service_time = random.expovariate(loading_mu)
                    # Get the number of seated passengers in the way of this passenger
                    num_blocking = get_num_seated(occupied_seats, ticket)
                    access_time = random.expovariate(1 / ((num_blocking + 1) * seating_mu))
                    future_events.append(
                        (clock + service_time + access_time, 'baggage', cur_row, next_passenger)
                    )
                    service_start_time[next_passenger] = clock
                    service_end_time[next_passenger] = clock + service_time + access_time
                    aisle_rows[cur_row] = next_passenger
                    break
                # Check if next row is available
                elif aisle_rows[cur_row + 1] == -1:
                    # Move to next row
                    aisle_rows[cur_row] = -1
                    cur_row += 1
                    aisle_rows[cur_row] = next_passenger
                else:
                    # Next row is occupied, so stop at this row
                    aisle_rows[cur_row] = next_passenger
                    break
        if draw:
            draw_plane(num_rows, num_cols, aisle_rows, occupied_seats, tickets, clock, future_events)

    # Calculate simulation final statistics
    total_time = clock
    avg_time_in_aisle = sum([service_end_time[i] - arrival_time[i] for i in range(num_passengers)]) / num_passengers
    avg_P_in_aisle = getAvg_p_in_aisle(p_in_aisle_for_this_long)
    return total_time, avg_time_in_aisle, avg_P_in_aisle

# Sizes are (rows, cols), where cols is number of seats on one side of the aisle
plane_sizes = {
    'small': (12, 2),
    'medium': (25, 2),
    'large': (43, 3)
}
total_times = {
    'small': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'medium': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'large': {'btf': [],'ftb': [],'rdm': [],'win': []}
}
avgs_time_in_aisle = {
    'small': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'medium': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'large': {'btf': [],'ftb': [],'rdm': [],'win': []}
}
avgs_P_in_aisle = {
    'small': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'medium': {'btf': [],'ftb': [],'rdm': [],'win': []},
    'large': {'btf': [],'ftb': [],'rdm': [],'win': []}
}
ordering_labels = ['btf', 'ftb', 'rdm', 'win']

num_sims = 100
total_sims = 0
for i in range(num_sims):
    # Run one simulation for each plane size
    for size in plane_sizes:
        # Get the four different orderings
        plane_rows, plane_cols = plane_sizes[size]
        orderings = create_orderings(plane_rows, plane_cols)
        for j, ordering in enumerate(orderings):
            # Init random seed so that all simulations in this run have the same service times
            random.seed(i)
            total_time, avg_time_in_aisle, avg_P_in_aisle  = run_simulation(plane_rows, plane_cols, ordering.copy(), draw=False)
            total_times[size][ordering_labels[j]].append(total_time)
            avgs_time_in_aisle[size][ordering_labels[j]].append(avg_time_in_aisle)
            avgs_P_in_aisle[size][ordering_labels[j]].append(avg_P_in_aisle)
            total_sims += 1

print("Total simulations run: {}".format(total_sims))

total_time_table = PrettyTable()

column_names = ["Plane Size","Back to Front","Front to Back","Random","Window"]
col_data = [
    ["small", "medium", "large"],
    [round(sum(total_times[size]['btf']) / num_sims, 1) for size in plane_sizes],
    [round(sum(total_times[size]['ftb']) / num_sims, 1) for size in plane_sizes],
    [round(sum(total_times[size]['rdm']) / num_sims, 1) for size in plane_sizes],
    [round(sum(total_times[size]['win']) / num_sims, 1) for size in plane_sizes]
]
length = len(column_names)
for i in range(length):
    total_time_table.add_column(column_names[i],col_data[i])
print("------------------AVERAGE TOTAL TIME------------------")
print(total_time_table)
print()

avg_time_in_aisle_table = PrettyTable()
col_data = [
    ["small", "medium", "large"],
    [round(sum(avgs_time_in_aisle[size]['btf']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_time_in_aisle[size]['ftb']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_time_in_aisle[size]['rdm']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_time_in_aisle[size]['win']) / num_sims, 1) for size in plane_sizes]
]
length = len(column_names)
for i in range(length):
    avg_time_in_aisle_table.add_column(column_names[i],col_data[i])
print("------------------AVERAGE TIME IN AISLE------------------")
print(avg_time_in_aisle_table)
print()

avg_P_in_aisle_table = PrettyTable()
col_data = [
    ["small", "medium", "large"],
    [round(sum(avgs_P_in_aisle[size]['btf']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_P_in_aisle[size]['ftb']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_P_in_aisle[size]['rdm']) / num_sims, 1) for size in plane_sizes],
    [round(sum(avgs_P_in_aisle[size]['win']) / num_sims, 1) for size in plane_sizes]
]
length = len(column_names)
for i in range(length):
    avg_P_in_aisle_table.add_column(column_names[i],col_data[i])
print("------------------AVERAGE P IN AISLE------------------")
print(avg_P_in_aisle_table)