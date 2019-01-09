# service.SerialController

Kodi Plugin for controlling media playback over serial and screen dimming on Raspberry pi running LibreELEC. Intended to serve as interface with something like an Arduino with buttons and controls, where the Arduino interprets presses and durations, sending through interpreted commands, see github.com/xoliul/PowerMan for example.

Includes slightly modified pyserial library (required to work on LibreELEC) by Chris Liechti: github.com/pyserial/pyserial

as well as wiringpi compiled for Cpython2.7 from PyPi: https://pypi.org/project/wiringpi/, github.com/WiringPi/WiringPi


Has 3 main functions:

- Listens to media commands on Serial, formatted as text. Commands do things like Play, pause, volume adjustment
- Waits for screensaver to activate and then starts 2 countdowns until it performs a hardware PWM signal on a Pin (defaults to Pin 12, will not work on other pins). For example, on screensaver activation it fades to 25% dim over PWM, then after 2 minutes it toggles PWM off. This is intened for use with Waveshare LCD screens without power management: they can be easily modded by following a manufacturer guide.
- After screensaver is off, it starts an even longer countdown dependant on a specific command through serial that specifies "Accesory Power" is off; eg, the key in a car is turned off, signalling the stereo unit to turn off. You can set the delay yourself. Conditions are: screensaver active, timeout met, no media playing and "Accessory Power off"

More info:

Photos: https://photos.google.com/share/AF1QipNOalSMYOtYQD1bHhmhJNEraALUsxx1hYXyfX8KLlF5mXhvgUfo9PTx3TV2ps-Vuw?key=SXJBNlMyUThsRFEtbjJHa1V4aWxrYUlvcS15NFlR

Partlist: https://docs.google.com/spreadsheets/d/13uf0IYDIL0jGhBBMnfD-xuNvdJcvdOVAqd9ZSzGYDHY/edit?usp=sharing

3D Model Files: https://www.thingiverse.com/thing:3299786
