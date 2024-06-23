
# The NBA Three-Point Revolution: A Data-Driven Analysis

## Project Overview

**Project Name:** The NBA Three-Point Revolution: A Data-Driven Analysis

**Description:**
We developed an interactive dashboard that allows the user to explore, analyze and understand the NBA's three-point revolution. Our tool enables in-depth data analytics and uses machine learning explanation techniques to understand regression models.

## Python Files in the Project

1. **demo_2.py**
   - A dashboard demo application showcasing the functionalities and all the plots for analysis.

2. **draw_courts.py**
   - Contains functions to draw the court visualizations with the team shots.

3. **player_app.py**
   - Manages player data including creation, update, and retrieval of player information.

4. **team_app.py**
   - Manages team data including creation, update, and retrieval of team information.


## Requirements

To run this project, you'll need Python 3 installed on your machine along with the required dependencies listed in `requirements.txt`.

## Installation and Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/Michael-Aggelos/2AMV10-Visual-Analytics-Project-Group-8.git
   ```

2. **Install the Dependencies**
   ```sh
   pip install -r requirements.txt
   ```
   The project dependencies are listed in `requirements.txt`. Make sure to install them using the command provided in the Installation section.
   
3. **Unzip the Data File**
   ```sh
   unzip NBA_2004_2023_Shots_new.zip
   ```
   After unzipping the file, you should see a folder named `NBA_2004_2023_Shots_new` containing the dataset. Move the csv file from this folder to the path with all the other python and csv files.

## How to Run

- **Run the Demo Application**
  ```sh
  python demo_2.py
  ```


## Important details

- When running the demo application, it will probably take a minute to run the server and show example output below in the terminal, due to the ml running in the background for the first time. The output will look like this:
  
  ```sh
  * Dash is running on http://127.0.0.1:8050/
   ```
When you see this message, open the link in your browser to view the demo application.

- There is a high chance that an error will occur when running the demo application for the first time. This is due to the ml model running in the background while also trying to load the plots at the same time. If this happens, please refresh the window or click the link again to reload the page and it should work fine with no errors.