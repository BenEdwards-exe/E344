
### ------------------------------- GUI Requirements ------------------------------- ###

# 1. Display both the battery voltage and photovoltaic (PV) source voltage (in V).
# 2. Display the battery current (in mA).
# 3. Display the ambient light level:
#       - 0-100 scale
#       - 0: absolute darkness; 100: brightest light available
# 4. Allow the user to control the brightness of the LED array.

### -------------------------------------------------------------------------------- ###



import SerialComms
import PySimpleGUI as sg 
from serial import SerialException


import matplotlib.pyplot as plt

import time


start_time = time.time()

is_show_plot = False

com_port = 'COM9'
baud_rate = 9600
refresh_rate = 500

supply_voltage = 0.0
battery_voltage = 0.0
battery_current = 0.0
ambient_light_level = 0


supply_voltage_data = []
battery_voltage_data = []
battery_current_data = []
ambientLightData = []
plot_time = []


fig, ((ax_ambient, ax_supply), (ax_battery_voltage, ax_battery_current)) = plt.subplots(nrows=2, ncols=2)
fig.tight_layout(pad=2.0)

ax_ambient.set_title("Ambient Light Level")
ax_ambient.set_xlabel("Time (s)")
ax_ambient.set_ylabel("Percentage Light(%)")



def animate_plot():
    global ax, start_time
    plot_time.append(time.time() - start_time)

    if (plot_time[-1] - plot_time[0] > 20):
        plot_time.pop(0)
        ambientLightData.pop(0)
        supply_voltage_data.pop(0)
        battery_voltage_data.pop(0)
        battery_current_data.pop(0)



    ax_ambient.clear()
    ax_supply.clear()
    ax_battery_voltage.clear()
    ax_battery_current.clear()





    
    ax_ambient.set_xlim([plot_time[0]-2, plot_time[0]+25])
    ax_supply.set_xlim([plot_time[0]-2, plot_time[0]+25])
    ax_battery_voltage.set_xlim([plot_time[0]-2, plot_time[0]+25])
    ax_battery_current.set_xlim([plot_time[0]-2, plot_time[0]+25])

    ax_ambient.set_ylim([0, 100])

    ax_ambient.plot(plot_time, ambientLightData)

    plt.ion()
    plt.show()
    



# creates an instance of the SerialComms class
sc = SerialComms.SerialComms(com_port, baud_rate)


# Open the serial connection
def open_connection(sc):
    sc.setCOMPort(com_port)
    sc.setBaudrate(baud_rate)
    sc.open()

# Close the serial connection
def close_connection(sc):
    sc.close()

# Toggle the serial connection to the beetle
def toggle_beetle_connection():
    global com_port
    global baud_rate

    # If the connection is closed, try to open it
    if (sc.isOpen == False):
        # Try to open serial connection. Display error message if fails.
        try:
            open_connection(sc)
        except SerialException:
            print("Unable to connect")
        # Connection is open
        if (sc.isOpen == True):
            print("Connected successfully")
            return "The device is currently connected"

    elif (sc.isOpen == True):
        # Try to close serial connection. Display error if fails.
        try:
            close_connection(sc)
        except SerialException:
            print("Unable to close connection")
        # Connection is closed
        if (sc.isOpen == False):
            print("Disconnected successfully")
            return "The device is currently disconnected"

# Send brightness level (0-100)
def set_load_brightness(brightness):
    if (sc.isOpen == True):
        sc.send("PWM-" + str(brightness))

# Toggle the battery charging
def toggle_charging(is_charging):
    if (sc.isOpen == True):
        # If overcharge is connected: disconnect
        if (is_charging):
            sc.send("OV1")
        # If overcharge is not connected: connect
        elif (not is_charging):
            sc.send("OV0")
        
# Update the measured values
def update_measurements(message_array: list):
    global battery_voltage, supply_voltage, battery_current, ambient_light_level
    # Split the measurement message
    message = message_array[0]
    split_message = message.replace("\'","").split(',')
    # Update values
    battery_voltage = split_message[1]
    supply_voltage = split_message[2]
    battery_current = split_message[3]
    ambient_light_level = split_message[4]

    # Update plot data if plot is shown
    if (is_show_plot):
        ambientLightData.append(int(ambient_light_level))
        supply_voltage_data.append(float(supply_voltage))
        battery_current_data.append(float(battery_current))
        battery_voltage_data.append(float(supply_voltage))
        animate_plot()


    
    
# Receive a message
def receive_message():
    if (sc.isOpen == True):
        message_array = sc.receive()
        if (len(message_array) > 0):
            # print(message_array)
            update_measurements(message_array)


