
# Sports Team Management and Visualization

## Project Overview

**Project Name:** Sports Team Management and Visualization

**Description:**
This project consists of several Python scripts designed to manage sports team data and visualize sports courts. The key functionalities include drawing sports courts, managing player and team data, and running demo applications. The project is organized into different modules, each responsible for specific tasks.

## Files in the Project

1. **demo_2.py**
   - A demo application script showcasing the functionalities of the other modules.

2. **draw_courts.py**
   - Contains functions to draw various types of sports courts.

3. **player_app.py**
   - Manages player data including creation, update, and retrieval of player information.

4. **team_app.py**
   - Manages team data including creation, update, and retrieval of team information.

5. **requirements.txt**
   - Lists all the dependencies required to run the project.

## Requirements

To run this project, you'll need Python 3 installed on your machine along with the required dependencies listed in `requirements.txt`.

## Installation and Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/sports-team-management.git
   cd sports-team-management
   ```

2. **Create a Virtual Environment**
   ```sh
   python -m venv venv
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Install the Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

## How to Run

- **Run the Demo Application**
  ```sh
  python demo_2.py
  ```

- **Draw Courts**
  ```sh
  python draw_courts.py
  ```

- **Manage Player Data**
  ```sh
  python player_app.py
  ```

- **Manage Team Data**
  ```sh
  python team_app.py
  ```

## Dependencies

The project dependencies are listed in `requirements.txt`. Make sure to install them using the command provided in the Installation section.

## Detailed File Descriptions

- **demo_2.py:** This script demonstrates the overall functionality of the project, integrating features from drawing courts and managing player and team data.
  
- **draw_courts.py:** This script contains the logic to draw sports courts. It includes functions for rendering different types of sports courts using matplotlib.
  
- **player_app.py:** This script handles player-related operations. It includes functions to create, update, and retrieve player information from a data store.
  
- **team_app.py:** This script handles team-related operations. It includes functions to create, update, and retrieve team information from a data store.

## Important details

- When running the demo application, it will probably take a minute to run the server and show example output below in the terminal, due to the ml running in the background for the first time. The output will look like this:
  
  ```sh
  * Dash is running on http://127.0.0.1:8050/
   ```
When you see this message, open the link in your browser to view the demo application.

- There is a high chance that an error will occur when running the demo application for the first time. This is due to the ml model running in the background while also trying to load the plots at the same time. If this happens, please refresh the window or click the link again to reload the page and it should work fine with no errors.