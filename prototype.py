import random

num_rows = 10

aisle_rows = [-1 for i in range(num_rows)]
seat_rows = [-1 for i in range(num_rows)]
assigned_seats = [i for i in range(num_rows)]
random.shuffle(assigned_seats)
queue = assigned_seats.copy()
random.shuffle(queue)

num_seated = 0

def draw_plane(aisle_positions, seat_positions):
    for i in range(num_rows):
        print(f"{i}  |", end="")
    print()
    for i in range(num_rows):
        print(f"{str(seat_positions[i]).ljust(3)}|", end="")
    print()
    for i in range(num_rows):
        print(f"{str(aisle_positions[i]).ljust(3)}|", end="")
    print()
    print("_" * (num_rows * 4 + 1))

time_steps = 0
while num_seated < num_rows:
    for aisle_row in range(num_rows-1, -1, -1):
        if aisle_rows[aisle_row] == -1:
            continue
        assigned_seat = aisle_rows[aisle_row]
        # Check if passenger is in the row of their assigned seat
        if assigned_seat == aisle_row:
            seat_rows[aisle_row] = assigned_seat
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
    draw_plane(aisle_rows, seat_rows)
    time_steps += 1

print(f"Time steps: {time_steps}")
