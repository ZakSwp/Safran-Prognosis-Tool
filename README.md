![[Pasted image 20260207093422.png]]

This project is part of a smart sensor project for helicopter gearbox health prognosis. The objective was to develop a minimal cost/latency solution to provide prognosis results characterizing the health of the gears composing the main gearbox in helicopters.


The project includes is separated into two sections: 
- Signal acquisition and processing chip: STM32 MCU loaded with TinyAI inference model and equipped with a minimum of 1 accelerometer and 1 microphone to mount on the target gear(s)
- Signal visualization and analysis tool (this repository) allowing maintenance workers to visualize sensor data, inference results and perform signal analysis and basic cyclo-stationnary signal processing operations.

![[Pasted image 20260207092547.png]]
