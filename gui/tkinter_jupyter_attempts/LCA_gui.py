import tkinter as tk
import tkinter.ttk as tkk

from configs import fixed_dist_maker, range_dist_maker, triangular_dist_maker, gaussian_dist_maker
from functions.general.utility import update_user_inputs_toml


root = tk.Tk()
root.geometry("300x500")

units = "kWh"

distribution_variable = tk.StringVar()
distribution_options = [("default", "None"),
                        ("fixed", "fixed_dist_maker"),
                        ("range", "range_dist_maker"),
                        ("triangular", "triangular_dist_maker"),
                        ("gaussian", "gaussian_dist_maker")]

def save_distribution_selection(variable_name):

    # update_user_inputs_toml(variable_name=variable_name, variable_value=1, absolute_raw_filepath=r"C:\Users\2270577A\PycharmProjects"
    #                                                   r"\PhD_LCA_TEA\configs\user_inputs.toml")
    return variable_name



def display_distribution_inputs():

    def close_window():
        new_window.destroy()
        proceed_button.config(text="Completed", bg="GREEN")

    new_window = tk.Tk()  # open new window
    general_label = tk.Label(new_window, text="Enter the required parameters:", padx=20)
    close_button = tk.Button(new_window, text="Save entries and proceed", command=close_window)

    options_frame = tk.Frame(master=new_window)
    units_label = tk.Label(options_frame, text=units, padx=20)

    if distribution_variable.get() == "None":
        pass
    # Todo: Add other alternatives

    elif distribution_variable.get() == "fixed_dist_maker":
        pass

    elif distribution_variable.get() == "range_dist_maker":
        pass

    elif distribution_variable.get() == "triangular_dist_maker":
        triangular_label_lower = tk.Label(options_frame, text="Lower:")
        triangular_label_mode = tk.Label(options_frame, text="Mode:")
        triangular_label_upper = tk.Label(options_frame, text="Upper:")

        triangular_entry_lower = tk.Entry(options_frame, width=10)
        triangular_entry_mode = tk.Entry(options_frame, width=10)
        triangular_entry_upper = tk.Entry(options_frame, width=10)

        triangular_label_lower.grid(row=0, column=0)
        triangular_label_mode.grid(row=1, column=0)
        triangular_label_upper.grid(row=2, column=0)
        triangular_entry_lower.grid(row=0, column=1)
        triangular_entry_mode.grid(row=1, column=1)
        triangular_entry_upper.grid(row=2, column=1)
        units_label.grid(row=0, column=2)
        units_label.grid(row=1, column=2)
        units_label.grid(row=2, column=2)


    elif distribution_variable.get() == "gaussian_dist_maker":
        pass

    general_label.pack()
    options_frame.pack()
    close_button.pack()



tk.Label(root, text="Select a distribution option:", padx=20).pack(anchor=tk.W)

for distribution_option, val in distribution_options:
    distribution_radio_buttons = tkk.Radiobutton(master=root,
                                                 text=distribution_option,
                                                 variable=distribution_variable,
                                                 command=save_distribution_selection(val),
                                                 value=val)
    distribution_radio_buttons.pack(anchor=tk.W)

proceed_button = tk.Button(root, text="Proceed", command=display_distribution_inputs)

proceed_button.pack()

root.mainloop()


# Todo: make into function - create widget with right units and right labels - then save under correct name



