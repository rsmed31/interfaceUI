## Description

This project is to build a UI that will pull data from our agent's API.
Dashboard that updates automatically to display data evolving over time. Thus, the final user has an good idea of the health of her servers in a blink of an eye.

## Project hierarchy

- [components](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/components) : Used plots different fetched metrics.
- [layouts](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/layouts) : Different sections of the page.
- [assets](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/assets) : General files to use for display (styling, images....)
- [services](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/tree/main/src/services) : Code needed to communicate with the agent api and handle responses.
- [app.py](https://devops.telecomste.fr/printerfaceadmin/2024-25/group1/printerfaceui/-/blob/main/src/app.py) : Main file that runs the project.


## How to use

For now the ui only runs with local agent. first run the agent, then run the app.py and it will work. 