# Project Report

- [View the Project Report (PDF)](./projectReport.pdf)

## Execution Instructions

1. To run the simulator:
    ```bash
    python3 simulator.py
    ```

2. If you'd like to visualize the plane:
   - Set `draw` to `True` on line 312.
   - **IMPORTANT**: Ensure `num_sims` is set to `1` when drawing the plane.

## Configuration Notes

- You can adjust the number of simulations at line 301.
- The aircraft's size can be modified by altering values in the `plane_size` dictionary. This dictionary uses the format `(rows, cols)`, where `cols` denotes the number of columns on one side of the aisle.
