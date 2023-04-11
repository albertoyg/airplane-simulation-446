import random
import statistics as stat


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
    # get the rest of the seats
    rest_of_seats = [x for x in front_to_back if x not in window_seats_first]
    # shuffle both to be random
    random.shuffle(window_seats_first)
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


def run_simulation(num_rows, num_cols, queue, enter_time, start_loading_time, service_time_lst, seat_time, draw=False):
    num_passengers = len(queue)

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

    # TODO Incorporate time to access seat into service time, which is dependent on
    # the number of passengers already seated in this row
    loading_mu = 1 / 3

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
            ticket = tickets[next_passenger]
            enter_time[next_passenger] = clock
            cur_row = 0
            while cur_row <= ticket['row']:
                if cur_row == ticket['row']:
                    # Passenger is in the row of their assigned seat
                    # Create service event
                    service_time = random.expovariate(loading_mu)
                    service_time_lst[next_passenger] = service_time
                    start_loading_time[next_passenger] = clock
                    future_events.append((clock + service_time, 'baggage', cur_row, next_passenger))
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

        # Print number of passengers in aisle (# pas standing at time x)
        number_of_p_in_asile = len([x for x in aisle_rows if x != -1])
        # print("number of Passengers standing in plane: ", number_of_p_in_asile)

        # Sort future events and get next event
        future_events.sort()
        next_event = future_events.pop(0)

        # the amount of time the passengers in the aisle have been standing for
        time_elapsed = next_event[0] - clock;
        # print("These many Passengers been standing for this much time: ", time_elapsed)

        # add tuple of (Passengers in aisle, elapsed time) to list
        p_in_aisle_for_this_long.append((number_of_p_in_asile, time_elapsed))

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
            seat_time[passenger] = clock
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
                    start_loading_time[next_passenger] = clock
                    service_time_lst[next_passenger] = service_time
                    future_events.append((clock + service_time, 'baggage', cur_row, next_passenger))
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

    return clock


plane_rows = 10
plane_cols = 2

# all_orders will be a list of seating orders: front to back, back to fron, randomized order, window seats first then the rest
all_orders = create_orderings(plane_rows, plane_cols)

avgPinQ = []
enter_time = [-1 for i in range(plane_rows * plane_cols * 2)]
seat_time = [-1 for i in range(plane_rows * plane_cols * 2)]
customer_num = plane_rows * plane_cols * 2

avg_total_time = []
avg_waiting_time_inQ = []

times = []
best_time = 0
best_seed = 0
best_ordering = []
worst_time = 0
worst_seed = 0
worst_ordering = []
for i in range(10):
    # (num of customers in queue, for time x)
    p_in_aisle_for_this_long = []

    random.seed(i)
    ordering = [i for i in range(plane_rows * plane_cols * 2)]

    random.shuffle(ordering)
    random.seed(10)

    enter_time = [-1 for i in range(customer_num)]
    start_loading_time = [-1 for i in range(customer_num)]
    service_time_lst = [-1 for i in range(customer_num)]
    seat_time = [-1 for i in range(customer_num)]
    waiting_time_inQ = [-1 for i in range(customer_num)]

    time = run_simulation(plane_rows, plane_cols, ordering.copy(), enter_time, start_loading_time, service_time_lst,
                          seat_time, draw=False)

    for index in range(0, customer_num):
        waiting_time_inQ[index] = seat_time[index] - enter_time[index]
    avg_waiting_time_inQ.append(stat.mean(waiting_time_inQ))
    avg_total_time.append(max(seat_time))
    times.append(time)

    # do average of pass in aisle
    avgPinQ.append(getAvg_p_in_aisle(p_in_aisle_for_this_long))

    if time > worst_time:
        worst_time = time
        worst_seed = i
        worst_ordering = ordering
    elif time < best_time or best_time == 0:
        best_time = time
        best_seed = i
        best_ordering = ordering

print(f"Average time steps: {sum(times) / len(times)}")
print(f"Best time steps: {best_time}")
print(f"Best ordering: {best_ordering}")
print(f"Best seed: {best_seed}")
print(f"Worst time steps: {worst_time}")
print(f"Worst ordering: {worst_ordering}")
print(f"Worst seed: {worst_seed}")
print(f"Average Number of Passengers in aisle at any moment: {stat.mean(avgPinQ)}")
print("Average Waiting Time in the Queue: ", stat.mean(avg_waiting_time_inQ))
print("Average Total Simulation Time: ", stat.mean(avg_total_time))
