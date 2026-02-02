A Python-based simulation of ships traveling between planets using Dijkstra's algorithm for pathfinding. The simulation logs data to a SQLite database and generates an animated GIF of the ships' movements.

## Features

- **Pathfinding**: Uses Dijkstra's algorithm to find the fastest path based on ship speed and distance.
- **Visualization**: Generates a `simulation.gif` showing the ships moving between planets.
- **Data Logging**: Logs events (route entry, exit, distance traveled) to a SQLite database (`cul_data.db`).
- **Customizable**: Allows user input for planets, routes, and ships, or a default configuration.

## Prerequisites

- Python 3.x

## Installation

1.  Navigate to the project directory.
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the simulation from the project root directory:

```bash
python main.py
```

Follow the on-screen prompts to configure the simulation or use the default setup.

## Output

- **Animation**: A file named `simulation.gif` will be created in the current directory.
- **Database**: A SQLite file named `cul_data.db` will be created/updated with simulation logs.


