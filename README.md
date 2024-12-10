## Description

This project is to build a UI that will pull data from our agent's API.
Dashboard that updates automatically to display data evolving over time. Thus, the final user has an good idea of the health of her servers in a blink of an eye.

## Project hierarchy

- [components](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/components) : contains modular code responsible for generating the visual elements of the dashboard application. Each module focuses on a specific system metric, handling data fetching and visualization. .
- [layouts](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/layouts) : Different pages frontend code.
- [assets](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/assets) : General files to use for display (styling, images....)
- [services](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/services) : Code needed to communicate with the agent api and handle responses.
- [app.py](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/blob/main/src/app.py) : Main file that runs the project contains callbacks,and main frontend code logic.


## How to use

first run the agent, install requirements.txt using pip install -r requirements.txt then run the app.py and it will work. 