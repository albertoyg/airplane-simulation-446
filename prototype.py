import random

def run_simulation():
    num_rows = 10
    num_seats = 1   # Number of seats on each side of the aisle

    aisle_rows = [-1 for i in range(num_rows)]
    seat_rows = [-1 for i in range(num_rows*num_seats*2)]
    assigned_seats = [i for i in range(num_rows*num_seats*2)]
    random.shuffle(assigned_seats)
    queue = assigned_seats.copy()

    storing_baggage = [0 for i in range(num_rows)]
    num_seated = 0

    def draw_plane(aisle_positions, seat_positions):
        print("_" * (num_rows * 7 + 1))
        print("Row number:        ", end="")
        for i in range(0, num_rows*num_seats*2, 2):
            print(f"{str(i).ljust(4)}|", end="")
        print()
        print("Seated passengers: ", end="")
        for i in range(0, num_rows*num_seats*2, 2):
            print(f"{str(seat_positions[i]).ljust(4)}|", end="")
        print()
        print("Aisle passengers:  ", end="")
        for i in range(num_rows):
            print(f"{str(aisle_positions[i]).ljust(4)}|", end="")
        print()
        print("Seated passengers: ", end="")
        for i in range(1, num_rows*num_seats*2, 2):
            print(f"{str(seat_positions[i]).ljust(4)}|", end="")
        print()
        print("Row number:        ", end="")
        for i in range(1, num_rows*num_seats*2, 2):
            print(f"{str(i).ljust(4)}|", end="")
        print()
        print("_" * (num_rows * 7 + 1))

    time_steps = 0
    # Loop until all passengers are seated
    while num_seated < num_rows*num_seats*2:
        # Loop through each row from the back to the front, moving passengers forward if possible
        for aisle_row in range(num_rows-1, -1, -1):
            if aisle_rows[aisle_row] == -1:
                continue
            assigned_seat = aisle_rows[aisle_row]
            # Check if passenger is in the row of their assigned seat
            if (aisle_row*2)+1 - assigned_seat in [0, 1]:
                # Start storing baggage timer
                if storing_baggage[aisle_row] == 0:
                    storing_baggage[aisle_row] = 3
                else:
                    storing_baggage[aisle_row] -= 1
                    # If timer is up then seat the passenger
                    if storing_baggage[aisle_row] == 0:
                        seat_rows[assigned_seat] = assigned_seat
                        aisle_rows[aisle_row] = -1
                        num_seated += 1
            else:
                # Check if next aisle row is empty
                if aisle_rows[aisle_row + 1] == -1:
                    aisle_rows[aisle_row + 1] = assigned_seat
                    aisle_rows[aisle_row] = -1

        if len(queue) > 0 and aisle_rows[0] == -1:
            assigned_seat = queue.pop()
            aisle_rows[0] = assigned_seat
        #draw_plane(aisle_rows, seat_rows)
        time_steps += 1
    return time_steps, assigned_seats

times = []
best_time = 0
best_assignment = []
worst_time = 0
worst_assignment = []
for i in range(10000):
    time, assignment = run_simulation()
    times.append(time)
    if time > worst_time:
        worst_time = time
        worst_assignment = assignment
    elif time < best_time or best_time == 0:
        best_time = time
        best_assignment = assignment
print(f"Average time steps: {sum(times) / len(times)}")
print(f"Best time steps: {best_time}")
print(f"Best assignment: {best_assignment}")
print(f"Worst time steps: {worst_time}")
print(f"Worst assignment: {worst_assignment}")
