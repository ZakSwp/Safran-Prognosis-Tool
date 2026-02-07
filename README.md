<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/12aa23b2-9dd7-4f02-b4d2-607eb27211b3" />


This project is part of a smart sensor project for helicopter gearbox health prognosis. The objective was to develop a minimal cost/latency solution to provide prognosis results characterizing the health of the gears composing the main gearbox in helicopters.


The project includes is separated into two sections: 
- Signal acquisition and processing chip: STM32 MCU loaded with TinyAI inference model and equipped with a minimum of 1 accelerometer and 1 microphone to mount on the target gear(s)
- Signal visualization and analysis tool (this repository) allowing maintenance workers to visualize sensor data, inference results and perform signal analysis and basic cyclo-stationnary signal processing operations.

Currently this tool provides:
- Signal acquisition and visualization windows
- Gear configuration window
- Automated DFT execution on the read signal (window length/sample size non-configurable at this stage) with Hann windowing for spectral leakage reduction.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/c77db704-617a-497c-a04b-944bfe403a89" />