# Serial refresh rate
def update_refresh_rate():
    if (refresh_rate >= 10 and sc.isOpen == True):
        sc.send("RR-" + str(int(refresh_rate)))


# Update the displayed values of the measurements
def update_measurements_display(window: sg.Window):
    window["-BATTERY VOLTAGE-"].update(value=str(battery_voltage) + " V")
    window["-SUPPLY VOLTAGE-"].update(value=str(supply_voltage) + " V")
    window["-BATTERY CURRENT-"].update(value=str(battery_current) + " mA")
    window["-AMBIENT LIGHT LEVEL-"].update(value=str(ambient_light_level) + " %")




def main():

    global com_port
    global baud_rate
    global refresh_rate

    sg.change_look_and_feel('DarkTeal6')
    
    user_input_column = [
        [   sg.Text("User Input\n", font="Any 15") ],
        [   sg.Text("Baud Rate"),
            sg.In(default_text=str(baud_rate), size=(10, 1), enable_events=True, key="-BAUD RATE-") ], 
        [   sg.Text("COM Port"),
            sg.In(default_text=com_port, size=(10, 1), enable_events=True, key="-COM PORT-") ],
        [   sg.Text("Refresh Rate (ms)"),
            sg.In(default_text=str(refresh_rate), size=(10,1), enable_events=True, key="-REFRESH RATE-") ],
        [   sg.Button("Toggle Connection", key="-TOGGLE CONNECTION-") ],
        [   sg.Text("The device is currently disconnected", key="-CONNECTION STATUS-") ],
        [   sg.Text('_'  * 80) ],
        [   sg.Checkbox("Charge Control", enable_events=True, key="-CHARGE CONTROL-") ],
        [   sg.Text('_'  * 80) ],
        [   sg.Checkbox("LED Load", enable_events=True, key="-TOGGLE LED-") ],
        [   sg.Text("LED Brightness:") ],
        [   sg.Slider(range=(0, 100), orientation='h', size=(34, 20), default_value=0, border_width=2, key="-LED BRIGHTNESS-", enable_events=True) ],
        [   sg.Text('_'  * 80) ]
    ]

    data_output_column = [
        [   sg.Text("Measurements\n", font="Any 15") ],
        [   sg.Text("Battery Voltage: "),
            sg.Text(str(battery_voltage) + " V", key="-BATTERY VOLTAGE-") ],
        [   sg.Text("Supply Voltage: "),
            sg.Text(str(supply_voltage) + " V", key="-SUPPLY VOLTAGE-") ],
        [   sg.Text("Battery Current: "),
            sg.Text(str(battery_current) + " mA", key="-BATTERY CURRENT-") ],
        [   sg.Text("Ambient Light Level: "),
            sg.Text(str(ambient_light_level) + " %", key="-AMBIENT LIGHT LEVEL-") ]
    ]



    # Full layout
    layout = [
        [
            sg.Column(layout=user_input_column, size=(350,400)),
            sg.VSeparator(),
            sg.Column(data_output_column, size=(250,400))
        ]
    ]

    window = sg.Window("Battery Charger", layout, keep_on_top=False)

    # Event Loop
    while True:
        event, values = window.read(timeout=5)

        # End program if user closes window
        if event == sg.WIN_CLOSED:
            break

        # Baud rate input
        if (event == "-BAUD RATE-"):
            baud_rate = int(values["-BAUD RATE-"])

        # Com port input
        if (event == "-COM PORT-"):
            com_port = values["-COM PORT-"]

        # Refresh rate input
        if (event == "-REFRESH RATE-"):
            val = values["-REFRESH RATE-"]
            if (val != ""):
                refresh_rate = int(val)
                update_refresh_rate()

        # Toggle the connection
        if (event == "-TOGGLE CONNECTION-"):
            message = toggle_beetle_connection()
            window["-CONNECTION STATUS-"].update(message)

        # Charge control toggled
        if (event == "-CHARGE CONTROL-"):
            toggle_charging(values["-CHARGE CONTROL-"])            

        # LED load toggled
        if (event == "-TOGGLE LED-"):
            # set slider to right position
            if (values["-TOGGLE LED-"] == True):
                window["-LED BRIGHTNESS-"].update(value=50)
                brightness = 50
            elif (values["-TOGGLE LED-"] == False):
                window["-LED BRIGHTNESS-"].update(value=0)
                brightness = 0
            
            set_load_brightness(brightness)
            
        # Brightness slider changes
        if (event == "-LED BRIGHTNESS-"):
            brightness = values["-LED BRIGHTNESS-"]
            set_load_brightness(brightness)
        
        receive_message()

        update_measurements_display(window)





        
        

    window.close()


if __name__ == '__main__':
    main()







